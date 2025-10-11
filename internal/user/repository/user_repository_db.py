from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from sqlalchemy import text
from sqlalchemy.orm import Session
from internal.user.model.user_entity import User
from internal.user.repository.user_repository import UserRepository


class DatabaseUserRepository(UserRepository):
    """Database implementation of User repository using raw SQL"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID using raw SQL"""
        query = text("""
            SELECT id, department_id, position_id, manager_id, location_id, 
                   name, image, email, password, country, created_at
            FROM users 
            WHERE id = :user_id
        """)
        
        result = self.db.execute(query, {"user_id": user_id}).fetchone()
        
        if not result:
            return None
        
        return User(
            id=result.id,
            department_id=result.department_id,
            position_id=result.position_id,
            manager_id=result.manager_id,
            location_id=result.location_id,
            name=result.name,
            image=result.image,
            email=result.email,
            password=result.password,
            country=result.country,
            created_at=result.created_at
        )
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email using raw SQL"""
        query = text("""
            SELECT id, department_id, position_id, manager_id, location_id, 
                   name, image, email, password, country, created_at
            FROM users 
            WHERE email = :email
        """)
        
        result = self.db.execute(query, {"email": email}).fetchone()
        
        if not result:
            return None
        
        return User(
            id=result.id,
            department_id=result.department_id,
            position_id=result.position_id,
            manager_id=result.manager_id,
            location_id=result.location_id,
            name=result.name,
            image=result.image,
            email=result.email,
            password=result.password,
            country=result.country,
            created_at=result.created_at
        )
    
    async def create_user(self, user: User) -> User:
        """Create a new user using raw SQL"""
        user.id = uuid4()
        user.hash_password()
        
        query = text("""
            INSERT INTO users (id, department_id, position_id, manager_id, location_id, 
                             name, image, email, password, country, created_at)
            VALUES (:id, :department_id, :position_id, :manager_id, :location_id, 
                    :name, :image, :email, :password, :country, :created_at)
        """)
        
        self.db.execute(query, {
            "id": user.id,
            "department_id": user.department_id,
            "position_id": user.position_id,
            "manager_id": user.manager_id,
            "location_id": user.location_id,
            "name": user.name,
            "image": user.image,
            "email": user.email,
            "password": user.password,
            "country": user.country,
            "created_at": user.created_at
        })
        
        self.db.commit()
        return user
    
    async def get_user_summary(self, user_id: UUID) -> Dict[str, Any]:
        """Get user dashboard summary statistics using raw SQL"""
        
        # Get course statistics
        course_stats_query = text("""
            SELECT 
                COUNT(*) as total_courses,
                COUNT(CASE WHEN is_completed = true THEN 1 END) as completed_courses,
                AVG(CASE WHEN is_completed = true THEN progress ELSE NULL END) as avg_completion_rate,
                SUM(CASE WHEN is_completed = true THEN estimated_duration ELSE 0 END) as total_learning_hours
            FROM courses 
            WHERE user_id = :user_id
        """)
        
        course_stats = self.db.execute(course_stats_query, {"user_id": user_id}).fetchone()
        
        # Get quiz statistics
        quiz_stats_query = text("""
            SELECT 
                COUNT(CASE WHEN q.is_completed = true THEN 1 END) as total_quiz_completed
            FROM quizzes q
            JOIN modules m ON q.module_id = m.id
            JOIN courses c ON m.course_id = c.id
            WHERE c.user_id = :user_id
        """)
        
        quiz_stats = self.db.execute(quiz_stats_query, {"user_id": user_id}).fetchone()
        
        # Get skills acquired (from completed courses)
        skills_query = text("""
            SELECT DISTINCT unnest(skill) as skill_name
            FROM courses 
            WHERE user_id = :user_id AND is_completed = true AND skill IS NOT NULL
        """)
        
        skills_result = self.db.execute(skills_query, {"user_id": user_id}).fetchall()
        skills_acquired = [row.skill_name for row in skills_result if row.skill_name]
        
        # Calculate learning path progress (average progress of all courses)
        progress_query = text("""
            SELECT AVG(progress) as learning_path_progress
            FROM courses 
            WHERE user_id = :user_id
        """)
        
        progress_result = self.db.execute(progress_query, {"user_id": user_id}).fetchone()
        
        return {
            "learning_time_hours": float(course_stats.total_learning_hours or 0),
            "courses_completed": int(course_stats.completed_courses or 0),
            "total_quiz_completed": int(quiz_stats.total_quiz_completed or 0),
            "completion_rate": float(course_stats.avg_completion_rate or 0),
            "skills_acquired": skills_acquired,
            "learning_path_progress": float(progress_result.learning_path_progress or 0),
            "total_courses": int(course_stats.total_courses or 0)
        }