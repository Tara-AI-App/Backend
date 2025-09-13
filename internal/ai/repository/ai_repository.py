from abc import ABC, abstractmethod
from typing import List, Optional
from internal.ai.model.ai_entity import AIConversation, AIAnalysis, AIRecommendation

class AIRepository(ABC):
    """Repository interface for AI entities"""
    
    @abstractmethod
    async def save_conversation(self, conversation: AIConversation) -> AIConversation:
        """Save AI conversation"""
        pass
    
    @abstractmethod
    async def get_conversation(self, conversation_id: int) -> Optional[AIConversation]:
        """Get conversation by ID"""
        pass
    
    @abstractmethod
    async def get_user_conversations(self, user_id: str, limit: int = 10) -> List[AIConversation]:
        """Get user's conversations"""
        pass
    
    @abstractmethod
    async def save_analysis(self, analysis: AIAnalysis) -> AIAnalysis:
        """Save AI analysis"""
        pass
    
    @abstractmethod
    async def get_analysis(self, analysis_id: int) -> Optional[AIAnalysis]:
        """Get analysis by ID"""
        pass
    
    @abstractmethod
    async def get_item_analyses(self, item_id: int) -> List[AIAnalysis]:
        """Get analyses for an item"""
        pass
    
    @abstractmethod
    async def save_recommendation(self, recommendation: AIRecommendation) -> AIRecommendation:
        """Save AI recommendation"""
        pass
    
    @abstractmethod
    async def get_recommendation(self, recommendation_id: int) -> Optional[AIRecommendation]:
        """Get recommendation by ID"""
        pass
    
    @abstractmethod
    async def get_user_recommendations(self, user_id: str) -> List[AIRecommendation]:
        """Get user's recommendations"""
        pass
