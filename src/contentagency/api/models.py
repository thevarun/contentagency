"""
Pydantic models for API request/response validation.
"""
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class InterestItem(BaseModel):
    """Single interest item."""
    topic: str = Field(..., min_length=1, description="Interest topic")

    @field_validator('topic')
    @classmethod
    def topic_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Topic cannot be empty or whitespace')
        return v.strip()


class UserInterestsRequest(BaseModel):
    """Request model for updating user interests."""
    user_id: str = Field(..., min_length=1, description="User identifier")
    interests: List[InterestItem] = Field(..., min_length=1, description="List of user interests")

    @field_validator('interests')
    @classmethod
    def interests_not_empty(cls, v: List[InterestItem]) -> List[InterestItem]:
        if not v:
            raise ValueError('At least one interest is required')
        return v


class PostItem(BaseModel):
    """Single post item."""
    id: str = Field(..., description="Post identifier")
    platform: str = Field(..., description="Platform name (e.g., linkedin, twitter)")
    content: str = Field(..., description="Post content")
    title: Optional[str] = Field(None, description="Post title (optional)")
    topics: Optional[List[str]] = Field(default_factory=list, description="Post topics")


class RecentPostsRequest(BaseModel):
    """Request model for updating recent posts."""
    user_id: str = Field(..., min_length=1, description="User identifier")
    posts: List[PostItem] = Field(..., description="List of recent posts")


class BrainstormRequest(BaseModel):
    """Request model for running brainstorm crew."""
    user_id: Optional[str] = Field(None, description="User identifier (optional, uses default if not provided)")
    interests: Optional[UserInterestsRequest] = Field(None, description="Override user interests for this session")
    posts: Optional[RecentPostsRequest] = Field(None, description="Override recent posts for this session")


class ResourceLink(BaseModel):
    """Resource link with metadata."""
    title: str = Field(..., description="Resource title")
    url: str = Field(..., description="Resource URL")
    published_date: Optional[str] = Field(None, description="Publication date")


class ContentSuggestion(BaseModel):
    """Individual content suggestion."""
    id: str = Field(..., description="Unique suggestion identifier")
    title: str = Field(..., description="Suggestion title")
    description: str = Field(..., description="Detailed description")
    platform_fit: List[str] = Field(..., description="Recommended platforms")
    interest_alignment: str = Field(..., description="How it aligns with user interests")
    trend_connection: str = Field(..., description="Connection to current trends")
    resource_links: List[ResourceLink] = Field(default_factory=list, description="Related resources")
    engagement_potential: str = Field(..., description="Expected engagement level (High/Moderate/Low)")
    engagement_reason: str = Field(..., description="Why this will engage the audience")


class BrainstormResult(BaseModel):
    """Structured brainstorm session result."""
    user_id: str
    timestamp: str
    suggestions: List[ContentSuggestion] = Field(..., description="List of content suggestions")
    trending_context_summary: Optional[str] = Field(None, description="Summary of trending context")


class BrainstormResponse(BaseModel):
    """Response model for successful brainstorm execution."""
    status: str = Field(default="success", description="Operation status")
    message: str = Field(..., description="Human-readable message")
    result: Optional[BrainstormResult] = Field(None, description="Brainstorm result")


class ErrorResponse(BaseModel):
    """Standardized error response."""
    status: str = Field(default="error", description="Operation status")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")


class SuccessResponse(BaseModel):
    """Generic success response."""
    status: str = Field(default="success", description="Operation status")
    message: str = Field(..., description="Success message")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(default="healthy", description="Service health status")
    version: str = Field(..., description="API version")
