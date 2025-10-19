from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy.orm import Session
from sqlalchemy import text
from internal.ai.chat.model.session_model import CourseChatSession, GuideChatSession
from datetime import datetime, timezone, timedelta

# GMT+7 timezone
GMT_PLUS_7 = timezone(timedelta(hours=7))

class SessionRepository:
    """Repository for chat session operations using raw queries"""
    
    def __init__(self, db: Session):
        self.db = db

    async def get_or_create_course_session(self, user_id: UUID, course_id: UUID, ai_session_id: str) -> CourseChatSession:
        """Get existing course session or create a new one using raw query"""
        # Try to get existing session
        query = text("""
            SELECT id, user_id, course_id, ai_session_id, created_at, updated_at
            FROM course_chat_sessions 
            WHERE user_id = :user_id AND course_id = :course_id
        """)
        
        result = self.db.execute(query, {"user_id": str(user_id), "course_id": str(course_id)}).fetchone()
        
        if result:
            return CourseChatSession(
                id=result[0] if isinstance(result[0], UUID) else UUID(result[0]),
                user_id=result[1] if isinstance(result[1], UUID) else UUID(result[1]),
                course_id=result[2] if isinstance(result[2], UUID) else UUID(result[2]),
                ai_session_id=result[3],
                created_at=result[4],
                updated_at=result[5]
            )
        
        # Create new session
        insert_query = text("""
            INSERT INTO course_chat_sessions (id, user_id, course_id, ai_session_id, created_at, updated_at)
            VALUES (:id, :user_id, :course_id, :ai_session_id, :created_at, :updated_at)
            RETURNING id, user_id, course_id, ai_session_id, created_at, updated_at
        """)
        
        session_id = uuid4()
        now = datetime.now(GMT_PLUS_7)
        
        result = self.db.execute(insert_query, {
            "id": str(session_id),
            "user_id": str(user_id),
            "course_id": str(course_id),
            "ai_session_id": ai_session_id,
            "created_at": now,
            "updated_at": now
        }).fetchone()
        
        self.db.commit()
        
        return CourseChatSession(
            id=result[0] if isinstance(result[0], UUID) else UUID(result[0]),
            user_id=result[1] if isinstance(result[1], UUID) else UUID(result[1]),
            course_id=result[2] if isinstance(result[2], UUID) else UUID(result[2]),
            ai_session_id=result[3],
            created_at=result[4],
            updated_at=result[5]
        )

    async def get_or_create_guide_session(self, user_id: UUID, guide_id: UUID, ai_session_id: str) -> GuideChatSession:
        """Get existing guide session or create a new one using raw query"""
        # Try to get existing session
        query = text("""
            SELECT id, user_id, guide_id, ai_session_id, created_at, updated_at
            FROM guide_chat_sessions 
            WHERE user_id = :user_id AND guide_id = :guide_id
        """)
        
        result = self.db.execute(query, {"user_id": str(user_id), "guide_id": str(guide_id)}).fetchone()
        
        if result:
            return GuideChatSession(
                id=result[0] if isinstance(result[0], UUID) else UUID(result[0]),
                user_id=result[1] if isinstance(result[1], UUID) else UUID(result[1]),
                guide_id=result[2] if isinstance(result[2], UUID) else UUID(result[2]),
                ai_session_id=result[3],
                created_at=result[4],
                updated_at=result[5]
            )
        
        # Create new session
        insert_query = text("""
            INSERT INTO guide_chat_sessions (id, user_id, guide_id, ai_session_id, created_at, updated_at)
            VALUES (:id, :user_id, :guide_id, :ai_session_id, :created_at, :updated_at)
            RETURNING id, user_id, guide_id, ai_session_id, created_at, updated_at
        """)
        
        session_id = uuid4()
        now = datetime.now(GMT_PLUS_7)
        
        result = self.db.execute(insert_query, {
            "id": str(session_id),
            "user_id": str(user_id),
            "guide_id": str(guide_id),
            "ai_session_id": ai_session_id,
            "created_at": now,
            "updated_at": now
        }).fetchone()
        
        self.db.commit()
        
        return GuideChatSession(
            id=result[0] if isinstance(result[0], UUID) else UUID(result[0]),
            user_id=result[1] if isinstance(result[1], UUID) else UUID(result[1]),
            guide_id=result[2] if isinstance(result[2], UUID) else UUID(result[2]),
            ai_session_id=result[3],
            created_at=result[4],
            updated_at=result[5]
        )

    async def get_course_session(self, user_id: UUID, course_id: UUID) -> Optional[CourseChatSession]:
        """Get existing course session using raw query"""
        query = text("""
            SELECT id, user_id, course_id, ai_session_id, created_at, updated_at
            FROM course_chat_sessions 
            WHERE user_id = :user_id AND course_id = :course_id
        """)
        
        result = self.db.execute(query, {"user_id": str(user_id), "course_id": str(course_id)}).fetchone()
        
        if result:
            return CourseChatSession(
                id=result[0] if isinstance(result[0], UUID) else UUID(result[0]),
                user_id=result[1] if isinstance(result[1], UUID) else UUID(result[1]),
                course_id=result[2] if isinstance(result[2], UUID) else UUID(result[2]),
                ai_session_id=result[3],
                created_at=result[4],
                updated_at=result[5]
            )
        return None

    async def get_guide_session(self, user_id: UUID, guide_id: UUID) -> Optional[GuideChatSession]:
        """Get existing guide session using raw query"""
        query = text("""
            SELECT id, user_id, guide_id, ai_session_id, created_at, updated_at
            FROM guide_chat_sessions 
            WHERE user_id = :user_id AND guide_id = :guide_id
        """)
        
        result = self.db.execute(query, {"user_id": str(user_id), "guide_id": str(guide_id)}).fetchone()
        
        if result:
            return GuideChatSession(
                id=result[0] if isinstance(result[0], UUID) else UUID(result[0]),
                user_id=result[1] if isinstance(result[1], UUID) else UUID(result[1]),
                guide_id=result[2] if isinstance(result[2], UUID) else UUID(result[2]),
                ai_session_id=result[3],
                created_at=result[4],
                updated_at=result[5]
            )
        return None

    async def update_session_timestamp(self, session_id: UUID, is_course: bool = True) -> None:
        """Update session timestamp using raw query"""
        if is_course:
            query = text("""
                UPDATE course_chat_sessions 
                SET updated_at = :updated_at 
                WHERE id = :session_id
            """)
        else:
            query = text("""
                UPDATE guide_chat_sessions 
                SET updated_at = :updated_at 
                WHERE id = :session_id
            """)
        
        self.db.execute(query, {
            "session_id": str(session_id),
            "updated_at": datetime.now(GMT_PLUS_7)
        })
        self.db.commit()
