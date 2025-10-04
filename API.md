# ContentAgency REST API

Backend API for content brainstorming and trend research with frontend integration support.

## Quick Start

### 1. Install Dependencies
```bash
uv sync
```

### 2. Configure Environment
Copy `.env.example` to `.env` and add your API keys:
```bash
cp .env.example .env
# Edit .env with your OPENAI_API_KEY
```

### 3. Start API Server
```bash
uv run api
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health

## API Endpoints

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "v1"
}
```

### Update User Interests
```http
POST /api/v1/interests
Content-Type: application/json

{
  "user_id": "user_001",
  "interests": [
    {"topic": "Artificial Intelligence"},
    {"topic": "Technology Trends"},
    {"topic": "Business Strategy"}
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Successfully updated 3 interests for user user_001"
}
```

### Update Recent Posts
```http
POST /api/v1/posts
Content-Type: application/json

{
  "user_id": "user_001",
  "posts": [
    {
      "id": "post_001",
      "platform": "linkedin",
      "content": "Post content here...",
      "title": "Optional title",
      "topics": ["AI", "Tech"]
    }
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Successfully updated 1 posts for user user_001"
}
```

### Run Brainstorming Crew
```http
POST /api/v1/brainstorm
Content-Type: application/json

{
  "user_id": "user_001"
}
```

**Optional - Override data for this session:**
```json
{
  "user_id": "user_001",
  "interests": {
    "user_id": "user_001",
    "interests": [{"topic": "AI Ethics"}]
  },
  "posts": {
    "user_id": "user_001",
    "posts": [...]
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Brainstorming complete!",
  "result": {
    "user_id": "user_001",
    "timestamp": "2025-10-04T10:30:00",
    "suggested_topics": "**Content Topic Suggestions:**\n\n1. ..."
  }
}
```

### Get Brainstorm Results
```http
GET /api/v1/results?limit=10
```

**Response:**
```json
{
  "status": "success",
  "count": 5,
  "sessions": [
    {
      "user_id": "user_001",
      "timestamp": "2025-10-04T10:30:00",
      "suggested_topics": "..."
    }
  ]
}
```

## Error Responses

All errors follow a standardized format:

```json
{
  "status": "error",
  "message": "Error description",
  "detail": "Additional details (optional)"
}
```

**Common Status Codes:**
- `400` - Validation error (bad request data)
- `500` - Server error

## CORS Configuration

By default, the API allows requests from:
- `http://localhost:3000`
- `http://localhost:3001`
- `http://localhost:8000`

To add your frontend URL, update `CORS_ORIGINS` in `.env`:
```bash
CORS_ORIGINS=http://localhost:3000,https://your-frontend.com
```

## Validation

All requests are validated using Pydantic models:

- **Interests**: Must have at least one topic, topics cannot be empty
- **Posts**: Must include id, platform, and content
- **User ID**: Required and cannot be empty

## Development vs Production

### Local Development (with UI)
```bash
uv run web_ui
```
This starts the local web UI at http://localhost:8000 for testing.

### Production API (for frontend)
```bash
uv run api
```
This starts the REST API without the UI, ready for frontend integration.

## Interactive Documentation

Visit http://localhost:8000/docs for interactive Swagger UI documentation where you can:
- See all endpoints
- Test API calls
- View request/response schemas
- Download OpenAPI spec

## Example Frontend Integration

### JavaScript/TypeScript
```typescript
const API_URL = 'http://localhost:8000';

// Run brainstorm
async function runBrainstorm(userId: string) {
  const response = await fetch(`${API_URL}/api/v1/brainstorm`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ user_id: userId }),
  });

  const data = await response.json();
  return data.result;
}

// Update interests
async function updateInterests(userId: string, interests: string[]) {
  const response = await fetch(`${API_URL}/api/v1/interests`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      user_id: userId,
      interests: interests.map(topic => ({ topic })),
    }),
  });

  return await response.json();
}
```

### Python
```python
import requests

API_URL = "http://localhost:8000"

def run_brainstorm(user_id: str):
    response = requests.post(
        f"{API_URL}/api/v1/brainstorm",
        json={"user_id": user_id}
    )
    return response.json()

def update_interests(user_id: str, topics: list[str]):
    response = requests.post(
        f"{API_URL}/api/v1/interests",
        json={
            "user_id": user_id,
            "interests": [{"topic": t} for t in topics]
        }
    )
    return response.json()
```

## Deployment

The API is ready for deployment to:
- **Railway**: Deploy with one click
- **Render**: Free tier available
- **AWS Lambda**: Use Mangum adapter
- **Google Cloud Run**: Container deployment
- **Azure Container Apps**: Container deployment

See deployment guides in the documentation for platform-specific instructions.
