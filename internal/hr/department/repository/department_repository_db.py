from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from internal.hr.department.repository.department_repository import DepartmentRepository
from internal.hr.department.model.department_dto import DepartmentOverviewItem


class DatabaseDepartmentRepository(DepartmentRepository):
    """Database implementation of department statistics repository"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_department_overview(self) -> List[DepartmentOverviewItem]:
        """Get department overview statistics from database using raw SQL"""
        
        # Enhanced query to get department statistics with better handling of edge cases
        department_stats_query = text("""
            SELECT 
                d.name as department,
                COUNT(DISTINCT u.id) as total_users,
                COUNT(DISTINCT CASE WHEN u.status = true THEN u.id END) as active_users,
                COALESCE(
                    ROUND(AVG(CASE WHEN c.progress IS NOT NULL THEN c.progress END)), 
                    0
                ) as avg_progress
            FROM departments d
            LEFT JOIN users u ON d.id = u.department_id
            LEFT JOIN courses c ON u.id = c.user_id AND c.progress IS NOT NULL
            GROUP BY d.id, d.name
            HAVING COUNT(DISTINCT u.id) > 0  -- Only include departments with users
            ORDER BY d.name
        """)
        
        result = self.db.execute(department_stats_query).fetchall()
        
        departments = []
        for row in result:
            departments.append(DepartmentOverviewItem(
                department=row.department,
                total_users=row.total_users or 0,
                active_users=row.active_users or 0,
                avg_progress=int(row.avg_progress) if row.avg_progress else 0
            ))
        
        return departments
