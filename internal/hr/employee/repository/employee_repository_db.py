from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from uuid import UUID
from internal.hr.employee.repository.employee_repository import EmployeeRepository
from internal.hr.employee.model.employee_dto import EmployeeDetailResponse


class DatabaseEmployeeRepository(EmployeeRepository):
    """Database implementation of employee repository"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_employee_detail(self, user_id: UUID) -> Optional[EmployeeDetailResponse]:
        """Get detailed employee information by user ID"""
        
        # Raw SQL query to get employee details with all related information
        query = text("""
            SELECT 
                u.id,
                u.name,
                u.email,
                u.image,
                u.status,
                u.country,
                u.cv,
                u.created_at,
                u.department_id,
                d.name as department_name,
                u.position_id,
                p.name as position_name,
                u.manager_id,
                m.name as manager_name,
                u.location_id,
                l.city as location_city,
                l.country as location_country,
                COALESCE(course_stats.total_courses, 0) as total_courses,
                COALESCE(course_stats.completed_courses, 0) as completed_courses,
                COALESCE(course_stats.in_progress_courses, 0) as in_progress_courses,
                COALESCE(course_stats.completion_rate, 0.0) as completion_rate,
                COALESCE(course_stats.total_learning_hours, 0.0) as total_learning_hours,
                COALESCE(skills_stats.skills, '{}') as skills
            FROM users u
            LEFT JOIN departments d ON u.department_id = d.id
            LEFT JOIN positions p ON u.position_id = p.id
            LEFT JOIN users m ON u.manager_id = m.id
            LEFT JOIN locations l ON u.location_id = l.id
            LEFT JOIN (
                SELECT 
                    user_id,
                    COUNT(*) as total_courses,
                    COUNT(CASE WHEN is_completed = true THEN 1 END) as completed_courses,
                    COUNT(CASE WHEN is_completed = false THEN 1 END) as in_progress_courses,
                    CASE 
                        WHEN COUNT(*) > 0 THEN 
                            CAST(ROUND((COUNT(CASE WHEN is_completed = true THEN 1 END)::numeric / COUNT(*)) * 100, 2) AS numeric)
                        ELSE 0.0 
                    END as completion_rate,
                    COALESCE(SUM(estimated_duration), 0.0) as total_learning_hours
                FROM courses 
                WHERE user_id = :user_id
                GROUP BY user_id
            ) course_stats ON u.id = course_stats.user_id
            LEFT JOIN (
                SELECT 
                    user_id,
                    COALESCE(
                        ARRAY_AGG(DISTINCT skill_element),
                        '{}'
                    ) as skills
                FROM courses, unnest(skill) as skill_element
                WHERE user_id = :user_id AND is_completed = true AND skill IS NOT NULL
                GROUP BY user_id
            ) skills_stats ON u.id = skills_stats.user_id
            WHERE u.id = :user_id
        """)
        
        result = self.db.execute(query, {"user_id": str(user_id)}).fetchone()
        
        if not result:
            return None
        
        # Handle skills array - PostgreSQL returns it as a list already
        skills = result.skills if result.skills else []
        if isinstance(skills, str):
            # If it's still a string (fallback), parse PostgreSQL array format
            if skills.startswith('{') and skills.endswith('}'):
                skills = skills[1:-1].split(',') if skills != '{}' else []
                skills = [skill.strip() for skill in skills if skill.strip()]
            else:
                skills = []
        
        # Helper function to safely convert to UUID
        def safe_uuid(value):
            if value is None:
                return None
            if isinstance(value, UUID):
                return value
            try:
                return UUID(str(value))
            except (ValueError, TypeError):
                return None
        
        return EmployeeDetailResponse(
            id=safe_uuid(result.id),
            name=result.name,
            email=result.email,
            image=result.image,
            status=result.status,
            country=result.country,
            cv=result.cv,
            created_at=result.created_at,
            
            # Department information
            department_id=safe_uuid(result.department_id),
            department_name=result.department_name,
            
            # Position information
            position_id=safe_uuid(result.position_id),
            position_name=result.position_name,
            
            # Manager information
            manager_id=safe_uuid(result.manager_id),
            manager_name=result.manager_name,
            
            # Location information
            location_id=safe_uuid(result.location_id),
            location_city=result.location_city,
            location_country=result.location_country,
            
            # Learning statistics
            total_courses=result.total_courses,
            completed_courses=result.completed_courses,
            in_progress_courses=result.in_progress_courses,
            completion_rate=float(result.completion_rate),
            total_learning_hours=float(result.total_learning_hours),
            skills=skills
        )
