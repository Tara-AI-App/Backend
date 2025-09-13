from typing import List, Optional
from datetime import datetime
from internal.ai.model.ai_entity import AIConversation, AIAnalysis, AIRecommendation
from internal.ai.repository.ai_repository import AIRepository

class InMemoryAIRepository(AIRepository):
    """In-memory implementation of AI repository"""
    
    def __init__(self):
        self._conversations: List[AIConversation] = []
        self._analyses: List[AIAnalysis] = []
        self._recommendations: List[AIRecommendation] = []
        self._conversation_id_counter = 1
        self._analysis_id_counter = 1
        self._recommendation_id_counter = 1
    
    async def save_conversation(self, conversation: AIConversation) -> AIConversation:
        """Save AI conversation"""
        if conversation.id is None:
            new_conversation = AIConversation(
                id=self._conversation_id_counter,
                user_id=conversation.user_id,
                title=conversation.title,
                messages=conversation.messages,
                model_used=conversation.model_used,
                provider=conversation.provider,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                is_active=conversation.is_active
            )
            self._conversations.append(new_conversation)
            self._conversation_id_counter += 1
            return new_conversation
        else:
            # Update existing conversation
            for i, existing in enumerate(self._conversations):
                if existing.id == conversation.id:
                    updated_conversation = AIConversation(
                        id=conversation.id,
                        user_id=conversation.user_id,
                        title=conversation.title,
                        messages=conversation.messages,
                        model_used=conversation.model_used,
                        provider=conversation.provider,
                        created_at=existing.created_at,
                        updated_at=datetime.now(),
                        is_active=conversation.is_active
                    )
                    self._conversations[i] = updated_conversation
                    return updated_conversation
            raise ValueError(f"Conversation with id {conversation.id} not found")
    
    async def get_conversation(self, conversation_id: int) -> Optional[AIConversation]:
        """Get conversation by ID"""
        for conversation in self._conversations:
            if conversation.id == conversation_id:
                return conversation
        return None
    
    async def get_user_conversations(self, user_id: str, limit: int = 10) -> List[AIConversation]:
        """Get user's conversations"""
        user_conversations = [
            conv for conv in self._conversations 
            if conv.user_id == user_id and conv.is_active
        ]
        return user_conversations[:limit]
    
    async def save_analysis(self, analysis: AIAnalysis) -> AIAnalysis:
        """Save AI analysis"""
        if analysis.id is None:
            new_analysis = AIAnalysis(
                id=self._analysis_id_counter,
                item_id=analysis.item_id,
                analysis_type=analysis.analysis_type,
                result=analysis.result,
                confidence=analysis.confidence,
                model_used=analysis.model_used,
                provider=analysis.provider,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            self._analyses.append(new_analysis)
            self._analysis_id_counter += 1
            return new_analysis
        else:
            # Update existing analysis
            for i, existing in enumerate(self._analyses):
                if existing.id == analysis.id:
                    updated_analysis = AIAnalysis(
                        id=analysis.id,
                        item_id=analysis.item_id,
                        analysis_type=analysis.analysis_type,
                        result=analysis.result,
                        confidence=analysis.confidence,
                        model_used=analysis.model_used,
                        provider=analysis.provider,
                        created_at=existing.created_at,
                        updated_at=datetime.now()
                    )
                    self._analyses[i] = updated_analysis
                    return updated_analysis
            raise ValueError(f"Analysis with id {analysis.id} not found")
    
    async def get_analysis(self, analysis_id: int) -> Optional[AIAnalysis]:
        """Get analysis by ID"""
        for analysis in self._analyses:
            if analysis.id == analysis_id:
                return analysis
        return None
    
    async def get_item_analyses(self, item_id: int) -> List[AIAnalysis]:
        """Get analyses for an item"""
        return [analysis for analysis in self._analyses if analysis.item_id == item_id]
    
    async def save_recommendation(self, recommendation: AIRecommendation) -> AIRecommendation:
        """Save AI recommendation"""
        if recommendation.id is None:
            new_recommendation = AIRecommendation(
                id=self._recommendation_id_counter,
                user_id=recommendation.user_id,
                item_ids=recommendation.item_ids,
                reasoning=recommendation.reasoning,
                confidence=recommendation.confidence,
                model_used=recommendation.model_used,
                provider=recommendation.provider,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            self._recommendations.append(new_recommendation)
            self._recommendation_id_counter += 1
            return new_recommendation
        else:
            # Update existing recommendation
            for i, existing in enumerate(self._recommendations):
                if existing.id == recommendation.id:
                    updated_recommendation = AIRecommendation(
                        id=recommendation.id,
                        user_id=recommendation.user_id,
                        item_ids=recommendation.item_ids,
                        reasoning=recommendation.reasoning,
                        confidence=recommendation.confidence,
                        model_used=recommendation.model_used,
                        provider=recommendation.provider,
                        created_at=existing.created_at,
                        updated_at=datetime.now()
                    )
                    self._recommendations[i] = updated_recommendation
                    return updated_recommendation
            raise ValueError(f"Recommendation with id {recommendation.id} not found")
    
    async def get_recommendation(self, recommendation_id: int) -> Optional[AIRecommendation]:
        """Get recommendation by ID"""
        for recommendation in self._recommendations:
            if recommendation.id == recommendation_id:
                return recommendation
        return None
    
    async def get_user_recommendations(self, user_id: str) -> List[AIRecommendation]:
        """Get user's recommendations"""
        return [rec for rec in self._recommendations if rec.user_id == user_id]
