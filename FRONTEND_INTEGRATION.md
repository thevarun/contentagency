# ContentAgency API - Frontend Integration Guide

This guide provides everything needed to integrate the ContentAgency REST API into a React TypeScript frontend application.

## Table of Contents
- [Quick Start](#quick-start)
- [Base Configuration](#base-configuration)
- [TypeScript Types](#typescript-types)
- [API Endpoints](#api-endpoints)
- [React Integration Examples](#react-integration-examples)
- [Error Handling](#error-handling)
- [Testing](#testing)

---

## Quick Start

### Backend Setup
```bash
# Start the API server (from backend directory)
uv run api
# Server runs at: http://127.0.0.1:8000
# API docs available at: http://127.0.0.1:8000/docs
```

### Frontend Environment Variables
Create a `.env.local` file in your React project:
```env
REACT_APP_API_BASE_URL=http://127.0.0.1:8000
REACT_APP_API_VERSION=v1
REACT_APP_USER_ID=user_001  # Optional: default user ID
```

---

## Base Configuration

### API Details
- **Base URL**: `http://127.0.0.1:8000`
- **API Version**: `v1`
- **Versioned Base Path**: `/api/v1`
- **CORS**: Enabled for `localhost:3000`, `localhost:3001`, `localhost:8000`
- **Content-Type**: `application/json`

### CORS Configuration
The backend accepts requests from these origins by default:
- `http://localhost:3000` (CRA default)
- `http://localhost:3001` (alternative port)
- `http://localhost:8000` (backend itself)

To add custom origins, set `CORS_ORIGINS` in backend `.env`:
```env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,https://myapp.com
```

---

## TypeScript Types

Create these types in `src/types/api.ts`:

```typescript
// ============================================
// Request Types
// ============================================

export interface InterestItem {
  topic: string;
}

export interface UserInterestsRequest {
  user_id: string;
  interests: InterestItem[];
}

export interface PostItem {
  id: string;
  platform: string;
  content: string;
  title?: string;
  topics?: string[];
}

export interface RecentPostsRequest {
  user_id: string;
  posts: PostItem[];
}

export interface BrainstormRequest {
  user_id?: string;
  interests?: UserInterestsRequest;
  posts?: RecentPostsRequest;
}

// ============================================
// Response Types
// ============================================

export interface ResourceLink {
  title: string;
  url: string;
  published_date?: string;
}

export interface ContentSuggestion {
  id: string;
  title: string;
  description: string;
  platform_fit: string[];
  interest_alignment: string;
  trend_connection: string;
  resource_links: ResourceLink[];
  engagement_potential: string; // "High" | "Moderate" | "Low"
  engagement_reason: string;
}

export interface BrainstormResult {
  user_id: string;
  timestamp: string;
  suggestions: ContentSuggestion[];
  trending_context_summary?: string;
}

export interface BrainstormResponse {
  status: string;
  message: string;
  result?: BrainstormResult;
}

export interface SuccessResponse {
  status: string;
  message: string;
}

export interface ErrorResponse {
  status: string;
  message: string;
  detail?: string;
}

export interface HealthResponse {
  status: string;
  version: string;
}

export interface ResultsResponse {
  status: string;
  count: number;
  sessions: BrainstormResult[];
}
```

---

## API Endpoints

### 1. Health Check
Check if the API is running.

**Endpoint**: `GET /health`

**Response**: `HealthResponse`

```typescript
// TypeScript Example
const checkHealth = async (): Promise<HealthResponse> => {
  const response = await fetch('http://127.0.0.1:8000/health');
  if (!response.ok) throw new Error('Health check failed');
  return response.json();
};
```

```bash
# cURL Example
curl -X GET "http://127.0.0.1:8000/health"
```

**Response Example**:
```json
{
  "status": "healthy",
  "version": "v1"
}
```

---

### 2. Update User Interests
Save user interests for content personalization.

**Endpoint**: `POST /api/v1/interests`

**Request Body**: `UserInterestsRequest`

**Response**: `SuccessResponse`

```typescript
// TypeScript Example
const updateInterests = async (
  userId: string,
  interests: string[]
): Promise<SuccessResponse> => {
  const response = await fetch('http://127.0.0.1:8000/api/v1/interests', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: userId,
      interests: interests.map(topic => ({ topic }))
    })
  });

  if (!response.ok) {
    const error: ErrorResponse = await response.json();
    throw new Error(error.message);
  }

  return response.json();
};

// Usage
await updateInterests('user_001', [
  'Artificial Intelligence',
  'Machine Learning',
  'Web Development',
  'Startup Entrepreneurship'
]);
```

```bash
# cURL Example
curl -X POST "http://127.0.0.1:8000/api/v1/interests" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "interests": [
      {"topic": "Artificial Intelligence"},
      {"topic": "Machine Learning"}
    ]
  }'
```

**Response Example**:
```json
{
  "status": "success",
  "message": "Successfully updated 4 interests for user user_001"
}
```

---

### 3. Update Recent Posts
Save user's recent post history for context-aware suggestions.

**Endpoint**: `POST /api/v1/posts`

**Request Body**: `RecentPostsRequest`

**Response**: `SuccessResponse`

```typescript
// TypeScript Example
const updatePosts = async (
  userId: string,
  posts: PostItem[]
): Promise<SuccessResponse> => {
  const response = await fetch('http://127.0.0.1:8000/api/v1/posts', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: userId,
      posts
    })
  });

  if (!response.ok) {
    const error: ErrorResponse = await response.json();
    throw new Error(error.message);
  }

  return response.json();
};

// Usage
await updatePosts('user_001', [
  {
    id: 'post_001',
    platform: 'linkedin',
    content: 'My thoughts on AI trends...',
    title: 'AI Trends 2025',
    topics: ['AI', 'Technology']
  },
  {
    id: 'post_002',
    platform: 'twitter',
    content: 'Quick tip on React hooks...',
    topics: ['React', 'JavaScript']
  }
]);
```

```bash
# cURL Example
curl -X POST "http://127.0.0.1:8000/api/v1/posts" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "posts": [
      {
        "id": "post_001",
        "platform": "linkedin",
        "content": "My thoughts on AI...",
        "title": "AI Trends",
        "topics": ["AI"]
      }
    ]
  }'
```

**Response Example**:
```json
{
  "status": "success",
  "message": "Successfully updated 2 posts for user user_001"
}
```

---

### 4. Run Brainstorm (Main Workflow)
Generate AI-powered content suggestions based on trends and user context.

**Endpoint**: `POST /api/v1/brainstorm`

**Request Body**: `BrainstormRequest` (all fields optional)

**Response**: `BrainstormResponse`

**Note**: This endpoint takes 30-60 seconds to complete as it runs AI agents.

```typescript
// TypeScript Example - Simple (uses stored interests/posts)
const runBrainstorm = async (
  userId?: string
): Promise<BrainstormResponse> => {
  const response = await fetch('http://127.0.0.1:8000/api/v1/brainstorm', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId })
  });

  if (!response.ok) {
    const error: ErrorResponse = await response.json();
    throw new Error(error.message);
  }

  return response.json();
};

// TypeScript Example - Override interests/posts for one-time use
const runBrainstormWithOverrides = async (
  request: BrainstormRequest
): Promise<BrainstormResponse> => {
  const response = await fetch('http://127.0.0.1:8000/api/v1/brainstorm', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request)
  });

  if (!response.ok) {
    const error: ErrorResponse = await response.json();
    throw new Error(error.message);
  }

  return response.json();
};

// Usage - Simple
const result = await runBrainstorm('user_001');
console.log(`Generated ${result.result?.suggestions.length} suggestions`);

// Usage - With overrides (doesn't save to backend)
const result = await runBrainstormWithOverrides({
  user_id: 'user_002',
  interests: {
    user_id: 'user_002',
    interests: [{ topic: 'AI' }, { topic: 'Blockchain' }]
  },
  posts: {
    user_id: 'user_002',
    posts: [
      {
        id: 'temp_001',
        platform: 'linkedin',
        content: 'My blockchain post...',
        topics: ['Blockchain']
      }
    ]
  }
});
```

```bash
# cURL Example - Simple
curl -X POST "http://127.0.0.1:8000/api/v1/brainstorm" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_001"}'

# cURL Example - With overrides
curl -X POST "http://127.0.0.1:8000/api/v1/brainstorm" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "interests": {
      "user_id": "user_001",
      "interests": [
        {"topic": "AI"},
        {"topic": "Blockchain"}
      ]
    }
  }'
```

**Response Example**:
```json
{
  "status": "success",
  "message": "Brainstorming complete!",
  "result": {
    "user_id": "user_001",
    "timestamp": "2025-11-10T14:30:00",
    "trending_context_summary": "Current trends show increased interest in AI safety...",
    "suggestions": [
      {
        "id": "suggestion_001",
        "title": "The Rise of AI Safety Protocols in 2025",
        "description": "Explore how companies are implementing new AI safety measures...",
        "platform_fit": ["linkedin", "medium"],
        "interest_alignment": "Aligns with your interest in AI and technology ethics",
        "trend_connection": "AI safety is trending with 45% increase in discussions",
        "resource_links": [
          {
            "title": "AI Safety Guidelines Released",
            "url": "https://example.com/ai-safety",
            "published_date": "November 2025"
          }
        ],
        "engagement_potential": "High",
        "engagement_reason": "Timely topic with strong industry relevance"
      }
    ]
  }
}
```

---

### 5. Get Brainstorm Results
Retrieve historical brainstorm sessions.

**Endpoint**: `GET /api/v1/results?limit=10`

**Query Parameters**:
- `limit` (optional, default: 10): Number of recent sessions to return

**Response**: `ResultsResponse`

```typescript
// TypeScript Example
const getResults = async (limit: number = 10): Promise<ResultsResponse> => {
  const response = await fetch(
    `http://127.0.0.1:8000/api/v1/results?limit=${limit}`
  );

  if (!response.ok) {
    const error: ErrorResponse = await response.json();
    throw new Error(error.message);
  }

  return response.json();
};

// Usage
const results = await getResults(5);
console.log(`Found ${results.count} sessions`);
results.sessions.forEach(session => {
  console.log(`${session.timestamp}: ${session.suggestions.length} ideas`);
});
```

```bash
# cURL Example
curl -X GET "http://127.0.0.1:8000/api/v1/results?limit=5"
```

**Response Example**:
```json
{
  "status": "success",
  "count": 3,
  "sessions": [
    {
      "user_id": "user_001",
      "timestamp": "2025-11-10T14:30:00",
      "suggestions": [...],
      "trending_context_summary": "..."
    },
    {
      "user_id": "user_001",
      "timestamp": "2025-11-09T10:15:00",
      "suggestions": [...],
      "trending_context_summary": "..."
    }
  ]
}
```

---

## React Integration Examples

### API Service Layer
Create `src/services/contentAgencyApi.ts`:

```typescript
import {
  HealthResponse,
  UserInterestsRequest,
  RecentPostsRequest,
  BrainstormRequest,
  BrainstormResponse,
  ResultsResponse,
  SuccessResponse,
  ErrorResponse
} from '../types/api';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://127.0.0.1:8000';
const API_VERSION = process.env.REACT_APP_API_VERSION || 'v1';

class ContentAgencyAPI {
  private baseUrl: string;
  private apiPath: string;

  constructor() {
    this.baseUrl = API_BASE_URL;
    this.apiPath = `/api/${API_VERSION}`;
  }

  // Health check
  async health(): Promise<HealthResponse> {
    const response = await fetch(`${this.baseUrl}/health`);
    if (!response.ok) throw await this.handleError(response);
    return response.json();
  }

  // Update interests
  async updateInterests(
    userId: string,
    interests: string[]
  ): Promise<SuccessResponse> {
    const response = await fetch(`${this.baseUrl}${this.apiPath}/interests`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userId,
        interests: interests.map(topic => ({ topic }))
      })
    });
    if (!response.ok) throw await this.handleError(response);
    return response.json();
  }

  // Update posts
  async updatePosts(request: RecentPostsRequest): Promise<SuccessResponse> {
    const response = await fetch(`${this.baseUrl}${this.apiPath}/posts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });
    if (!response.ok) throw await this.handleError(response);
    return response.json();
  }

  // Run brainstorm
  async brainstorm(request: BrainstormRequest = {}): Promise<BrainstormResponse> {
    const response = await fetch(`${this.baseUrl}${this.apiPath}/brainstorm`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });
    if (!response.ok) throw await this.handleError(response);
    return response.json();
  }

  // Get results
  async getResults(limit: number = 10): Promise<ResultsResponse> {
    const response = await fetch(
      `${this.baseUrl}${this.apiPath}/results?limit=${limit}`
    );
    if (!response.ok) throw await this.handleError(response);
    return response.json();
  }

  // Error handler
  private async handleError(response: Response): Promise<Error> {
    try {
      const error: ErrorResponse = await response.json();
      return new Error(error.message || 'API request failed');
    } catch {
      return new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
  }
}

export const api = new ContentAgencyAPI();
```

### React Hooks

Create `src/hooks/useContentAgency.ts`:

```typescript
import { useState, useCallback } from 'react';
import { api } from '../services/contentAgencyApi';
import {
  BrainstormResponse,
  ResultsResponse,
  PostItem,
  BrainstormRequest
} from '../types/api';

export const useContentAgency = (userId: string = 'user_001') => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Update interests
  const updateInterests = useCallback(async (interests: string[]) => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.updateInterests(userId, interests);
      return result;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to update interests';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [userId]);

  // Update posts
  const updatePosts = useCallback(async (posts: PostItem[]) => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.updatePosts({ user_id: userId, posts });
      return result;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to update posts';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [userId]);

  // Run brainstorm
  const runBrainstorm = useCallback(async (
    request?: BrainstormRequest
  ): Promise<BrainstormResponse | null> => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.brainstorm(request || { user_id: userId });
      return result;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Brainstorm failed';
      setError(message);
      return null;
    } finally {
      setLoading(false);
    }
  }, [userId]);

  // Get results
  const getResults = useCallback(async (
    limit: number = 10
  ): Promise<ResultsResponse | null> => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.getResults(limit);
      return result;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch results';
      setError(message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    loading,
    error,
    updateInterests,
    updatePosts,
    runBrainstorm,
    getResults
  };
};
```

### Example Component

```typescript
import React, { useState } from 'react';
import { useContentAgency } from './hooks/useContentAgency';
import { ContentSuggestion } from './types/api';

const BrainstormPage: React.FC = () => {
  const { loading, error, runBrainstorm } = useContentAgency('user_001');
  const [suggestions, setSuggestions] = useState<ContentSuggestion[]>([]);

  const handleBrainstorm = async () => {
    const result = await runBrainstorm();
    if (result?.result?.suggestions) {
      setSuggestions(result.result.suggestions);
    }
  };

  return (
    <div className="brainstorm-page">
      <h1>Content Brainstorm</h1>

      <button
        onClick={handleBrainstorm}
        disabled={loading}
      >
        {loading ? 'Generating Ideas...' : 'Generate Content Ideas'}
      </button>

      {error && <div className="error">{error}</div>}

      <div className="suggestions">
        {suggestions.map(suggestion => (
          <div key={suggestion.id} className="suggestion-card">
            <h2>{suggestion.title}</h2>
            <p>{suggestion.description}</p>
            <div className="meta">
              <span>Platforms: {suggestion.platform_fit.join(', ')}</span>
              <span>Engagement: {suggestion.engagement_potential}</span>
            </div>
            <div className="resources">
              {suggestion.resource_links.map((link, idx) => (
                <a key={idx} href={link.url} target="_blank" rel="noopener noreferrer">
                  {link.title}
                </a>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default BrainstormPage;
```

---

## Error Handling

### Error Response Format
All errors return consistent structure:

```typescript
{
  "status": "error",
  "message": "Human-readable error message",
  "detail": "Technical details (optional)"
}
```

### HTTP Status Codes
- `200` - Success
- `400` - Bad Request (validation errors)
- `500` - Internal Server Error

### Common Errors

**Validation Error** (400):
```json
{
  "status": "error",
  "message": "At least one interest is required",
  "detail": "Please check your request data and try again."
}
```

**Server Error** (500):
```json
{
  "status": "error",
  "message": "Brainstorming failed: OpenAI API key not configured",
  "detail": "OPENAI_API_KEY environment variable is missing"
}
```

### Error Handling Pattern

```typescript
try {
  const result = await api.brainstorm({ user_id: 'user_001' });
  // Handle success
} catch (error) {
  if (error instanceof Error) {
    // Display error.message to user
    console.error('Brainstorm error:', error.message);
  }
}
```

---

## Testing

### Test API Connection

```typescript
// Quick connection test
import { api } from './services/contentAgencyApi';

const testConnection = async () => {
  try {
    const health = await api.health();
    console.log('✓ API is healthy:', health);

    const results = await api.getResults(1);
    console.log('✓ Can fetch results:', results);

    return true;
  } catch (error) {
    console.error('✗ API connection failed:', error);
    return false;
  }
};
```

### Manual Testing with cURL

```bash
# 1. Check health
curl http://127.0.0.1:8000/health

# 2. Update interests
curl -X POST http://127.0.0.1:8000/api/v1/interests \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test_user","interests":[{"topic":"AI"}]}'

# 3. Run brainstorm (takes 30-60 seconds)
curl -X POST http://127.0.0.1:8000/api/v1/brainstorm \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test_user"}'

# 4. Get results
curl http://127.0.0.1:8000/api/v1/results?limit=1
```

### Interactive API Documentation
The backend provides interactive Swagger docs:
```
http://127.0.0.1:8000/docs
```

Use this to:
- Test all endpoints in browser
- See detailed request/response schemas
- Try different payloads

---

## Typical Workflow

### First-Time User Setup
1. **Update interests** → `POST /api/v1/interests`
2. **Update recent posts** (optional) → `POST /api/v1/posts`
3. **Run brainstorm** → `POST /api/v1/brainstorm`
4. **Display suggestions** from response

### Returning User
1. **Run brainstorm** → `POST /api/v1/brainstorm` (uses stored data)
2. **Display suggestions** from response

### View History
1. **Get results** → `GET /api/v1/results?limit=20`
2. **Display past sessions** with timestamps

### Quick Experiment (No Storage)
1. **Run brainstorm with overrides** → `POST /api/v1/brainstorm` with `interests` and `posts` in request body
2. Data not saved, useful for testing different personas

---

## Performance Notes

- **Brainstorm endpoint**: 30-60 seconds (runs AI agents)
- **Other endpoints**: < 100ms
- **Rate limiting**: Not currently implemented
- **Concurrent requests**: Supported (each brainstorm is independent)

---

## Support

- **API Documentation**: http://127.0.0.1:8000/docs
- **Backend Issues**: Check backend console logs
- **CORS Issues**: Verify `CORS_ORIGINS` in backend `.env`
- **Timeout Issues**: Brainstorm endpoint may take up to 60 seconds

---

## Example .env Files

### Backend `.env`
```env
OPENAI_API_KEY=sk-...
MODEL=gpt-4o
SERPER_API_KEY=...
API_HOST=0.0.0.0
API_PORT=8000
DEFAULT_USER_ID=user_001
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Frontend `.env.local`
```env
REACT_APP_API_BASE_URL=http://127.0.0.1:8000
REACT_APP_API_VERSION=v1
REACT_APP_USER_ID=user_001
```

---

## Quick Reference

| Endpoint | Method | Purpose | Duration |
|----------|--------|---------|----------|
| `/health` | GET | Health check | < 100ms |
| `/api/v1/interests` | POST | Save user interests | < 100ms |
| `/api/v1/posts` | POST | Save recent posts | < 100ms |
| `/api/v1/brainstorm` | POST | Generate content ideas | 30-60s |
| `/api/v1/results` | GET | Get history | < 100ms |

---

**Generated for ContentAgency API v1**
Last Updated: 2025-11-10
