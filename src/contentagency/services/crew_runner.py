"""
Shared crew execution logic for both CLI and web UI.
Eliminates code duplication and provides a single source of truth.
"""
import re
from datetime import datetime
from typing import Dict, List, Any
from crewai import Crew, Process

from contentagency.crew import Contentagency
from contentagency.services.data_service import data_service
from contentagency.exceptions import ValidationError


def parse_brainstorm_markdown(markdown_text: str) -> Dict[str, Any]:
    """
    Parse LLM markdown output into structured format.

    Extracts numbered suggestions with their fields:
    - Topic Title
    - Description
    - Platform Fit
    - Interest Alignment
    - Trend Connection
    - Resource Links (with URLs and dates)
    - Engagement Potential

    Also extracts the Trending Context Summary at the end.

    Returns:
        Dict with 'suggestions' list and 'trending_context_summary'
    """
    suggestions = []

    # Split by numbered items (1., 2., 3., etc.)
    pattern = r'\n(\d+)\.\s+\*\*Topic Title\*\*:\s*["\u201c]([^"\u201d]+)["\u201d]'
    matches = list(re.finditer(pattern, markdown_text))

    for i, match in enumerate(matches):
        suggestion_num = match.group(1)
        title = match.group(2).strip()

        # Extract the text for this suggestion (until next number or end)
        start_pos = match.end()
        if i < len(matches) - 1:
            end_pos = matches[i + 1].start()
        else:
            # Find "Trending Context Summary" or end of text
            trending_match = re.search(r'\n#+\s*Trending Context', markdown_text[start_pos:])
            end_pos = start_pos + trending_match.start() if trending_match else len(markdown_text)

        suggestion_text = markdown_text[start_pos:end_pos]

        # Extract fields using regex
        description = _extract_field(suggestion_text, r'\*\*Description\*\*:\s*(.+?)(?=\n\s*-\s*\*\*|\n\n|\Z)', multiline=True)
        platform_fit = _extract_field(suggestion_text, r'\*\*Platform Fit\*\*:\s*(.+?)(?=\n\s*-\s*\*\*|\n\n|\Z)')
        interest_alignment = _extract_field(suggestion_text, r'\*\*Interest Alignment\*\*:\s*(.+?)(?=\n\s*-\s*\*\*|\n\n|\Z)')
        trend_connection = _extract_field(suggestion_text, r'\*\*Trend Connection\*\*:\s*(.+?)(?=\n\s*-\s*\*\*|\n\n|\Z)')
        engagement_potential = _extract_field(suggestion_text, r'\*\*Engagement Potential\*\*:\s*(\w+)')
        engagement_reason = _extract_field(suggestion_text, r'\*\*Engagement Potential\*\*:\s*\w+[,\s]+(?:due to|because|as|given|with)\s*(.+?)(?=\n\s*-\s*\*\*|\n\n|\Z)', multiline=True)

        # Extract resource links
        resource_links = _extract_resource_links(suggestion_text)

        # Parse platform_fit into list
        platforms = []
        if platform_fit:
            # Clean up and split by comma or "and"
            platform_fit = re.sub(r'\s*-\s*.*$', '', platform_fit)  # Remove explanations after dash
            platforms = [p.strip() for p in re.split(r',|\sand\s', platform_fit) if p.strip()]

        # Clean up engagement_reason
        if not engagement_reason and engagement_potential:
            # Try to extract the part after the potential
            potential_match = re.search(r'\*\*Engagement Potential\*\*:\s*\w+[,.]?\s*(.+?)(?=\n\s*-\s*\*\*|\n\n|\Z)', suggestion_text, re.DOTALL)
            if potential_match:
                engagement_reason = potential_match.group(1).strip()

        suggestions.append({
            "id": f"suggestion_{suggestion_num}",
            "title": title,
            "description": description or "",
            "platform_fit": platforms,
            "interest_alignment": interest_alignment or "",
            "trend_connection": trend_connection or "",
            "resource_links": resource_links,
            "engagement_potential": engagement_potential or "Moderate",
            "engagement_reason": engagement_reason or ""
        })

    # Extract trending context summary
    trending_summary = ""
    trending_match = re.search(r'#+\s*Trending Context[^\n]*\n(.+)', markdown_text, re.DOTALL)
    if trending_match:
        trending_summary = trending_match.group(1).strip()

    return {
        "suggestions": suggestions,
        "trending_context_summary": trending_summary
    }


def _extract_field(text: str, pattern: str, multiline: bool = False) -> str:
    """Extract a single field from text using regex."""
    flags = re.DOTALL if multiline else 0
    match = re.search(pattern, text, flags)
    if match:
        result = match.group(1).strip()
        # Clean up extra whitespace and newlines
        result = re.sub(r'\s+', ' ', result)
        return result
    return ""


def _extract_resource_links(text: str) -> List[Dict[str, str]]:
    """Extract resource links from text."""
    links = []

    # Pattern: [Title](URL) - Published: Date
    # or just [Title](URL)
    pattern = r'\[([^\]]+)\]\(([^)]+)\)(?:\s*-\s*Published:\s*([^)\n]+))?'

    for match in re.finditer(pattern, text):
        link_title = match.group(1).strip()
        url = match.group(2).strip()
        published_date = match.group(3).strip() if match.group(3) else None

        links.append({
            "title": link_title,
            "url": url,
            "published_date": published_date
        })

    return links


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


def run_brainstorm_crew(user_interests: Dict[str, Any], recent_posts: List[Dict[str, Any]], user_id: str = None) -> str:
    """
    Run the unified brainstorming crew with trend research and content generation.

    Args:
        user_interests: User interests dictionary
        recent_posts: List of recent posts with engagement data
        user_id: User identifier for saving results (optional, extracted from user_interests if not provided)

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

    # Extract user_id from user_interests if not provided
    if user_id is None:
        user_id = user_interests.get('user_id', 'default_user')

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

    # Parse markdown output into structured format
    structured_data = parse_brainstorm_markdown(str(result))

    # Save structured results using data service
    results_data = {
        "timestamp": datetime.now().isoformat(),
        "suggestions": structured_data["suggestions"],
        "trending_context_summary": structured_data.get("trending_context_summary", "")
    }

    data_service.save_brainstorm_results(user_id, results_data)

    return str(result)
