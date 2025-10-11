from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any
from internal.hr.company.repository.company_repository import CompanyRepository
from internal.hr.company.model.company_dto import CompanyStatisticResponse


class DatabaseCompanyRepository(CompanyRepository):
    """Database implementation of company statistics repository"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_company_statistics(self) -> CompanyStatisticResponse:
        """Get company statistics from database using raw SQL"""
        
        # Total employees (active users)
        total_employees_query = text("""
            SELECT COUNT(*) as count 
            FROM users 
            WHERE status = true
        """)
        total_employees_result = self.db.execute(total_employees_query).fetchone()
        total_employees = total_employees_result.count if total_employees_result else 0
        
        # Active learners (users with at least one course)
        active_learners_query = text("""
            SELECT COUNT(DISTINCT u.id) as count 
            FROM users u 
            INNER JOIN courses c ON u.id = c.user_id 
            WHERE u.status = true
        """)
        active_learners_result = self.db.execute(active_learners_query).fetchone()
        active_learners = active_learners_result.count if active_learners_result else 0
        
        # Average progress across all courses (already in percentage)
        avg_progress_query = text("""
            SELECT ROUND(AVG(progress)) as avg_progress 
            FROM courses
        """)
        avg_progress_result = self.db.execute(avg_progress_query).fetchone()
        avg_progress = int(avg_progress_result.avg_progress) if avg_progress_result and avg_progress_result.avg_progress else 0
        
        # Courses completed
        courses_completed_query = text("""
            SELECT COUNT(*) as count 
            FROM courses 
            WHERE is_completed = true
        """)
        courses_completed_result = self.db.execute(courses_completed_query).fetchone()
        courses_completed = courses_completed_result.count if courses_completed_result else 0
        
        # Top performer department (highest average progress)
        top_performer_query = text("""
            SELECT d.name 
            FROM departments d 
            INNER JOIN users u ON d.id = u.department_id 
            INNER JOIN courses c ON u.id = c.user_id 
            GROUP BY d.id, d.name 
            ORDER BY AVG(c.progress) DESC 
            LIMIT 1
        """)
        top_performer_result = self.db.execute(top_performer_query).fetchone()
        top_performer = top_performer_result.name if top_performer_result else "N/A"
        
        # Most active department (most courses)
        most_active_query = text("""
            SELECT d.name 
            FROM departments d 
            INNER JOIN users u ON d.id = u.department_id 
            INNER JOIN courses c ON u.id = c.user_id 
            GROUP BY d.id, d.name 
            ORDER BY COUNT(c.id) DESC 
            LIMIT 1
        """)
        most_active_result = self.db.execute(most_active_query).fetchone()
        most_active = most_active_result.name if most_active_result else "N/A"
        
        # Largest team (most employees)
        largest_team_query = text("""
            SELECT d.name 
            FROM departments d 
            INNER JOIN users u ON d.id = u.department_id 
            WHERE u.status = true 
            GROUP BY d.id, d.name 
            ORDER BY COUNT(u.id) DESC 
            LIMIT 1
        """)
        largest_team_result = self.db.execute(largest_team_query).fetchone()
        largest_team = largest_team_result.name if largest_team_result else "N/A"
        
        return CompanyStatisticResponse(
            total_employees=total_employees,
            active_learners=active_learners,
            avg_progress=avg_progress,
            courses_completed=courses_completed,
            top_performer=top_performer,
            most_active=most_active,
            largest_team=largest_team
        )
