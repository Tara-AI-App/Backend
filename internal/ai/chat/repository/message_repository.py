from typing import List, Optional
from uuid import UUID, uuid4
from sqlalchemy.orm import Session
from sqlalchemy import text
from internal.ai.chat.model.message_model import ChatMessage
from datetime import datetime, timezone, timedelta

# GMT+7 timezone
GMT_PLUS_7 = timezone(timedelta(hours=7))

class MessageRepository:
    """Repository for chat message operations using raw queries"""
    
    def __init__(self, db: Session):
        self.db = db

    async def save_course_message(self, session_id: UUID, content: str, is_user: bool, message_order: int) -> ChatMessage:
        """Save a message for a course session using raw query"""
        insert_query = text("""
            INSERT INTO chat_messages (id, course_session_id, content, is_user, message_order, created_at)
            VALUES (:id, :course_session_id, :content, :is_user, :message_order, :created_at)
            RETURNING id, course_session_id, guide_session_id, content, is_user, message_order, created_at
        """)
        
        message_id = uuid4()
        now = datetime.now(GMT_PLUS_7)
        
        result = self.db.execute(insert_query, {
            "id": str(message_id),
            "course_session_id": str(session_id),
            "content": content,
            "is_user": is_user,
            "message_order": message_order,
            "created_at": now
        }).fetchone()
        
        self.db.commit()
        
        return ChatMessage(
            id=result[0] if isinstance(result[0], UUID) else UUID(result[0]),
            course_session_id=result[1] if isinstance(result[1], UUID) else (UUID(result[1]) if result[1] else None),
            guide_session_id=result[2] if isinstance(result[2], UUID) else (UUID(result[2]) if result[2] else None),
            content=result[3],
            is_user=result[4],
            message_order=result[5],
            created_at=result[6]
        )

    async def save_guide_message(self, session_id: UUID, content: str, is_user: bool, message_order: int) -> ChatMessage:
        """Save a message for a guide session using raw query"""
        insert_query = text("""
            INSERT INTO chat_messages (id, guide_session_id, content, is_user, message_order, created_at)
            VALUES (:id, :guide_session_id, :content, :is_user, :message_order, :created_at)
            RETURNING id, course_session_id, guide_session_id, content, is_user, message_order, created_at
        """)
        
        message_id = uuid4()
        now = datetime.now(GMT_PLUS_7)
        
        result = self.db.execute(insert_query, {
            "id": str(message_id),
            "guide_session_id": str(session_id),
            "content": content,
            "is_user": is_user,
            "message_order": message_order,
            "created_at": now
        }).fetchone()
        
        self.db.commit()
        
        return ChatMessage(
            id=result[0] if isinstance(result[0], UUID) else UUID(result[0]),
            course_session_id=result[1] if isinstance(result[1], UUID) else (UUID(result[1]) if result[1] else None),
            guide_session_id=result[2] if isinstance(result[2], UUID) else (UUID(result[2]) if result[2] else None),
            content=result[3],
            is_user=result[4],
            message_order=result[5],
            created_at=result[6]
        )

    async def get_course_messages(self, session_id: UUID) -> List[ChatMessage]:
        """Get all messages for a course session using raw query"""
        query = text("""
            SELECT id, course_session_id, guide_session_id, content, is_user, message_order, created_at
            FROM chat_messages 
            WHERE course_session_id = :session_id
            ORDER BY message_order ASC
        """)
        
        results = self.db.execute(query, {"session_id": str(session_id)}).fetchall()
        
        return [
            ChatMessage(
                id=row[0] if isinstance(row[0], UUID) else UUID(row[0]),
                course_session_id=row[1] if isinstance(row[1], UUID) else (UUID(row[1]) if row[1] else None),
                guide_session_id=row[2] if isinstance(row[2], UUID) else (UUID(row[2]) if row[2] else None),
                content=row[3],
                is_user=row[4],
                message_order=row[5],
                created_at=row[6]
            )
            for row in results
        ]

    async def get_guide_messages(self, session_id: UUID) -> List[ChatMessage]:
        """Get all messages for a guide session using raw query"""
        query = text("""
            SELECT id, course_session_id, guide_session_id, content, is_user, message_order, created_at
            FROM chat_messages 
            WHERE guide_session_id = :session_id
            ORDER BY message_order ASC
        """)
        
        results = self.db.execute(query, {"session_id": str(session_id)}).fetchall()
        
        return [
            ChatMessage(
                id=row[0] if isinstance(row[0], UUID) else UUID(row[0]),
                course_session_id=row[1] if isinstance(row[1], UUID) else (UUID(row[1]) if row[1] else None),
                guide_session_id=row[2] if isinstance(row[2], UUID) else (UUID(row[2]) if row[2] else None),
                content=row[3],
                is_user=row[4],
                message_order=row[5],
                created_at=row[6]
            )
            for row in results
        ]

    async def get_next_message_order(self, session_id: UUID, is_course: bool = True) -> int:
        """Get the next message order number for a session using raw query"""
        if is_course:
            query = text("""
                SELECT message_order
                FROM chat_messages 
                WHERE course_session_id = :session_id
                ORDER BY message_order DESC
                LIMIT 1
            """)
        else:
            query = text("""
                SELECT message_order
                FROM chat_messages 
                WHERE guide_session_id = :session_id
                ORDER BY message_order DESC
                LIMIT 1
            """)
        
        result = self.db.execute(query, {"session_id": str(session_id)}).fetchone()
        
        if not result:
            return 1
        return result[0] + 1
