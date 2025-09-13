from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

class AIProvider(str, Enum):
    """AI provider types"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"

class AIModelType(str, Enum):
    """AI model types"""
    OPENAI_GPT4 = "openai_gpt4"
    OPENAI_GPT35 = "openai_gpt35"
    ANTHROPIC_CLAUDE = "anthropic_claude"
    LOCAL_LLM = "local_llm"

@dataclass
class AIConversation:
    """AI conversation entity"""
    id: Optional[int]
    user_id: Optional[str]
    title: str
    messages: list[Dict[str, str]]
    model_used: AIModelType
    provider: AIProvider
    created_at: datetime
    updated_at: datetime
    is_active: bool = True

@dataclass
class AIAnalysis:
    """AI analysis entity"""
    id: Optional[int]
    item_id: int
    analysis_type: str
    result: Dict[str, Any]
    confidence: float
    model_used: AIModelType
    provider: AIProvider
    created_at: datetime
    updated_at: datetime

@dataclass
class AIRecommendation:
    """AI recommendation entity"""
    id: Optional[int]
    user_id: Optional[str]
    item_ids: list[int]
    reasoning: str
    confidence: float
    model_used: AIModelType
    provider: AIProvider
    created_at: datetime
    updated_at: datetime
