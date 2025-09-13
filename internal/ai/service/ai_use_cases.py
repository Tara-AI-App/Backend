from typing import List, Optional
from internal.ai.model.ai_dto import (
    ChatRequest, ChatResponse,
    AIAnalysisRequest, AIAnalysisResponse,
    AIRecommendationRequest, AIRecommendationResponse
)
from internal.ai.service.ai_service import AIService
from internal.ai.repository.ai_repository import AIRepository

class AIUseCases:
    """AI use cases for business logic"""
    
    def __init__(self, ai_service: AIService, ai_repository: AIRepository):
        self.ai_service = ai_service
        self.ai_repository = ai_repository
    
    async def chat_with_ai(self, request: ChatRequest) -> ChatResponse:
        """Chat with AI and save conversation"""
        # Generate AI response
        response = await self.ai_service.chat_completion(request)
        
        # Save conversation to repository
        # TODO: Implement conversation saving
        
        return response
    
    async def analyze_item_with_ai(self, request: AIAnalysisRequest) -> AIAnalysisResponse:
        """Analyze item using AI and save analysis"""
        # Generate AI analysis
        response = await self.ai_service.analyze_item(request)
        
        # Save analysis to repository
        # TODO: Implement analysis saving
        
        return response
    
    async def get_item_recommendations(self, request: AIRecommendationRequest) -> AIRecommendationResponse:
        """Get AI-powered item recommendations"""
        # Generate recommendations
        response = await self.ai_service.generate_recommendations(request)
        
        # Save recommendation to repository
        # TODO: Implement recommendation saving
        
        return response
    
    async def enhance_item_description(self, item_id: int, current_description: str) -> str:
        """Enhance item description using AI"""
        enhanced_description = await self.ai_service.enhance_description(item_id, current_description)
        
        # Save enhanced description
        # TODO: Implement description saving
        
        return enhanced_description
    
    async def analyze_item_pricing(self, item_id: int, current_price: float) -> dict:
        """Analyze item pricing using AI"""
        analysis = await self.ai_service.price_analysis(item_id, current_price)
        
        # Save pricing analysis
        # TODO: Implement pricing analysis saving
        
        return analysis
    
    async def get_conversation_history(self, user_id: str, limit: int = 10) -> List[dict]:
        """Get user's conversation history"""
        # TODO: Implement conversation history retrieval
        return []
    
    async def get_analysis_history(self, item_id: int) -> List[dict]:
        """Get item's analysis history"""
        # TODO: Implement analysis history retrieval
        return []
    
    async def get_recommendation_history(self, user_id: str) -> List[dict]:
        """Get user's recommendation history"""
        # TODO: Implement recommendation history retrieval
        return []
