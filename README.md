# ContentAgency - AI-Powered Content Brainstorming

Multi-agent AI system that generates compelling content ideas by analyzing current trends and user interests. Built with [crewAI](https://crewai.com) framework.

## 🚀 Features

- **🔍 Trend Research Agent** - Discovers trending topics and discussions across the internet
- **💡 Content Brainstorming Agent** - Generates platform-specific content suggestions
- **🌐 REST API** - FastAPI with OpenAPI/Swagger documentation
- **🖥️ Interactive Web UI** - Browser-based testing and visualization
- **📊 Structured JSON Responses** - Card-ready data format for frontend integration
- **✅ Comprehensive Testing** - 72 tests covering all components
- **🔄 Multi-user Support** - Isolated data storage per user

## 📋 Prerequisites

- Python >=3.10 <3.14
- OpenAI API key
- (Optional) Serper API key for web search

## 🛠️ Installation

1. **Install UV package manager:**
   ```bash
   pip install uv
   ```

2. **Clone and navigate to project:**
   ```bash
   git clone <repository-url>
   cd contentagency
   ```

3. **Install dependencies:**
   ```bash
   uv sync
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

## 🎯 Quick Start

### Option 1: Web UI (Recommended)
```bash
uv run web_ui
```
- Open http://127.0.0.1:8000
- Edit user interests and recent posts
- Click "Run Brainstorm Crew"
- View results as interactive cards

### Option 2: REST API
```bash
uv run api
```
- API server at http://localhost:8000
- Swagger docs at http://localhost:8000/docs
- Use with cURL, Postman, or your frontend

### Option 3: CLI
```bash
uv run brainstorm
```
- Runs brainstorming from command line
- Uses data from `data/` directory

## 🏗️ Architecture

### Agents

1. **Trend Researcher**
   - Role: Trend Research and Analysis Specialist
   - Searches current trends across the internet
   - Finds articles, discussions, and emerging themes
   - Provides URLs with publication dates

2. **Brainstorming Strategist**
   - Role: Content Strategy and Brainstorming Specialist
   - Analyzes trends and user interests
   - Generates 8-10 platform-specific content ideas
   - Provides engagement predictions and resources

### Workflow

```
User Interests + Recent Posts
         ↓
   Trend Research Task
         ↓
  Brainstorming Task
         ↓
Structured JSON Response
```

### Data Structure

Each suggestion includes:
- **Title** - Engaging topic title
- **Description** - 2-3 sentence explanation
- **Platform Fit** - Recommended platforms (LinkedIn/Twitter/Medium)
- **Interest Alignment** - Connection to user interests
- **Trend Connection** - Link to current trends
- **Resource Links** - URLs with publication dates
- **Engagement Potential** - Expected audience response (High/Moderate/Low)

## 📚 API Documentation

### Endpoints

- `GET /health` - Health check
- `POST /api/v1/interests` - Update user interests
- `POST /api/v1/posts` - Update recent posts
- `POST /api/v1/brainstorm` - Run brainstorming crew
- `GET /api/v1/results` - Get brainstorm results

### Interactive Docs

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Full Documentation**: [API.md](./API.md)

### Example Request

```bash
curl -X POST http://localhost:8000/api/v1/brainstorm \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_001"}'
```

### Example Response

```json
{
  "status": "success",
  "message": "Brainstorming complete!",
  "result": {
    "user_id": "user_001",
    "timestamp": "2025-10-04T10:00:00",
    "suggestions": [
      {
        "id": "suggestion_1",
        "title": "AI in Healthcare: Current Trends",
        "description": "Explore how AI is transforming healthcare...",
        "platform_fit": ["LinkedIn", "Medium"],
        "interest_alignment": "Aligns with AI and healthcare interests",
        "trend_connection": "Recent AI healthcare advancements",
        "resource_links": [
          {
            "title": "AI Healthcare Study",
            "url": "https://example.com/study",
            "published_date": "January 2025"
          }
        ],
        "engagement_potential": "High",
        "engagement_reason": "Timely and relevant to audience"
      }
    ],
    "trending_context_summary": "Key trends include..."
  }
}
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
uv run pytest

# Run specific test files
uv run pytest tests/test_api.py -v
uv run pytest tests/test_crew_runner.py -v

# Run with coverage
uv run pytest --cov=contentagency --cov-report=html
```

See [TESTING.md](./TESTING.md) for detailed testing guide.

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here
MODEL=gpt-4o

# Optional
SERPER_API_KEY=your_serper_api_key_here

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
```

### Data Storage

- **File-based** (current): `data/` directory
- **Migration-ready**: Easy to switch to database service

Files:
- `data/user_interests.json` - User interests
- `data/recent_posts.json` - Recent post performance
- `data/brainstorm_results.json` - Brainstorming sessions

## 📁 Project Structure

```
contentagency/
├── src/contentagency/
│   ├── api/                    # REST API
│   │   ├── main.py            # FastAPI app
│   │   └── models.py          # Pydantic models
│   ├── config/                # Agent/task configs
│   │   ├── agents.yaml
│   │   └── tasks.yaml
│   ├── services/              # Business logic
│   │   ├── crew_runner.py     # Crew execution
│   │   └── data_service.py    # Data access
│   ├── templates/             # Web UI
│   │   └── index.html
│   ├── crew.py                # Crew definition
│   ├── main.py                # CLI entry point
│   └── config.py              # Settings
├── tests/                      # Test suite
├── data/                       # Data storage
├── output/                     # Crew outputs
├── API.md                      # API documentation
├── TESTING.md                  # Testing guide
├── REFACTORING.md             # Refactoring history
└── README.md                   # This file
```

## 🔧 Development

### Customizing Agents

Edit `src/contentagency/config/agents.yaml`:
```yaml
trend_researcher:
  role: >
    Trend Research and Analysis Specialist
  goal: >
    Research current trends and hot topics
  backstory: >
    You're a skilled researcher...
```

### Customizing Tasks

Edit `src/contentagency/config/tasks.yaml`:
```yaml
trend_research_task:
  description: >
    Research current trending topics...
  expected_output: >
    A comprehensive trend research report...
  agent: trend_researcher
```

### Adding Custom Tools

1. Create tool in `src/contentagency/tools/`
2. Import in agent configuration
3. Use in task execution

### Extending the API

1. Add Pydantic models in `src/contentagency/api/models.py`
2. Create endpoints in `src/contentagency/api/main.py`
3. Add tests in `tests/test_api.py`

## 📖 Documentation

- **[API.md](./API.md)** - Complete API reference and examples
- **[TESTING.md](./TESTING.md)** - Testing guide and best practices
- **[REFACTORING.md](./REFACTORING.md)** - Refactoring history and decisions
- **[CLAUDE.md](./CLAUDE.md)** - Instructions for Claude Code AI assistant

## 🤝 Support

For support, questions, or feedback:
- Visit [crewAI documentation](https://docs.crewai.com)
- Check out [crewAI GitHub repository](https://github.com/joaomdmoura/crewai)
- Join [crewAI Discord](https://discord.com/invite/X4JWnZnxPb)

## 📄 License

[Your License Here]

## 🙏 Acknowledgments

Built with [crewAI](https://crewai.com) - The Multi-Agent Framework for AI

---

**Ready to brainstorm?** Start with `uv run web_ui` and explore AI-powered content ideas! 🚀
