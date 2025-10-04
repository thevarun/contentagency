#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from contentagency.crew import Contentagency
from contentagency.services.data_service import data_service
from contentagency.services.crew_runner import run_brainstorm_crew
from contentagency.exceptions import ValidationError

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    inputs = {
        'topic': 'AI LLMs',
        'current_year': str(datetime.now().year)
    }

    try:
        Contentagency().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def brainstorm():
    """
    Run the unified brainstorming crew with trend research and content generation.
    CLI-specific wrapper around shared crew runner logic.
    """
    try:
        # Load user data using the data service
        user_interests = data_service.get_user_interests()
        recent_posts = data_service.get_recent_posts(limit=5)

        print("🧠 Starting unified brainstorming crew...")
        print(f"📊 Analyzing {len(user_interests.get('interests', []))} interest areas")
        print(f"📈 Reviewing {len(recent_posts)} recent posts")
        print("🔍 Crew will perform trend research followed by content brainstorming")
        print("\n🚀 Starting collaborative crew execution...")

        # Run the shared crew logic
        result = run_brainstorm_crew(user_interests, recent_posts)

        print("\n✅ Unified brainstorming crew complete! Results saved to brainstorm_suggestions.md")
        print("📊 Trend research was incorporated into the collaborative workflow")

        return result

    except ValidationError as e:
        print(f"\n❌ Validation Error: {str(e)}")
        print("💡 Tip: Add user interests in data/user_interests.json and try again.")
        sys.exit(1)
    except Exception as e:
        raise Exception(f"An error occurred while running brainstorming: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }
    try:
        Contentagency().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Contentagency().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }

    try:
        Contentagency().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "brainstorm":
        brainstorm()
    else:
        run()
