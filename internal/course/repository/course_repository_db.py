import logging
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import text
from internal.course.repository.course_repository import CourseRepository
from internal.course.model.course_dto import CourseListResponse, CourseListItem, CourseDetail, ModuleDetail, LessonDetail

logger = logging.getLogger(__name__)

class DatabaseCourseRepository(CourseRepository):
    """Database repository for course operations using raw SQL queries"""

    def __init__(self, db: Session):
        self.db = db

    async def get_courses_by_user(self, user_id: UUID) -> CourseListResponse:
        """Get all courses for a user"""
        try:
            # Query to get all courses for the user
            courses_query = text("""
                SELECT id, title, description, estimated_duration, difficulty, 
                       learning_objectives, source_from, progress, is_completed, 
                       created_at, updated_at
                FROM courses 
                WHERE user_id = :user_id 
                ORDER BY created_at DESC
            """)
            
            result = self.db.execute(courses_query, {"user_id": user_id})
            courses_data = result.fetchall()
            
            # Convert to CourseListItem objects
            courses = []
            for row in courses_data:
                course_item = CourseListItem(
                    id=row.id,
                    title=row.title,
                    description=row.description,
                    estimated_duration=row.estimated_duration,
                    difficulty=row.difficulty,
                    learning_objectives=row.learning_objectives,
                    source_from=row.source_from,
                    progress=row.progress,
                    is_completed=row.is_completed,
                    created_at=row.created_at.isoformat() if row.created_at else "",
                    updated_at=row.updated_at.isoformat() if row.updated_at else ""
                )
                courses.append(course_item)
            
            return CourseListResponse(
                courses=courses,
                total=len(courses)
            )
            
        except Exception as e:
            logger.error(f"Error getting courses for user {user_id}: {str(e)}")
            raise e

    async def get_course_by_id(self, course_id: UUID, user_id: UUID) -> Optional[CourseDetail]:
        """Get a course by ID for a specific user with modules and lessons using JOIN query"""
        try:
            # Single JOIN query to get course, modules, and lessons in one go
            join_query = text("""
                SELECT 
                    c.id as course_id,
                    c.title as course_title,
                    c.description as course_description,
                    c.estimated_duration as course_estimated_duration,
                    c.difficulty as course_difficulty,
                    c.learning_objectives as course_learning_objectives,
                    c.source_from as course_source_from,
                    c.progress as course_progress,
                    c.is_completed as course_is_completed,
                    c.created_at as course_created_at,
                    c.updated_at as course_updated_at,
                    m.id as module_id,
                    m.title as module_title,
                    m.order_index as module_order_index,
                    m.is_completed as module_is_completed,
                    m.created_at as module_created_at,
                    m.updated_at as module_updated_at,
                    l.id as lesson_id,
                    l.title as lesson_title,
                    l.content as lesson_content,
                    l.index as lesson_index,
                    l.is_completed as lesson_is_completed,
                    l.created_at as lesson_created_at,
                    l.updated_at as lesson_updated_at
                FROM courses c
                LEFT JOIN modules m ON c.id = m.course_id
                LEFT JOIN lessons l ON m.id = l.module_id
                WHERE c.id = :course_id AND c.user_id = :user_id
                ORDER BY m.order_index ASC, l.index ASC
            """)
            
            result = self.db.execute(join_query, {"course_id": course_id, "user_id": user_id})
            rows = result.fetchall()
            
            if not rows:
                return None
            
            # Get course data from first row
            first_row = rows[0]
            course_detail = CourseDetail(
                id=first_row.course_id,
                title=first_row.course_title,
                description=first_row.course_description,
                estimated_duration=first_row.course_estimated_duration,
                difficulty=first_row.course_difficulty,
                learning_objectives=first_row.course_learning_objectives,
                source_from=first_row.course_source_from,
                progress=first_row.course_progress,
                is_completed=first_row.course_is_completed,
                created_at=first_row.course_created_at.isoformat() if first_row.course_created_at else "",
                updated_at=first_row.course_updated_at.isoformat() if first_row.course_updated_at else "",
                modules=[]
            )
            
            # Group data by modules and lessons
            modules_dict = {}
            lessons_dict = {}
            
            for row in rows:
                # Process module if it exists and not already processed
                if row.module_id and row.module_id not in modules_dict:
                    modules_dict[row.module_id] = ModuleDetail(
                        id=row.module_id,
                        title=row.module_title,
                        order_index=row.module_order_index,
                        is_completed=row.module_is_completed,
                        created_at=row.module_created_at.isoformat() if row.module_created_at else "",
                        updated_at=row.module_updated_at.isoformat() if row.module_updated_at else "",
                        lessons=[]
                    )
                
                # Process lesson if it exists and not already processed
                if row.lesson_id and row.lesson_id not in lessons_dict:
                    lesson_detail = LessonDetail(
                        id=row.lesson_id,
                        title=row.lesson_title,
                        content=row.lesson_content,
                        index=row.lesson_index,
                        is_completed=row.lesson_is_completed,
                        created_at=row.lesson_created_at.isoformat() if row.lesson_created_at else "",
                        updated_at=row.lesson_updated_at.isoformat() if row.lesson_updated_at else ""
                    )
                    lessons_dict[row.lesson_id] = lesson_detail
                    
                    # Add lesson to its module
                    if row.module_id and row.module_id in modules_dict:
                        modules_dict[row.module_id].lessons.append(lesson_detail)
            
            # Convert modules dict to list and add to course
            course_detail.modules = list(modules_dict.values())
            
            return course_detail
            
        except Exception as e:
            logger.error(f"Error getting course {course_id} for user {user_id}: {str(e)}")
            raise e
