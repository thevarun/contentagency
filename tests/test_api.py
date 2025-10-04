"""
Test suite for API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock

from contentagency.api.main import app
from contentagency.api.models import (
    UserInterestsRequest,
    RecentPostsRequest,
    BrainstormRequest,
)


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_data_service():
    """Mock data service."""
    with patch('contentagency.api.main.data_service') as mock:
        yield mock


@pytest.fixture
def mock_crew_runner():
    """Mock crew runner."""
    with patch('contentagency.api.main.run_brainstorm_crew') as mock:
        yield mock


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, client):
        """Should return healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestUpdateInterests:
    """Test update interests endpoint."""

    def test_update_interests_success(self, client, mock_data_service):
        """Should update interests successfully."""
        request_data = {
            "user_id": "test_user",
            "interests": [
                {"topic": "AI"},
                {"topic": "Machine Learning"}
            ]
        }

        response = client.post("/api/v1/interests", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "2 interests" in data["message"]
        assert mock_data_service.save_user_interests.called

    def test_update_interests_validation_error(self, client):
        """Should reject empty interests."""
        request_data = {
            "user_id": "test_user",
            "interests": []
        }

        response = client.post("/api/v1/interests", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_update_interests_empty_topic(self, client):
        """Should reject empty topic."""
        request_data = {
            "user_id": "test_user",
            "interests": [
                {"topic": ""}
            ]
        }

        response = client.post("/api/v1/interests", json=request_data)

        assert response.status_code == 422


class TestUpdatePosts:
    """Test update posts endpoint."""

    def test_update_posts_success(self, client, mock_data_service):
        """Should update posts successfully."""
        request_data = {
            "user_id": "test_user",
            "posts": [
                {
                    "id": "post_1",
                    "platform": "linkedin",
                    "content": "Test content"
                }
            ]
        }

        response = client.post("/api/v1/posts", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert mock_data_service.save_recent_posts.called

    def test_update_posts_with_optional_fields(self, client, mock_data_service):
        """Should handle optional fields."""
        request_data = {
            "user_id": "test_user",
            "posts": [
                {
                    "id": "post_1",
                    "platform": "twitter",
                    "content": "Short tweet",
                    "title": "Optional Title",
                    "topics": ["AI", "Tech"]
                }
            ]
        }

        response = client.post("/api/v1/posts", json=request_data)

        assert response.status_code == 200


class TestRunBrainstorm:
    """Test brainstorm endpoint."""

    def test_brainstorm_success(self, client, mock_data_service, mock_crew_runner):
        """Should run brainstorm successfully."""
        # Setup mocks
        mock_data_service.get_user_interests.return_value = {
            "user_id": "test_user",
            "interests": [{"topic": "AI"}]
        }
        mock_data_service.get_recent_posts.return_value = []
        mock_data_service.get_brainstorm_results.return_value = {
            "sessions": [{
                "user_id": "test_user",
                "timestamp": "2025-10-04T10:00:00",
                "suggestions": [{
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
                "trending_context_summary": "Test summary"
            }]
        }

        request_data = {"user_id": "test_user"}

        response = client.post("/api/v1/brainstorm", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["result"] is not None
        assert mock_crew_runner.called

    def test_brainstorm_with_override(self, client, mock_crew_runner, mock_data_service):
        """Should use override interests when provided."""
        mock_data_service.get_brainstorm_results.return_value = {"sessions": []}

        request_data = {
            "user_id": "test_user",
            "interests": {
                "user_id": "test_user",
                "interests": [{"topic": "Custom Topic"}]
            }
        }

        response = client.post("/api/v1/brainstorm", json=request_data)

        # Should call crew runner with override interests
        assert mock_crew_runner.called
        call_args = mock_crew_runner.call_args
        assert call_args.kwargs['user_id'] == "test_user"

    def test_brainstorm_validation_error(self, client, mock_crew_runner):
        """Should handle validation errors."""
        from contentagency.exceptions import ValidationError
        mock_crew_runner.side_effect = ValidationError("No interests provided")

        request_data = {"user_id": "test_user"}

        response = client.post("/api/v1/brainstorm", json=request_data)

        assert response.status_code == 400


class TestGetResults:
    """Test get results endpoint."""

    def test_get_results_success(self, client, mock_data_service):
        """Should return results successfully."""
        mock_data_service.get_brainstorm_results.return_value = {
            "sessions": [
                {
                    "user_id": "test_user",
                    "timestamp": "2025-10-04T10:00:00",
                    "suggested_topics": "Topics 1"
                },
                {
                    "user_id": "test_user",
                    "timestamp": "2025-10-04T11:00:00",
                    "suggested_topics": "Topics 2"
                }
            ]
        }

        response = client.get("/api/v1/results?limit=10")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["count"] == 2
        assert len(data["sessions"]) == 2

    def test_get_results_with_limit(self, client, mock_data_service):
        """Should respect limit parameter."""
        mock_data_service.get_brainstorm_results.return_value = {
            "sessions": [{"user_id": "test_user", "timestamp": f"2025-10-0{i}", "suggested_topics": f"Topics {i}"}
                        for i in range(1, 6)]
        }

        response = client.get("/api/v1/results?limit=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data["sessions"]) == 2  # Should only return last 2

    def test_get_results_empty(self, client, mock_data_service):
        """Should handle no results."""
        mock_data_service.get_brainstorm_results.return_value = {"sessions": []}

        response = client.get("/api/v1/results")

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["sessions"] == []
