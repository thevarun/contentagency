"""
Test suite for Pydantic models validation.
"""
import pytest
from pydantic import ValidationError

from contentagency.api.models import (
    InterestItem,
    UserInterestsRequest,
    PostItem,
    RecentPostsRequest,
    BrainstormRequest,
    BrainstormResult,
    BrainstormResponse,
    ErrorResponse,
    SuccessResponse,
    HealthResponse
)


class TestInterestItem:
    """Test InterestItem validation."""

    def test_valid_interest(self):
        """Should accept valid interest."""
        interest = InterestItem(topic="Artificial Intelligence")

        assert interest.topic == "Artificial Intelligence"

    def test_empty_topic_rejected(self):
        """Should reject empty topic."""
        with pytest.raises(ValidationError):
            InterestItem(topic="")

    def test_whitespace_topic_rejected(self):
        """Should reject whitespace-only topic."""
        with pytest.raises(ValidationError):
            InterestItem(topic="   ")

    def test_topic_stripped(self):
        """Should strip whitespace from topic."""
        interest = InterestItem(topic="  AI  ")

        assert interest.topic == "AI"


class TestUserInterestsRequest:
    """Test UserInterestsRequest validation."""

    def test_valid_request(self):
        """Should accept valid interests request."""
        request = UserInterestsRequest(
            user_id="test_user",
            interests=[
                InterestItem(topic="AI"),
                InterestItem(topic="ML")
            ]
        )

        assert request.user_id == "test_user"
        assert len(request.interests) == 2

    def test_empty_interests_rejected(self):
        """Should reject empty interests list."""
        with pytest.raises(ValidationError):
            UserInterestsRequest(
                user_id="test_user",
                interests=[]
            )

    def test_missing_user_id_rejected(self):
        """Should reject missing user_id."""
        with pytest.raises(ValidationError):
            UserInterestsRequest(interests=[InterestItem(topic="AI")])


class TestPostItem:
    """Test PostItem validation."""

    def test_valid_post(self):
        """Should accept valid post."""
        post = PostItem(
            id="post_1",
            platform="linkedin",
            content="Test content"
        )

        assert post.id == "post_1"
        assert post.platform == "linkedin"
        assert post.content == "Test content"

    def test_post_with_optional_fields(self):
        """Should accept optional fields."""
        post = PostItem(
            id="post_1",
            platform="twitter",
            content="Test",
            title="Title",
            topics=["AI", "ML"]
        )

        assert post.title == "Title"
        assert post.topics == ["AI", "ML"]

    def test_post_without_optional_fields(self):
        """Should handle missing optional fields."""
        post = PostItem(
            id="post_1",
            platform="linkedin",
            content="Test"
        )

        assert post.title is None
        assert post.topics == []

    def test_missing_required_fields_rejected(self):
        """Should reject missing required fields."""
        with pytest.raises(ValidationError):
            PostItem(platform="linkedin", content="Test")  # Missing id


class TestRecentPostsRequest:
    """Test RecentPostsRequest validation."""

    def test_valid_posts_request(self):
        """Should accept valid posts request."""
        request = RecentPostsRequest(
            user_id="test_user",
            posts=[
                PostItem(id="1", platform="linkedin", content="Content")
            ]
        )

        assert request.user_id == "test_user"
        assert len(request.posts) == 1

    def test_empty_posts_allowed(self):
        """Should allow empty posts list."""
        request = RecentPostsRequest(
            user_id="test_user",
            posts=[]
        )

        assert request.posts == []


class TestBrainstormRequest:
    """Test BrainstormRequest validation."""

    def test_minimal_request(self):
        """Should accept minimal request."""
        request = BrainstormRequest()

        assert request.user_id is None
        assert request.interests is None
        assert request.posts is None

    def test_request_with_user_id(self):
        """Should accept user_id."""
        request = BrainstormRequest(user_id="test_user")

        assert request.user_id == "test_user"

    def test_request_with_override_interests(self):
        """Should accept override interests."""
        request = BrainstormRequest(
            user_id="test_user",
            interests=UserInterestsRequest(
                user_id="test_user",
                interests=[InterestItem(topic="AI")]
            )
        )

        assert request.interests is not None
        assert len(request.interests.interests) == 1


class TestBrainstormResult:
    """Test BrainstormResult model."""

    def test_valid_result(self):
        """Should create valid result."""
        result = BrainstormResult(
            user_id="test_user",
            timestamp="2025-10-04T10:00:00",
            suggestions=[{
                "id": "suggestion_1",
                "title": "Test Topic",
                "description": "Test description",
                "platform_fit": ["LinkedIn"],
                "interest_alignment": "Aligns with AI",
                "trend_connection": "Current trend",
                "resource_links": [],
                "engagement_potential": "High",
                "engagement_reason": "Timely"
            }],
            trending_context_summary="Test summary"
        )

        assert result.user_id == "test_user"
        assert result.timestamp == "2025-10-04T10:00:00"
        assert len(result.suggestions) == 1
        assert result.suggestions[0].title == "Test Topic"


class TestBrainstormResponse:
    """Test BrainstormResponse model."""

    def test_success_response(self):
        """Should create success response."""
        response = BrainstormResponse(
            message="Success",
            result=BrainstormResult(
                user_id="test_user",
                timestamp="2025-10-04T10:00:00",
                suggestions=[],
                trending_context_summary="Summary"
            )
        )

        assert response.status == "success"
        assert response.message == "Success"
        assert response.result is not None

    def test_response_without_result(self):
        """Should allow None result."""
        response = BrainstormResponse(
            message="No results yet",
            result=None
        )

        assert response.result is None


class TestErrorResponse:
    """Test ErrorResponse model."""

    def test_error_response(self):
        """Should create error response."""
        response = ErrorResponse(
            message="An error occurred",
            detail="Additional details"
        )

        assert response.status == "error"
        assert response.message == "An error occurred"
        assert response.detail == "Additional details"

    def test_error_without_detail(self):
        """Should allow None detail."""
        response = ErrorResponse(message="Error")

        assert response.detail is None


class TestSuccessResponse:
    """Test SuccessResponse model."""

    def test_success_response(self):
        """Should create success response."""
        response = SuccessResponse(message="Operation successful")

        assert response.status == "success"
        assert response.message == "Operation successful"


class TestHealthResponse:
    """Test HealthResponse model."""

    def test_health_response(self):
        """Should create health response."""
        response = HealthResponse(version="v1")

        assert response.status == "healthy"
        assert response.version == "v1"
