#!/usr/bin/env python
"""
Simple web UI for testing the research agent locally.
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from pathlib import Path

from contentagency.services.data_service import data_service
from contentagency.services.crew_runner import run_brainstorm_crew
from contentagency.exceptions import ValidationError

app = FastAPI(title="ContentAgency Research UI")

# Setup templates directory
templates_dir = Path(__file__).parent / "templates"
templates_dir.mkdir(exist_ok=True)
templates = Jinja2Templates(directory=str(templates_dir))


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main UI page."""
    # Load current data
    user_interests = data_service.get_user_interests()
    recent_posts = data_service.get_recent_posts(limit=10)
    brainstorm_results = data_service.get_brainstorm_results()

    # Get the latest brainstorm result if available
    latest_result = None
    if brainstorm_results and "sessions" in brainstorm_results:
        sessions = brainstorm_results["sessions"]
        if sessions:
            latest_result = sessions[-1]  # Get most recent

    return templates.TemplateResponse("index.html", {
        "request": request,
        "user_interests": user_interests,
        "recent_posts": recent_posts,
        "latest_result": latest_result
    })


@app.get("/api/data")
async def get_data():
    """API endpoint to get current data."""
    recent_posts = data_service.get_recent_posts(limit=10)
    return {
        "user_interests": data_service.get_user_interests(),
        "recent_posts": {"user_id": "user_001", "posts": recent_posts},
        "brainstorm_results": data_service.get_brainstorm_results()
    }


@app.post("/api/update-interests")
async def update_interests(request: Request):
    """Update user interests."""
    data = await request.json()
    data_service.save_user_interests(data)
    return {"status": "success", "message": "Interests updated successfully"}


@app.post("/api/update-posts")
async def update_posts(request: Request):
    """Update recent posts."""
    try:
        data = await request.json()
        data_service.save_recent_posts(data)
        return {"status": "success", "message": "Posts updated successfully"}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )


@app.post("/api/run-brainstorm")
async def run_brainstorm_endpoint():
    """Run the brainstorming crew. Web API wrapper around shared crew runner logic."""
    try:
        # Load user data
        user_interests = data_service.get_user_interests()
        recent_posts = data_service.get_recent_posts(limit=5)

        # Run the shared crew logic
        run_brainstorm_crew(user_interests, recent_posts)

        # Retrieve the latest saved results for returning to client
        brainstorm_results = data_service.get_brainstorm_results()
        latest_result = brainstorm_results["sessions"][-1] if brainstorm_results.get("sessions") else None

        return {
            "status": "success",
            "message": "Brainstorming complete!",
            "result": latest_result
        }

    except ValidationError as e:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": str(e),
                "tip": "Add user interests in the User Interests section and try again."
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )


def start_server(host: str = "127.0.0.1", port: int = 8000):
    """Start the web server."""
    print(f"🚀 Starting ContentAgency Web UI at http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_server()
