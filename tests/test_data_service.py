"""
Test suite for data service layer.
"""
import pytest
import json
import tempfile
from pathlib import Path

from contentagency.services.data_service import FileDataService, create_data_service


@pytest.fixture
def temp_data_dir():
    """Create temporary data directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def data_service(temp_data_dir):
    """Create FileDataService with temp directory."""
    return FileDataService(data_dir=temp_data_dir)


class TestFileDataService:
    """Test FileDataService class."""

    def test_get_user_interests_not_found(self, data_service):
        """Should return empty structure when file not found."""
        result = data_service.get_user_interests(user_id="test_user")

        assert result["user_id"] == "test_user"
        assert result["interests"] == []

    def test_get_user_interests_default_user(self, data_service):
        """Should use default_user when user_id not provided."""
        result = data_service.get_user_interests()

        assert result["user_id"] == "default_user"

    def test_save_and_get_user_interests(self, data_service):
        """Should save and retrieve user interests."""
        interests_data = {
            "user_id": "test_user",
            "interests": [
                {"topic": "AI"},
                {"topic": "ML"}
            ]
        }

        # Save
        data_service.save_user_interests(interests_data)

        # Retrieve
        result = data_service.get_user_interests()

        assert result["user_id"] == "test_user"
        assert len(result["interests"]) == 2
        assert result["interests"][0]["topic"] == "AI"

    def test_get_recent_posts_not_found(self, data_service):
        """Should return empty list when file not found."""
        result = data_service.get_recent_posts(user_id="test_user")

        assert result == []

    def test_save_and_get_recent_posts(self, data_service):
        """Should save and retrieve recent posts."""
        posts_data = {
            "user_id": "test_user",
            "posts": [
                {
                    "id": "post_1",
                    "platform": "linkedin",
                    "content": "Test content",
                    "published_date": "2025-10-04"
                },
                {
                    "id": "post_2",
                    "platform": "twitter",
                    "content": "Tweet content",
                    "published_date": "2025-10-03"
                }
            ]
        }

        # Save
        data_service.save_recent_posts(posts_data)

        # Retrieve
        result = data_service.get_recent_posts(user_id="test_user")

        assert len(result) == 2
        # Should be sorted by date (most recent first)
        assert result[0]["id"] == "post_1"

    def test_get_recent_posts_with_limit(self, data_service):
        """Should respect limit parameter."""
        posts_data = {
            "user_id": "test_user",
            "posts": [
                {"id": f"post_{i}", "platform": "linkedin", "content": f"Content {i}", "published_date": f"2025-10-0{i}"}
                for i in range(1, 6)
            ]
        }

        data_service.save_recent_posts(posts_data)

        result = data_service.get_recent_posts(user_id="test_user", limit=2)

        assert len(result) == 2

    def test_get_brainstorm_results_empty(self, data_service):
        """Should return empty sessions when file not found."""
        result = data_service.get_brainstorm_results()

        assert result == {"sessions": []}

    def test_save_and_get_brainstorm_results(self, data_service):
        """Should save and retrieve brainstorm results."""
        results_data = {
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
        }

        # Save
        data_service.save_brainstorm_results("test_user", results_data)

        # Retrieve all
        result = data_service.get_brainstorm_results()

        assert len(result["sessions"]) == 1
        assert result["sessions"][0]["user_id"] == "test_user"
        assert len(result["sessions"][0]["suggestions"]) == 1
        assert result["sessions"][0]["suggestions"][0]["title"] == "Test Topic"

    def test_get_brainstorm_results_filtered_by_user(self, data_service):
        """Should filter results by user_id."""
        # Save results for multiple users
        data_service.save_brainstorm_results("user_1", {
            "timestamp": "2025-10-04T10:00:00",
            "suggestions": [],
            "trending_context_summary": "User 1 summary"
        })
        data_service.save_brainstorm_results("user_2", {
            "timestamp": "2025-10-04T11:00:00",
            "suggestions": [],
            "trending_context_summary": "User 2 summary"
        })

        # Get filtered results
        result = data_service.get_brainstorm_results(user_id="user_1")

        assert len(result["sessions"]) == 1
        assert result["sessions"][0]["user_id"] == "user_1"

    def test_multiple_brainstorm_sessions(self, data_service):
        """Should append multiple sessions."""
        # Save first session
        data_service.save_brainstorm_results("test_user", {
            "timestamp": "2025-10-04T10:00:00",
            "suggestions": [],
            "trending_context_summary": "Summary 1"
        })

        # Save second session
        data_service.save_brainstorm_results("test_user", {
            "timestamp": "2025-10-04T11:00:00",
            "suggestions": [],
            "trending_context_summary": "Summary 2"
        })

        result = data_service.get_brainstorm_results(user_id="test_user")

        assert len(result["sessions"]) == 2

    def test_invalid_json_format(self, data_service, temp_data_dir):
        """Should raise error for invalid JSON."""
        # Write invalid JSON
        interests_file = Path(temp_data_dir) / "user_interests.json"
        with open(interests_file, 'w') as f:
            f.write("invalid json{")

        with pytest.raises(ValueError, match="Invalid JSON format"):
            data_service.get_user_interests()


class TestCreateDataService:
    """Test data service factory."""

    def test_create_file_service(self):
        """Should create file service."""
        service = create_data_service("file")

        assert isinstance(service, FileDataService)

    def test_create_database_service(self):
        """Should create database service."""
        service = create_data_service("database", connection_string="test")

        from contentagency.services.data_service import DatabaseDataService
        assert isinstance(service, DatabaseDataService)

    def test_create_invalid_service(self):
        """Should raise error for invalid service type."""
        with pytest.raises(ValueError, match="Unknown service type"):
            create_data_service("invalid")
