"""
Data service layer for accessing user data and content.
Designed to be migration-friendly for future database integration.
"""

import json
import os
from typing import Dict, List, Any, Protocol
from abc import ABC, abstractmethod
from pathlib import Path


class DataServiceProtocol(Protocol):
    """Protocol defining the interface for data services."""

    def get_user_interests(self, user_id: str) -> Dict[str, Any]:
        """Get user interests and preferences."""
        ...

    def get_recent_posts(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent posts by user."""
        ...

    def get_brainstorm_results(self, user_id: str) -> Dict[str, Any]:
        """Get brainstorming session results."""
        ...

    def save_brainstorm_results(self, user_id: str, results: Dict[str, Any]) -> None:
        """Save brainstorming session results."""
        ...


class FileDataService:
    """File-based data service for development. Easily replaceable with database service."""

    def __init__(self, data_dir: str = None):
        if data_dir is None:
            # Default to project root/data directory
            project_root = Path(__file__).parent.parent.parent.parent
            self.data_dir = project_root / "data"
        else:
            self.data_dir = Path(data_dir)

        self.data_dir.mkdir(exist_ok=True)

    def get_user_interests(self, user_id: str = "user_001") -> Dict[str, Any]:
        """Load user interests from JSON file."""
        try:
            interests_file = self.data_dir / "user_interests.json"
            with open(interests_file, 'r') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            return {"user_id": user_id, "interests": [], "platforms": [], "posting_frequency": {}}
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format in user interests file")

    def save_user_interests(self, data: Dict[str, Any]) -> None:
        """Save user interests to JSON file."""
        try:
            interests_file = self.data_dir / "user_interests.json"
            with open(interests_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            raise ValueError(f"Failed to save user interests: {str(e)}")

    def get_recent_posts(self, user_id: str = "user_001", limit: int = 10) -> List[Dict[str, Any]]:
        """Load recent posts from JSON file."""
        try:
            posts_file = self.data_dir / "recent_posts.json"
            with open(posts_file, 'r') as f:
                data = json.load(f)

            # Filter by user_id and limit results
            posts = data.get("posts", [])
            filtered_posts = [post for post in posts if data.get("user_id") == user_id]

            # Sort by published_date (most recent first) and limit
            sorted_posts = sorted(filtered_posts,
                                key=lambda x: x.get("published_date", ""),
                                reverse=True)

            return sorted_posts[:limit]
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format in recent posts file")

    def save_recent_posts(self, data: Dict[str, Any]) -> None:
        """Save recent posts to JSON file."""
        try:
            posts_file = self.data_dir / "recent_posts.json"
            with open(posts_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            raise ValueError(f"Failed to save recent posts: {str(e)}")

    def get_brainstorm_results(self, user_id: str = "user_001") -> Dict[str, Any]:
        """Load brainstorming results from JSON file."""
        try:
            results_file = self.data_dir / "brainstorm_results.json"
            if results_file.exists():
                with open(results_file, 'r') as f:
                    return json.load(f)
            return {"sessions": []}
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format in brainstorm results file")

    def save_brainstorm_results(self, user_id: str, results: Dict[str, Any]) -> None:
        """Save brainstorming results to JSON file."""
        try:
            results_file = self.data_dir / "brainstorm_results.json"

            # Load existing results or create new structure
            if results_file.exists():
                with open(results_file, 'r') as f:
                    all_results = json.load(f)
            else:
                all_results = {"sessions": []}

            # Add new session
            session = {
                "user_id": user_id,
                "timestamp": results.get("timestamp"),
                "suggested_topics": results.get("suggested_topics", "")
            }

            all_results["sessions"].append(session)

            # Save updated results
            with open(results_file, 'w') as f:
                json.dump(all_results, f, indent=2)

        except Exception as e:
            raise ValueError(f"Failed to save brainstorm results: {str(e)}")


class DatabaseDataService:
    """Future database-based data service. Placeholder for cloud migration."""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        # TODO: Initialize database connection
        pass

    def get_user_interests(self, user_id: str) -> Dict[str, Any]:
        # TODO: Implement database query
        raise NotImplementedError("Database service not yet implemented")

    def get_recent_posts(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        # TODO: Implement database query
        raise NotImplementedError("Database service not yet implemented")

    def save_brainstorm_results(self, user_id: str, results: Dict[str, Any]) -> None:
        # TODO: Implement database insert
        raise NotImplementedError("Database service not yet implemented")


# Factory function for creating data service instances
def create_data_service(service_type: str = "file", **kwargs) -> DataServiceProtocol:
    """
    Factory function to create data service instances.
    Makes it easy to switch between file and database implementations.
    """
    if service_type == "file":
        return FileDataService(kwargs.get("data_dir"))
    elif service_type == "database":
        return DatabaseDataService(kwargs.get("connection_string"))
    else:
        raise ValueError(f"Unknown service type: {service_type}")


# Default instance for the application
data_service = create_data_service("file")