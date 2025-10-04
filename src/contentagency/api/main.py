"""
ContentAgency REST API - Production backend for frontend integration.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from contentagency.config import settings
from contentagency.api.models import (
    UserInterestsRequest,
    RecentPostsRequest,
    BrainstormRequest,
    BrainstormResponse,
    BrainstormResult,
    SuccessResponse,
    ErrorResponse,
    HealthResponse
)
from contentagency.services.data_service import data_service
from contentagency.services.crew_runner import run_brainstorm_crew
from contentagency.exceptions import ValidationError

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version=settings.api_version
    )


@app.post(f"/api/{settings.api_version}/interests", response_model=SuccessResponse)
async def update_interests(request: UserInterestsRequest):
    """Update user interests."""
    try:
        # Convert Pydantic model to dict format expected by data service
        interests_data = {
            "user_id": request.user_id,
            "interests": [{"topic": item.topic} for item in request.interests]
        }

        data_service.save_user_interests(interests_data)

        return SuccessResponse(
            status="success",
            message=f"Successfully updated {len(request.interests)} interests for user {request.user_id}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update interests: {str(e)}"
        )


@app.post(f"/api/{settings.api_version}/posts", response_model=SuccessResponse)
async def update_posts(request: RecentPostsRequest):
    """Update recent posts."""
    try:
        # Convert Pydantic model to dict format expected by data service
        posts_data = {
            "user_id": request.user_id,
            "posts": [post.model_dump() for post in request.posts]
        }

        data_service.save_recent_posts(posts_data)

        return SuccessResponse(
            status="success",
            message=f"Successfully updated {len(request.posts)} posts for user {request.user_id}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update posts: {str(e)}"
        )


@app.post(f"/api/{settings.api_version}/brainstorm", response_model=BrainstormResponse)
async def run_brainstorm(request: BrainstormRequest):
    """
    Run the brainstorming crew.

    Can optionally override user_id, interests, and posts for this session.
    If not provided, uses data from the data service.
    """
    try:
        # Determine user_id
        user_id = request.user_id or settings.default_user_id

        # Get user interests (from request or data service)
        if request.interests:
            user_interests = {
                "user_id": request.interests.user_id,
                "interests": [{"topic": item.topic} for item in request.interests.interests]
            }
        else:
            user_interests = data_service.get_user_interests()

        # Get recent posts (from request or data service)
        if request.posts:
            recent_posts = [post.model_dump() for post in request.posts.posts]
        else:
            recent_posts = data_service.get_recent_posts(limit=5)

        # Run the brainstorming crew with user_id
        run_brainstorm_crew(user_interests, recent_posts, user_id=user_id)

        # Retrieve the latest result
        brainstorm_results = data_service.get_brainstorm_results()
        latest_session = brainstorm_results["sessions"][-1] if brainstorm_results.get("sessions") else None

        if latest_session:
            result = BrainstormResult(
                user_id=latest_session.get("user_id", user_id),
                timestamp=latest_session.get("timestamp", ""),
                suggestions=latest_session.get("suggestions", []),
                trending_context_summary=latest_session.get("trending_context_summary", "")
            )
        else:
            result = None

        return BrainstormResponse(
            status="success",
            message="Brainstorming complete!",
            result=result
        )

    except ValidationError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Brainstorming failed: {str(e)}"
        )


@app.get(f"/api/{settings.api_version}/results")
async def get_results(limit: int = 10):
    """Get brainstorm results."""
    try:
        results = data_service.get_brainstorm_results()
        sessions = results.get("sessions", [])

        # Return latest sessions (limited)
        return {
            "status": "success",
            "count": len(sessions),
            "sessions": sessions[-limit:] if limit > 0 else sessions
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve results: {str(e)}"
        )


@app.exception_handler(ValidationError)
async def validation_error_handler(exc: ValidationError):
    """Handle ValidationError exceptions."""
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            status="error",
            message=str(exc),
            detail="Please check your request data and try again."
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(exc: Exception):
    """Handle general exceptions."""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            status="error",
            message="An unexpected error occurred",
            detail=str(exc)
        ).model_dump()
    )


def start_api(host: str = None, port: int = None):
    """Start the API server."""
    host = host or settings.host
    port = port or settings.port

    print(f"🚀 Starting ContentAgency API at http://{host}:{port}")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    print(f"🔄 CORS enabled for: {', '.join(settings.cors_origins)}")

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_api()
