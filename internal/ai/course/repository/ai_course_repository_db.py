import logging
import json
from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy.orm import Session
from sqlalchemy import text
from internal.ai.course.repository.ai_course_repository import AiCourseRepository
from internal.ai.course.model.course_dto import AiCourseGenerateResponse, ExternalAiCourseGenerateResponse, CourseListResponse, CourseListItem

logger = logging.getLogger(__name__)

class DatabaseAiCourseRepository(AiCourseRepository):
    """Database repository for AI course operations using raw SQL queries"""

    def __init__(self, db: Session):
        self.db = db

    async def save_course(self, user_id: UUID, external_response: ExternalAiCourseGenerateResponse) -> AiCourseGenerateResponse:
        """Save a generated course to the database using raw SQL queries with explicit transaction"""
        try:
            # Generate course ID
            course_id = uuid4()
            
            # Insert course
            self._insert_course(course_id, user_id, external_response)
            
            # Insert modules, lessons, and quizzes
            self._insert_modules_and_lessons(course_id, external_response)
            
            # Commit the transaction
            self.db.commit()
            
            return AiCourseGenerateResponse(
                course_id=course_id,
                external_response=external_response
            )
                
        except Exception as e:
            # Rollback the transaction
            self.db.rollback()
            raise e

    def _insert_course(self, course_id: UUID, user_id: UUID, external_response: ExternalAiCourseGenerateResponse) -> None:
        """Insert course record"""
        course_query = text("""
            INSERT INTO courses (id, user_id, title, description, estimated_duration, difficulty, learning_objectives, source_from, progress, is_completed, created_at, updated_at)
            VALUES (:id, :user_id, :title, :description, :estimated_duration, :difficulty, :learning_objectives, :source_from, :progress, :is_completed, NOW(), NOW())
        """)
        
        self.db.execute(course_query, {
            "id": course_id,
            "user_id": user_id,
            "title": external_response.title,
            "description": external_response.description,
            "estimated_duration": external_response.estimated_duration,
            "difficulty": external_response.difficulty,
            "learning_objectives": external_response.learning_objectives,
            "source_from": external_response.source_from,
            "progress": 0.0,
            "is_completed": False
        })

    def _insert_modules_and_lessons(self, course_id: UUID, external_response: ExternalAiCourseGenerateResponse) -> None:
        """Insert modules, their lessons, and quizzes"""
        for module_data in external_response.modules:
            module_id = uuid4()
            
            # Insert module using the index from input data
            self._insert_module(module_id, course_id, module_data)
            
            # Insert lessons for this module
            self._insert_lessons(module_id, module_data.lessons)
            
            # Insert quiz for this module if present
            if module_data.quiz:
                self._insert_quiz(module_id, module_data.quiz)

    def _insert_module(self, module_id: UUID, course_id: UUID, module_data) -> None:
        """Insert module record"""
        module_query = text("""
            INSERT INTO modules (id, course_id, title, order_index, is_completed, created_at, updated_at)
            VALUES (:id, :course_id, :title, :order_index, :is_completed, NOW(), NOW())
        """)
        
        self.db.execute(module_query, {
            "id": module_id,
            "course_id": course_id,
            "title": module_data.title,
            "order_index": module_data.index,  # Use index from input data
            "is_completed": False
        })

    def _insert_lessons(self, module_id: UUID, lessons) -> None:
        """Insert lessons for a module"""
        for lesson_data in lessons:
            lesson_id = uuid4()
            
            lesson_query = text("""
                INSERT INTO lessons (id, module_id, title, content, index, is_completed, created_at, updated_at)
                VALUES (:id, :module_id, :title, :content, :index, :is_completed, NOW(), NOW())
            """)
            
            self.db.execute(lesson_query, {
                "id": lesson_id,
                "module_id": module_id,
                "title": lesson_data.title,
                "content": lesson_data.content,
                "index": lesson_data.index,  # Use index from input data
                "is_completed": False
            })

    def _insert_quiz(self, module_id: UUID, quiz_questions) -> None:
        """Insert quiz questions one by one for a module"""
        quiz_query = text("""
            INSERT INTO quizzes (id, module_id, questions, is_completed, is_correct, created_at, updated_at)
            VALUES (:id, :module_id, :questions, :is_completed, :is_correct, NOW(), NOW())
        """)
        
        # Insert each question as a separate row
        for question_data in quiz_questions:
            quiz_id = uuid4()
            
            # Convert single question to JSON format
            question_json = {
                "question": question_data.question,
                "choices": question_data.choices,
                "answer": question_data.answer
            }
            
            self.db.execute(quiz_query, {
                "id": quiz_id,
                "module_id": module_id,
                "questions": json.dumps(question_json),
                "is_completed": False,
                "is_correct": False
            })

