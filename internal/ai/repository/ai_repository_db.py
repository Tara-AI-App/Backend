from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.database.models import AIConversationModel, AIAnalysisModel, AIRecommendationModel
from internal.ai.model.ai_entity import AIConversation, AIAnalysis, AIRecommendation
from internal.ai.repository.ai_repository import AIRepository

class DatabaseAIRepository(AIRepository):
    """Database implementation of AI repository"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def save_conversation(self, conversation: AIConversation) -> AIConversation:
        """Save AI conversation"""
        if conversation.id is None:
            # Create new conversation
            db_conversation = AIConversationModel(
                user_id=conversation.user_id,
                title=conversation.title,
                messages=conversation.messages,
                model_used=conversation.model_used.value,
                provider=conversation.provider.value,
                is_active=conversation.is_active
            )
            self.db.add(db_conversation)
            self.db.commit()
            self.db.refresh(db_conversation)
            
            return AIConversation(
                id=db_conversation.id,
                user_id=db_conversation.user_id,
                title=db_conversation.title,
                messages=db_conversation.messages,
                model_used=conversation.model_used,
                provider=conversation.provider,
                created_at=db_conversation.created_at,
                updated_at=db_conversation.updated_at,
                is_active=db_conversation.is_active
            )
        else:
            # Update existing conversation
            db_conversation = self.db.query(AIConversationModel).filter(
                AIConversationModel.id == conversation.id
            ).first()
            if not db_conversation:
                raise ValueError(f"Conversation with id {conversation.id} not found")
            
            db_conversation.user_id = conversation.user_id
            db_conversation.title = conversation.title
            db_conversation.messages = conversation.messages
            db_conversation.model_used = conversation.model_used.value
            db_conversation.provider = conversation.provider.value
            db_conversation.is_active = conversation.is_active
            db_conversation.updated_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(db_conversation)
            
            return AIConversation(
                id=db_conversation.id,
                user_id=db_conversation.user_id,
                title=db_conversation.title,
                messages=db_conversation.messages,
                model_used=conversation.model_used,
                provider=conversation.provider,
                created_at=db_conversation.created_at,
                updated_at=db_conversation.updated_at,
                is_active=db_conversation.is_active
            )
    
    async def get_conversation(self, conversation_id: int) -> Optional[AIConversation]:
        """Get conversation by ID"""
        db_conversation = self.db.query(AIConversationModel).filter(
            AIConversationModel.id == conversation_id
        ).first()
        if not db_conversation:
            return None
        
        return AIConversation(
            id=db_conversation.id,
            user_id=db_conversation.user_id,
            title=db_conversation.title,
            messages=db_conversation.messages,
            model_used=db_conversation.model_used,
            provider=db_conversation.provider,
            created_at=db_conversation.created_at,
            updated_at=db_conversation.updated_at,
            is_active=db_conversation.is_active
        )
    
    async def get_user_conversations(self, user_id: str, limit: int = 10) -> List[AIConversation]:
        """Get user's conversations"""
        db_conversations = self.db.query(AIConversationModel).filter(
            AIConversationModel.user_id == user_id,
            AIConversationModel.is_active == True
        ).limit(limit).all()
        
        return [
            AIConversation(
                id=conv.id,
                user_id=conv.user_id,
                title=conv.title,
                messages=conv.messages,
                model_used=conv.model_used,
                provider=conv.provider,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                is_active=conv.is_active
            )
            for conv in db_conversations
        ]
    
    async def save_analysis(self, analysis: AIAnalysis) -> AIAnalysis:
        """Save AI analysis"""
        if analysis.id is None:
            # Create new analysis
            db_analysis = AIAnalysisModel(
                item_id=analysis.item_id,
                analysis_type=analysis.analysis_type,
                result=analysis.result,
                confidence=analysis.confidence,
                model_used=analysis.model_used.value,
                provider=analysis.provider.value
            )
            self.db.add(db_analysis)
            self.db.commit()
            self.db.refresh(db_analysis)
            
            return AIAnalysis(
                id=db_analysis.id,
                item_id=db_analysis.item_id,
                analysis_type=db_analysis.analysis_type,
                result=db_analysis.result,
                confidence=db_analysis.confidence,
                model_used=analysis.model_used,
                provider=analysis.provider,
                created_at=db_analysis.created_at,
                updated_at=db_analysis.updated_at
            )
        else:
            # Update existing analysis
            db_analysis = self.db.query(AIAnalysisModel).filter(
                AIAnalysisModel.id == analysis.id
            ).first()
            if not db_analysis:
                raise ValueError(f"Analysis with id {analysis.id} not found")
            
            db_analysis.item_id = analysis.item_id
            db_analysis.analysis_type = analysis.analysis_type
            db_analysis.result = analysis.result
            db_analysis.confidence = analysis.confidence
            db_analysis.model_used = analysis.model_used.value
            db_analysis.provider = analysis.provider.value
            db_analysis.updated_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(db_analysis)
            
            return AIAnalysis(
                id=db_analysis.id,
                item_id=db_analysis.item_id,
                analysis_type=db_analysis.analysis_type,
                result=db_analysis.result,
                confidence=db_analysis.confidence,
                model_used=analysis.model_used,
                provider=analysis.provider,
                created_at=db_analysis.created_at,
                updated_at=db_analysis.updated_at
            )
    
    async def get_analysis(self, analysis_id: int) -> Optional[AIAnalysis]:
        """Get analysis by ID"""
        db_analysis = self.db.query(AIAnalysisModel).filter(
            AIAnalysisModel.id == analysis_id
        ).first()
        if not db_analysis:
            return None
        
        return AIAnalysis(
            id=db_analysis.id,
            item_id=db_analysis.item_id,
            analysis_type=db_analysis.analysis_type,
            result=db_analysis.result,
            confidence=db_analysis.confidence,
            model_used=db_analysis.model_used,
            provider=db_analysis.provider,
            created_at=db_analysis.created_at,
            updated_at=db_analysis.updated_at
        )
    
    async def get_item_analyses(self, item_id: int) -> List[AIAnalysis]:
        """Get analyses for an item"""
        db_analyses = self.db.query(AIAnalysisModel).filter(
            AIAnalysisModel.item_id == item_id
        ).all()
        
        return [
            AIAnalysis(
                id=analysis.id,
                item_id=analysis.item_id,
                analysis_type=analysis.analysis_type,
                result=analysis.result,
                confidence=analysis.confidence,
                model_used=analysis.model_used,
                provider=analysis.provider,
                created_at=analysis.created_at,
                updated_at=analysis.updated_at
            )
            for analysis in db_analyses
        ]
    
    async def save_recommendation(self, recommendation: AIRecommendation) -> AIRecommendation:
        """Save AI recommendation"""
        if recommendation.id is None:
            # Create new recommendation
            db_recommendation = AIRecommendationModel(
                user_id=recommendation.user_id,
                item_ids=recommendation.item_ids,
                reasoning=recommendation.reasoning,
                confidence=recommendation.confidence,
                model_used=recommendation.model_used.value,
                provider=recommendation.provider.value
            )
            self.db.add(db_recommendation)
            self.db.commit()
            self.db.refresh(db_recommendation)
            
            return AIRecommendation(
                id=db_recommendation.id,
                user_id=db_recommendation.user_id,
                item_ids=db_recommendation.item_ids,
                reasoning=db_recommendation.reasoning,
                confidence=db_recommendation.confidence,
                model_used=recommendation.model_used,
                provider=recommendation.provider,
                created_at=db_recommendation.created_at,
                updated_at=db_recommendation.updated_at
            )
        else:
            # Update existing recommendation
            db_recommendation = self.db.query(AIRecommendationModel).filter(
                AIRecommendationModel.id == recommendation.id
            ).first()
            if not db_recommendation:
                raise ValueError(f"Recommendation with id {recommendation.id} not found")
            
            db_recommendation.user_id = recommendation.user_id
            db_recommendation.item_ids = recommendation.item_ids
            db_recommendation.reasoning = recommendation.reasoning
            db_recommendation.confidence = recommendation.confidence
            db_recommendation.model_used = recommendation.model_used.value
            db_recommendation.provider = recommendation.provider.value
            db_recommendation.updated_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(db_recommendation)
            
            return AIRecommendation(
                id=db_recommendation.id,
                user_id=db_recommendation.user_id,
                item_ids=db_recommendation.item_ids,
                reasoning=db_recommendation.reasoning,
                confidence=db_recommendation.confidence,
                model_used=recommendation.model_used,
                provider=recommendation.provider,
                created_at=db_recommendation.created_at,
                updated_at=db_recommendation.updated_at
            )
    
    async def get_recommendation(self, recommendation_id: int) -> Optional[AIRecommendation]:
        """Get recommendation by ID"""
        db_recommendation = self.db.query(AIRecommendationModel).filter(
            AIRecommendationModel.id == recommendation_id
        ).first()
        if not db_recommendation:
            return None
        
        return AIRecommendation(
            id=db_recommendation.id,
            user_id=db_recommendation.user_id,
            item_ids=db_recommendation.item_ids,
            reasoning=db_recommendation.reasoning,
            confidence=db_recommendation.confidence,
            model_used=db_recommendation.model_used,
            provider=db_recommendation.provider,
            created_at=db_recommendation.created_at,
            updated_at=db_recommendation.updated_at
        )
    
    async def get_user_recommendations(self, user_id: str) -> List[AIRecommendation]:
        """Get user's recommendations"""
        db_recommendations = self.db.query(AIRecommendationModel).filter(
            AIRecommendationModel.user_id == user_id
        ).all()
        
        return [
            AIRecommendation(
                id=rec.id,
                user_id=rec.user_id,
                item_ids=rec.item_ids,
                reasoning=rec.reasoning,
                confidence=rec.confidence,
                model_used=rec.model_used,
                provider=rec.provider,
                created_at=rec.created_at,
                updated_at=rec.updated_at
            )
            for rec in db_recommendations
        ]
