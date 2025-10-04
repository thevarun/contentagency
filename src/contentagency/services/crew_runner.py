"""
Shared crew execution logic for both CLI and web UI.
Eliminates code duplication and provides a single source of truth.
"""
from datetime import datetime
from typing import Dict, List, Any
from crewai import Crew, Process

from contentagency.crew import Contentagency
from contentagency.services.data_service import data_service
from contentagency.exceptions import ValidationError


def format_interests_for_prompt(user_interests: dict) -> str:
    """Format user interests for the prompt."""
    if not user_interests or 'interests' not in user_interests:
        return "No specific interests provided."

    formatted = "**User Interest Areas:**\n"
    for interest in user_interests['interests']:
        # Handle missing 'topic' field safely
        topic = interest.get('topic', 'Untitled Topic')
        formatted += f"- **{topic}**\n"

    return formatted


def format_posts_for_prompt(recent_posts: list) -> str:
    """Format recent posts for the prompt."""
    if not recent_posts:
        return "No recent posts available for analysis."

    formatted = "**Recent Post Performance:**\n"
    for post in recent_posts:
        # Handle missing required fields safely
        post_id = post.get('id', 'unknown')
        platform = post.get('platform', 'unknown')
        content = post.get('content', '')

        formatted += f"\n**Post ID {post_id}** ({platform})\n"
        if post.get('title'):
            formatted += f"Title: {post['title']}\n"
        formatted += f"Content: {content[:150]}{'...' if len(content) > 150 else ''}\n"
        formatted += f"Topics: {', '.join(post.get('topics', []))}\n"

    return formatted


def run_brainstorm_crew(user_interests: Dict[str, Any], recent_posts: List[Dict[str, Any]]) -> str:
    """
    Run the unified brainstorming crew with trend research and content generation.

    Args:
        user_interests: User interests dictionary
        recent_posts: List of recent posts with engagement data

    Returns:
        The crew result as a string

    Raises:
        ValidationError: If user_interests is empty or invalid
    """
    # Validate user interests
    if not user_interests or 'interests' not in user_interests:
        raise ValidationError("Please add at least one user interest before running the crew")

    interests_list = user_interests.get('interests', [])
    if not interests_list or len(interests_list) == 0:
        raise ValidationError("Please add at least one user interest before running the crew")

    # Format the data for the tasks
    interests_summary = format_interests_for_prompt(user_interests)
    posts_summary = format_posts_for_prompt(recent_posts)

    # Create crew instance
    crew_instance = Contentagency()

    # Input data for the crew
    current_datetime = datetime.now()
    inputs = {
        'user_interests': interests_summary,
        'recent_posts': posts_summary,
        'current_year': str(current_datetime.year),
        'current_date': current_datetime.strftime("%B %d, %Y")
    }

    # Create unified crew with both agents and tasks
    # Tasks will execute sequentially: trend_research_task -> brainstorming_task
    unified_crew = Crew(
        agents=[
            crew_instance.trend_researcher(),
            crew_instance.brainstorming_strategist()
        ],
        tasks=[
            crew_instance.trend_research_task(),
            crew_instance.brainstorming_task()
        ],
        process=Process.sequential,
        verbose=True
    )

    # Run the crew
    result = unified_crew.kickoff(inputs=inputs)

    # Save results using data service
    results_data = {
        "timestamp": datetime.now().isoformat(),
        "suggested_topics": str(result)
    }

    data_service.save_brainstorm_results("user_001", results_data)

    return str(result)
