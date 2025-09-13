from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum

class AIModelType(str, Enum):
    """Supported AI model types"""
    OPENAI_GPT4 = "openai_gpt4"
    OPENAI_GPT35 = "openai_gpt35"
    ANTHROPIC_CLAUDE = "anthropic_claude"
    LOCAL_LLM = "local_llm"

class AIProvider(str, Enum):
    """Supported AI providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"

class ChatMessage(BaseModel):
    """Individual chat message"""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    """Chat completion request"""
    messages: List[ChatMessage]
    model: AIModelType = AIModelType.OPENAI_GPT35
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False

class ChatResponse(BaseModel):
    """Chat completion response"""
    id: str
    message: ChatMessage
    usage: Optional[Dict[str, int]] = None
    model: str
    created_at: str

class AIAnalysisRequest(BaseModel):
    """AI analysis request for items"""
    item_id: int
    analysis_type: str  # "price_analysis", "description_enhancement", "recommendation"
    context: Optional[Dict[str, Any]] = None

class AIAnalysisResponse(BaseModel):
    """AI analysis response"""
    item_id: int
    analysis_type: str
    result: Dict[str, Any]
    confidence: float
    created_at: str

class AIRecommendationRequest(BaseModel):
    """AI recommendation request"""
    user_preferences: Dict[str, Any]
    item_filters: Optional[Dict[str, Any]] = None
    limit: int = 10

class AIRecommendationResponse(BaseModel):
    """AI recommendation response"""
    recommendations: List[Dict[str, Any]]
    reasoning: str
    confidence: float
    created_at: str
