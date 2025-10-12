from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from internal.hr.department.repository.department_repository import DepartmentRepository
from internal.hr.department.model.department_dto import DepartmentOverviewItem, DepartmentDetailResponse, DepartmentListResponse, DepartmentListItem


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
    
    async def get_department_detail(self, department_id: str) -> Optional[DepartmentDetailResponse]:
        """Get specific department detail by ID"""
        
        # Query to get department detail with all required data
        department_detail_query = text("""
            SELECT 
                d.name as department_name,
                COALESCE(d.description, d.name || ' department') as description,
                COUNT(DISTINCT u.id) as total_employees,
                COUNT(DISTINCT CASE WHEN u.status = true THEN u.id END) as active_learners,
                COALESCE(
                    ROUND(AVG(CASE WHEN c.progress IS NOT NULL THEN c.progress END)), 
                    0
                ) as avg_progress,
                COUNT(CASE WHEN c.is_completed = true THEN c.id END) as courses_completed
            FROM departments d
            LEFT JOIN users u ON d.id = u.department_id
            LEFT JOIN courses c ON u.id = c.user_id
            WHERE d.id = :department_id
            GROUP BY d.id, d.name, d.description
        """)
        
        result = self.db.execute(department_detail_query, {"department_id": department_id}).fetchone()
        
        if not result:
            return None
        
        return DepartmentDetailResponse(
            department_name=result.department_name,
            description=result.description,
            total_employees=result.total_employees or 0,
            active_learners=result.active_learners or 0,
            avg_progress=int(result.avg_progress) if result.avg_progress else 0,
            courses_completed=result.courses_completed or 0
        )
    
    async def get_department_list(self) -> DepartmentListResponse:
        """Get list of all departments"""
        
        # Query to get all departments
        department_list_query = text("""
            SELECT 
                d.id,
                d.name,
                COALESCE(d.description, d.name || ' department') as description,
                d.created_at
            FROM departments d
            ORDER BY d.name
        """)
        
        result = self.db.execute(department_list_query).fetchall()
        
        departments = []
        for row in result:
            departments.append(DepartmentListItem(
                id=str(row.id),
                name=row.name,
                description=row.description,
                created_at=row.created_at.isoformat() if row.created_at else ""
            ))
        
        return DepartmentListResponse(departments=departments)
