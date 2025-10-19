from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

@dataclass
class AiGuideGenerateRequest:
    """Request model for AI guide generation"""
    token_github: str
    token_drive: str
    prompt: str
    files_url: Optional[str] = None
    cv: Optional[str] = None

@dataclass
class ExternalAiGuideGenerateResponse:
    """Response model from external API"""
    title: str
    description: str
    content: str
    source_from: List[str]

@dataclass
class AiGuideGenerateResponse:
    """Response model for AI guide generation"""
    guide_id: UUID
    external_response: Optional[ExternalAiGuideGenerateResponse] = None

@dataclass
class GuideListItem:
    """Guide list item model"""
    id: UUID
    title: str
    description: Optional[str]
    content: str
    source_from: Optional[List[str]]
    created_at: str
    updated_at: str

@dataclass
class GuideListResponse:
    """Response model for guide list"""
    guides: List[GuideListItem]
    total: int

@dataclass
class GuideDetailResponse:
    """Response model for guide detail"""
    id: UUID
    title: str
    description: Optional[str]
    content: str
    source_from: Optional[List[str]]
    created_at: str
    updated_at: str
