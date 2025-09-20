from fastapi import APIRouter, HTTPException, status, Query, Request, Depends
from typing import List, Optional
from internal.ai.model.ai_dto import (
    ChatRequest, ChatResponse,
    AIAnalysisRequest, AIAnalysisResponse,
    AIRecommendationRequest, AIRecommendationResponse
)
from internal.ai.service.ai_use_cases import AIUseCases
from internal.ai.service.ai_service import OpenAIService, LocalLLMService
from internal.ai.repository.ai_repository_impl import InMemoryAIRepository
from internal.auth.middleware import get_current_user_id

# Create router
router = APIRouter(prefix="/ai", tags=["ai"])

# Dependency injection
ai_repository = InMemoryAIRepository()
# TODO: Configure AI service based on environment
ai_service = OpenAIService(api_key="your-api-key-here")  # Placeholder
ai_use_cases = AIUseCases(ai_service, ai_repository)

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest, user_id: str = Depends(get_current_user_id)):
    """Chat with AI assistant"""
    try:
        return await ai_use_cases.chat_with_ai(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in AI chat: {str(e)}"
        )

@router.post("/analyze", response_model=AIAnalysisResponse)
async def analyze_item(request: AIAnalysisRequest, user_id: str = Depends(get_current_user_id)):
    """Analyze an item using AI"""
    try:
        return await ai_use_cases.analyze_item_with_ai(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in AI analysis: {str(e)}"
        )

@router.post("/recommendations", response_model=AIRecommendationResponse)
async def get_recommendations(request: AIRecommendationRequest, user_id: str = Depends(get_current_user_id)):
    """Get AI-powered item recommendations"""
    try:
        return await ai_use_cases.get_item_recommendations(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recommendations: {str(e)}"
        )

@router.post("/enhance-description/{item_id}")
async def enhance_description(item_id: int, current_description: str = Query(...), user_id: str = Depends(get_current_user_id)):
    """Enhance item description using AI"""
    try:
        enhanced = await ai_use_cases.enhance_item_description(item_id, current_description)
        return {"item_id": item_id, "enhanced_description": enhanced}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error enhancing description: {str(e)}"
        )

@router.post("/analyze-pricing/{item_id}")
async def analyze_pricing(item_id: int, current_price: float = Query(...), user_id: str = Depends(get_current_user_id)):
    """Analyze item pricing using AI"""
    try:
        analysis = await ai_use_cases.analyze_item_pricing(item_id, current_price)
        return {"item_id": item_id, "pricing_analysis": analysis}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing pricing: {str(e)}"
        )

@router.get("/conversations/{user_id}")
async def get_conversation_history(user_id: str, limit: int = Query(10, ge=1, le=100), current_user_id: str = Depends(get_current_user_id)):
    """Get user's conversation history"""
    try:
        conversations = await ai_use_cases.get_conversation_history(user_id, limit)
        return {"user_id": user_id, "conversations": conversations}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving conversations: {str(e)}"
        )

@router.get("/analyses/{item_id}")
async def get_item_analyses(item_id: int, user_id: str = Depends(get_current_user_id)):
    """Get AI analyses for an item"""
    try:
        analyses = await ai_use_cases.get_analysis_history(item_id)
        return {"item_id": item_id, "analyses": analyses}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving analyses: {str(e)}"
        )

@router.get("/recommendations/{user_id}")
async def get_recommendation_history(user_id: str, current_user_id: str = Depends(get_current_user_id)):
    """Get user's recommendation history"""
    try:
        recommendations = await ai_use_cases.get_recommendation_history(user_id)
        return {"user_id": user_id, "recommendations": recommendations}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving recommendations: {str(e)}"
        )
