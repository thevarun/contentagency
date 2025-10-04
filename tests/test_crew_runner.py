"""
Test suite for crew_runner module.
Tests edge cases and validation logic.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from contentagency.services.crew_runner import (
    format_interests_for_prompt,
    format_posts_for_prompt,
    run_brainstorm_crew
)
from contentagency.exceptions import ValidationError


class TestFormatInterestsForPrompt:
    """Test formatting of user interests for prompts."""

    def test_empty_interests_dict(self):
        """Should return message when interests dict is empty."""
        result = format_interests_for_prompt({})
        assert result == "No specific interests provided."

    def test_missing_interests_key(self):
        """Should return message when 'interests' key is missing."""
        result = format_interests_for_prompt({"other_field": "value"})
        assert result == "No specific interests provided."

    def test_empty_interests_array(self):
        """Should handle empty interests array."""
        result = format_interests_for_prompt({"interests": []})
        assert "**User Interest Areas:**" in result

    def test_missing_topic_field(self):
        """Should use fallback when topic field is missing."""
        interests = {
            "interests": [
                {}  # No 'topic' field
            ]
        }
        result = format_interests_for_prompt(interests)
        assert "Untitled Topic" in result

    def test_valid_interests(self):
        """Should format valid interests correctly."""
        interests = {
            "interests": [
                {
                    "topic": "Artificial Intelligence"
                }
            ]
        }
        result = format_interests_for_prompt(interests)
        assert "**Artificial Intelligence**" in result


class TestFormatPostsForPrompt:
    """Test formatting of recent posts for prompts."""

    def test_empty_posts_array(self):
        """Should return message when posts array is empty."""
        result = format_posts_for_prompt([])
        assert result == "No recent posts available for analysis."

    def test_none_posts(self):
        """Should handle None posts."""
        result = format_posts_for_prompt(None)
        assert result == "No recent posts available for analysis."

    def test_missing_post_fields(self):
        """Should use fallback values for missing fields."""
        posts = [
            {}  # All fields missing
        ]
        result = format_posts_for_prompt(posts)
        assert "**Post ID unknown**" in result
        assert "(unknown)" in result

    def test_missing_optional_fields(self):
        """Should handle missing optional fields gracefully."""
        posts = [
            {
                "id": "post_001",
                "platform": "linkedin",
                "content": "Test content"
                # Missing 'title' and 'topics'
            }
        ]
        result = format_posts_for_prompt(posts)
        assert "post_001" in result
        assert "linkedin" in result
        assert "Test content" in result
        assert "Topics:" in result

    def test_long_content_truncation(self):
        """Should truncate long content."""
        posts = [
            {
                "id": "post_001",
                "platform": "linkedin",
                "content": "A" * 200,
                "topics": ["AI"]
            }
        ]
        result = format_posts_for_prompt(posts)
        assert "..." in result
        assert len(posts[0]["content"]) > 150

    def test_valid_posts(self):
        """Should format valid posts correctly."""
        posts = [
            {
                "id": "post_001",
                "platform": "linkedin",
                "title": "Test Post",
                "content": "Test content",
                "topics": ["AI", "ML"]
            }
        ]
        result = format_posts_for_prompt(posts)
        assert "Test Post" in result
        assert "Test content" in result
        assert "AI, ML" in result


class TestRunBrainstormCrew:
    """Test crew execution with validation."""

    def test_empty_interests_dict_raises_error(self):
        """Should raise ValidationError when interests dict is empty."""
        with pytest.raises(ValidationError) as exc_info:
            run_brainstorm_crew({}, [])
        assert "at least one user interest" in str(exc_info.value)

    def test_missing_interests_key_raises_error(self):
        """Should raise ValidationError when 'interests' key is missing."""
        with pytest.raises(ValidationError) as exc_info:
            run_brainstorm_crew({"other_field": "value"}, [])
        assert "at least one user interest" in str(exc_info.value)

    def test_empty_interests_array_raises_error(self):
        """Should raise ValidationError when interests array is empty."""
        with pytest.raises(ValidationError) as exc_info:
            run_brainstorm_crew({"interests": []}, [])
        assert "at least one user interest" in str(exc_info.value)

    def test_empty_posts_allowed(self):
        """Should work with empty posts (posts are optional)."""
        user_interests = {
            "interests": [
                {"topic": "AI"}
            ]
        }

        # Mock the crew execution
        with patch('contentagency.services.crew_runner.Contentagency') as MockCrew, \
             patch('contentagency.services.crew_runner.Crew') as MockCrewClass, \
             patch('contentagency.services.crew_runner.data_service') as mock_data_service:

            # Setup mocks
            mock_instance = Mock()
            MockCrew.return_value = mock_instance

            mock_crew = Mock()
            mock_crew.kickoff.return_value = "Test result"
            MockCrewClass.return_value = mock_crew

            # Run with empty posts
            result = run_brainstorm_crew(user_interests, [])

            # Should not raise error
            assert mock_crew.kickoff.called
            assert result == "Test result"

    @patch('contentagency.services.crew_runner.Contentagency')
    @patch('contentagency.services.crew_runner.Crew')
    @patch('contentagency.services.crew_runner.data_service')
    def test_valid_execution(self, mock_data_service, MockCrewClass, MockCrew):
        """Should execute successfully with valid data."""
        user_interests = {
            "interests": [
                {"topic": "AI"}
            ]
        }
        recent_posts = [
            {
                "id": "post_001",
                "platform": "linkedin",
                "content": "Test content",
                "topics": ["AI"]
            }
        ]

        # Setup mocks
        mock_instance = Mock()
        MockCrew.return_value = mock_instance

        mock_crew = Mock()
        mock_crew.kickoff.return_value = "Brainstorm result"
        MockCrewClass.return_value = mock_crew

        # Run the crew
        result = run_brainstorm_crew(user_interests, recent_posts)

        # Assertions
        assert result == "Brainstorm result"
        assert mock_crew.kickoff.called
        assert mock_data_service.save_brainstorm_results.called

        # Verify inputs were formatted correctly
        call_args = mock_crew.kickoff.call_args
        inputs = call_args.kwargs['inputs']
        assert 'user_interests' in inputs
        assert 'recent_posts' in inputs
        assert 'current_year' in inputs
        assert 'current_date' in inputs
        assert "**AI**" in inputs['user_interests']
        assert "post_001" in inputs['recent_posts']
