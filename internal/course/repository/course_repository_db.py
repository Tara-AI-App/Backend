import logging
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import text
from internal.course.repository.course_repository import CourseRepository
from internal.course.model.course_dto import CourseListResponse, CourseListItem, CourseDetail, ModuleDetail, LessonDetail, QuizDetail, LessonCompletionResponse, QuizCompletionResponse

logger = logging.getLogger(__name__)

class DatabaseCourseRepository(CourseRepository):
    """Database repository for course operations using raw SQL queries"""

    def __init__(self, db: Session):
        self.db = db

    async def get_courses_by_user(self, user_id: UUID, limit: int = 10, offset: int = 0) -> CourseListResponse:
        """Get courses for a user with pagination"""
        try:
            # Query to get total count
            count_query = text("""
                SELECT COUNT(*) as total
                FROM courses 
                WHERE user_id = :user_id
            """)
            
            count_result = self.db.execute(count_query, {"user_id": user_id})
            total_count = count_result.fetchone().total
            
            # Query to get paginated courses for the user
            courses_query = text("""
                SELECT id, title, description, estimated_duration, difficulty, 
                       learning_objectives, source_from, progress, is_completed, 
                       skill, created_at, updated_at
                FROM courses 
                WHERE user_id = :user_id 
                ORDER BY created_at DESC
                LIMIT :limit OFFSET :offset
            """)
            
            result = self.db.execute(courses_query, {
                "user_id": user_id,
                "limit": limit,
                "offset": offset
            })
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
                    skill=row.skill,
                    progress=row.progress,
                    is_completed=row.is_completed,
                    created_at=row.created_at.isoformat() if row.created_at else "",
                    updated_at=row.updated_at.isoformat() if row.updated_at else ""
                )
                courses.append(course_item)
            
            return CourseListResponse(
                courses=courses,
                total=total_count
            )
            
        except Exception as e:
            logger.error(f"Error getting courses for user {user_id}: {str(e)}")
            raise e

    async def get_course_by_id(self, course_id: UUID, user_id: UUID) -> Optional[CourseDetail]:
        """Get a course by ID for a specific user with modules and lessons using JOIN query"""
        try:
            # Single JOIN query to get course, modules, lessons, and quizzes in one go
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
                    l.updated_at as lesson_updated_at,
                    q.id as quiz_id,
                    q.questions as quiz_questions,
                    q.is_completed as quiz_is_completed,
                    q.is_correct as quiz_is_correct,
                    q.created_at as quiz_created_at,
                    q.updated_at as quiz_updated_at
                FROM courses c
                LEFT JOIN modules m ON c.id = m.course_id
                LEFT JOIN lessons l ON m.id = l.module_id
                LEFT JOIN quizzes q ON m.id = q.module_id
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
            
            # Group data by modules, lessons, and quizzes
            modules_dict = {}
            lessons_dict = {}
            quizzes_dict = {}
            
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
                        lessons=[],
                        quizzes=[]
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
                
                # Process quiz if it exists and not already processed
                if row.quiz_id and row.quiz_id not in quizzes_dict:
                    quiz_detail = QuizDetail(
                        id=row.quiz_id,
                        questions=row.quiz_questions if row.quiz_questions else [],
                        is_completed=row.quiz_is_completed,
                        is_correct=row.quiz_is_correct,
                        created_at=row.quiz_created_at.isoformat() if row.quiz_created_at else "",
                        updated_at=row.quiz_updated_at.isoformat() if row.quiz_updated_at else ""
                    )
                    quizzes_dict[row.quiz_id] = quiz_detail
                    
                    # Add quiz to its module
                    if row.module_id and row.module_id in modules_dict:
                        modules_dict[row.module_id].quizzes.append(quiz_detail)
            
            # Convert modules dict to list and add to course
            course_detail.modules = list(modules_dict.values())
            
            return course_detail
            
        except Exception as e:
            logger.error(f"Error getting course {course_id} for user {user_id}: {str(e)}")
            raise e

    async def update_lesson_completion(self, lesson_id: UUID, user_id: UUID, is_completed: bool) -> LessonCompletionResponse:
        """Update lesson completion status for a specific lesson"""
        try:
            # First verify that the lesson exists and belongs to a course owned by the user
            verify_query = text("""
                SELECT l.id, l.is_completed, c.id as course_id, c.user_id
                FROM lessons l
                JOIN modules m ON l.module_id = m.id
                JOIN courses c ON m.course_id = c.id
                WHERE l.id = :lesson_id AND c.user_id = :user_id
            """)
            
            result = self.db.execute(verify_query, {"lesson_id": lesson_id, "user_id": user_id})
            lesson_data = result.fetchone()
            
            if not lesson_data:
                return LessonCompletionResponse(
                    success=False,
                    message="Lesson not found or access denied",
                    lesson_id=lesson_id,
                    is_completed=False
                )
            
            # Get the course_id for progress calculation
            course_id = lesson_data.course_id
            
            # Update the lesson completion status
            update_query = text("""
                UPDATE lessons 
                SET is_completed = :is_completed, 
                    updated_at = NOW()
                WHERE id = :lesson_id
            """)
            
            self.db.execute(update_query, {
                "lesson_id": lesson_id,
                "is_completed": is_completed
            })
            
            # First check and update module completion status based on lessons and quizzes
            await self.check_and_update_module_completion(course_id, user_id)
            
            # Calculate course progress after potential module updates
            calculated_progress = await self.calculate_course_progress(course_id, user_id)
            
            # Update course progress (this will commit both lesson and progress updates)
            progress_updated = await self.update_course_progress(course_id, user_id, calculated_progress)
            
            if not progress_updated:
                # If progress update failed but lesson update succeeded, we still committed lesson update
                logger.warning(f"Lesson {lesson_id} updated but course progress update failed")
            
            logger.info(f"Updated lesson {lesson_id} completion status to {is_completed} for user {user_id}. "
                       f"Modules auto-checked for completion. Course progress updated to {calculated_progress:.2f}%")
            
            return LessonCompletionResponse(
                success=True,
                message=f"Lesson {'marked as completed' if is_completed else 'marked as incomplete'}. "
                       f"Course progress: {calculated_progress:.1f}%",
                lesson_id=lesson_id,
                is_completed=is_completed
            )
            
        except Exception as e:
            logger.error(f"Error updating lesson {lesson_id} completion for user {user_id}: {str(e)}")
            self.db.rollback()
            raise e

    async def update_quiz_completion(self, quiz_id: UUID, user_id: UUID, is_completed: bool) -> QuizCompletionResponse:
        """Update quiz completion status for a specific quiz"""
        try:
            # First verify that the quiz exists and belongs to a course owned by the user
            verify_query = text("""
                SELECT q.id, q.is_completed, c.id as course_id, c.user_id
                FROM quizzes q
                JOIN modules m ON q.module_id = m.id
                JOIN courses c ON m.course_id = c.id
                WHERE q.id = :quiz_id AND c.user_id = :user_id
            """)
            
            result = self.db.execute(verify_query, {"quiz_id": quiz_id, "user_id": user_id})
            quiz_data = result.fetchone()
            
            if not quiz_data:
                return QuizCompletionResponse(
                    success=False,
                    message="Quiz not found or access denied",
                    quiz_id=quiz_id,
                    is_completed=False
                )
            
            # Get the course_id for progress calculation
            course_id = quiz_data.course_id
            
            # Update the quiz completion status
            update_query = text("""
                UPDATE quizzes 
                SET is_completed = :is_completed, 
                    updated_at = NOW()
                WHERE id = :quiz_id
            """)
            
            self.db.execute(update_query, {
                "quiz_id": quiz_id,
                "is_completed": is_completed
            })
            
            # First check and update module completion status based on lessons and quizzes
            await self.check_and_update_module_completion(course_id, user_id)
            
            # Calculate course progress after potential module updates
            calculated_progress = await self.calculate_course_progress(course_id, user_id)
            
            # Update course progress (this will commit both quiz and progress updates)
            progress_updated = await self.update_course_progress(course_id, user_id, calculated_progress)
            
            if not progress_updated:
                # If progress update failed but quiz update succeeded, we still committed quiz update
                logger.warning(f"Quiz {quiz_id} updated but course progress update failed")
            
            logger.info(f"Updated quiz {quiz_id} completion status to {is_completed} for user {user_id}. "
                       f"Modules auto-checked for completion. Course progress updated to {calculated_progress:.2f}%")
            
            return QuizCompletionResponse(
                success=True,
                message=f"Quiz {'marked as completed' if is_completed else 'marked as incomplete'}. "
                       f"Course progress: {calculated_progress:.1f}%",
                quiz_id=quiz_id,
                is_completed=is_completed
            )
            
        except Exception as e:
            logger.error(f"Error updating quiz {quiz_id} completion for user {user_id}: {str(e)}")
            self.db.rollback()
            raise e

    async def calculate_course_progress(self, course_id: UUID, user_id: UUID) -> float:
        """Calculate course progress based on completed lessons, modules, and quizzes"""
        try:
            # Query to get completion status of all course components
            progress_query = text("""
                SELECT 
                    COUNT(DISTINCT m.id) as total_modules,
                    COUNT(DISTINCT CASE WHEN m.is_completed = true THEN m.id END) as completed_modules,
                    COUNT(DISTINCT l.id) as total_lessons,
                    COUNT(DISTINCT CASE WHEN l.is_completed = true THEN l.id END) as completed_lessons,
                    COUNT(DISTINCT q.id) as total_quizzes,
                    COUNT(DISTINCT CASE WHEN q.is_completed = true THEN q.id END) as completed_quizzes
                FROM courses c
                JOIN modules m ON c.id = m.course_id
                LEFT JOIN lessons l ON m.id = l.module_id
                LEFT JOIN quizzes q ON m.id = q.module_id
                WHERE c.id = :course_id AND c.user_id = :user_id
            """)
            
            result = self.db.execute(progress_query, {"course_id": course_id, "user_id": user_id})
            row = result.fetchone()
            
            if not row:
                return 0.0
            
            total_modules = row.total_modules or 0
            completed_modules = row.completed_modules or 0
            total_lessons = row.total_lessons or 0
            completed_lessons = row.completed_lessons or 0
            total_quizzes = row.total_quizzes or 0
            completed_quizzes = row.completed_quizzes or 0
            
            # Calculate dynamic weights based on course composition
            # Each component gets weight proportional to its contribution to total items
            # 
            # Example:
            # - Course has 2 modules, 8 lessons, 2 quizzes (12 total items)
            # - Module weight: 2/12 * 100% = 16.67%
            # - Lesson weight: 8/12 * 100% = 66.67% 
            # - Quiz weight: 2/12 * 100% = 16.67%
            # This ensures progress reflects the actual course structure
            
            total_completable_items = total_modules + total_lessons + total_quizzes
            
            if total_completable_items == 0:
                return 100.0  # Empty course is 100% complete
            
            # Import necessary types
            from typing import Tuple
            
            # Calculate weights based on actual course composition
            module_weight_pct = (total_modules / total_completable_items) * 100 if total_completable_items > 0 else 0
            lesson_weight_pct = (total_lessons / total_completable_items) * 100 if total_completable_items > 0 else 0  
            quiz_weight_pct = (total_quizzes / total_completable_items) * 100 if total_completable_items > 0 else 0
            
            # Calculate weighted progress based on completion ratios
            module_progress = (completed_modules / total_modules) * module_weight_pct if total_modules > 0 else module_weight_pct
            lesson_progress = (completed_lessons / total_lessons) * lesson_weight_pct if total_lessons > 0 else lesson_weight_pct
            quiz_progress = (completed_quizzes / total_quizzes) * quiz_weight_pct if total_quizzes > 0 else quiz_weight_pct
            
            # Final progress is sum of weighted progress components
            final_progress = module_progress + lesson_progress + quiz_progress
            
            logger.info(f"Course {course_id} progress: "
                       f"Modules({completed_modules}/{total_modules}, weight: {module_weight_pct:.1f}%), "
                       f"Lessons({completed_lessons}/{total_lessons}, weight: {lesson_weight_pct:.1f}%), "
                       f"Quizzes({completed_quizzes}/{total_quizzes}, weight: {quiz_weight_pct:.1f}%), "
                       f"Final Progress: {final_progress:.2f}%")
            
            return min(100.0, max(0.0, final_progress))  # Ensure 0-100 range
            
        except Exception as e:
            logger.error(f"Error calculating progress for course {course_id}: {str(e)}")
            return 0.0

    async def update_course_progress(self, course_id: UUID, user_id: UUID, progress: float) -> bool:
        """Update course progress and completion status"""
        try:
            # Calculate if course should be marked as completed
            is_course_completed = progress >= 100.0
            
            # Update course progress and completion status
            update_query = text("""
                UPDATE courses 
                SET progress = :progress, 
                    is_completed = :is_completed,
                    updated_at = NOW()
                WHERE id = :course_id AND user_id = :user_id
            """)
            
            result = self.db.execute(update_query, {
                "course_id": course_id,
                "user_id": user_id,
                "progress": progress,
                "is_completed": is_course_completed
            })
            
            # Check if the course was found and updated
            if result.rowcount == 0:
                logger.warning(f"Course {course_id} not found or access denied for user {user_id}")
                return False
            
            # Commit the transaction
            self.db.commit()
            
            logger.info(f"Updated course {course_id} progress to {progress:.2f}%, completed: {is_course_completed}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating course progress for {course_id}: {str(e)}")
            self.db.rollback()
            return False

    async def check_and_update_module_completion(self, course_id: UUID, user_id: UUID) -> None:
        """Check all modules and auto-complete them if all lessons and quizzes are completed"""
        try:
            # Query to get module completion status and their lesson/quiz counts
            module_check_query = text("""
                SELECT 
                    m.id as module_id,
                    m.is_completed as module_completed,
                    COUNT(DISTINCT l.id) as total_lessons,
                    COUNT(DISTINCT CASE WHEN l.is_completed = true THEN l.id END) as completed_lessons,
                    COUNT(DISTINCT q.id) as total_quizzes,
                    COUNT(DISTINCT CASE WHEN q.is_completed = true THEN q.id END) as completed_quizzes
                FROM modules m
                LEFT JOIN lessons l ON m.id = l.module_id
                LEFT JOIN quizzes q ON m.id = q.module_id
                WHERE m.course_id = :course_id
                GROUP BY m.id, m.is_completed
                ORDER BY m.order_index
            """)
            
            result = self.db.execute(module_check_query, {"course_id": course_id})
            modules_data = result.fetchall()
            
            logger.info(f"Checking module completion for course {course_id}")
            
            # Process each module
            for row in modules_data:
                module_id = row.module_id
                currently_completed = row.module_completed
                total_lessons = row.total_lessons or 0
                completed_lessons = row.completed_lessons or 0
                total_quizzes = row.total_quizzes or 0
                completed_quizzes = row.completed_quizzes or 0
                
                # Check if module should be completed
                should_be_completed = (
                    completed_lessons >= total_lessons and 
                    completed_quizzes >= total_quizzes and
                    (total_lessons + total_quizzes) > 0  # Module has content
                )
                
                # Update module completion status if needed
                if should_be_completed != currently_completed:
                    update_module_query = text("""
                        UPDATE modules 
                        SET is_completed = :is_completed, 
                            updated_at = NOW()
                        WHERE id = :module_id
                    """)
                    
                    self.db.execute(update_module_query, {
                        "module_id": module_id,
                        "is_completed": should_be_completed
                    })
                    
                    status_text = "completed" if should_be_completed else "incomplete"
                    logger.info(f"Module {module_id} marked as {status_text}: "
                               f"Lessons({completed_lessons}/{total_lessons}), "
                               f"Quizzes({completed_quizzes}/{total_quizzes})")
                else:
                    logger.debug(f"Module {module_id} completion status unchanged: {currently_completed}")
            
        except Exception as e:
            logger.error(f"Error checking module completion for course {course_id}: {str(e)}")
            # Don't raise exception here - this shouldn't break the main lesson completion flow
