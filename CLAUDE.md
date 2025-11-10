# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ContentAgency is a multi-agent AI system built with crewAI framework that generates compelling content ideas by analyzing current trends and user interests. The system offers three interfaces (CLI, REST API, Web UI) and features comprehensive testing. The long-term vision is to evolve this into a full agentic content agency for multi-platform publishing (see `agentic_content_agency_vision_feature_requirements.md`).

## Common Commands

### Running the System
```bash
# Recommended: Interactive web interface
uv run web_ui          # Start web UI at http://127.0.0.1:8000

# REST API with Swagger docs
uv run api             # Start API at http://127.0.0.1:8000/docs

# CLI brainstorming
uv run brainstorm      # Run crew from command line using data/ files
```

### Legacy/Alternative Commands
```bash
uv run contentagency   # Legacy: run with default topic "AI LLMs"
uv run run_crew        # Alternative to contentagency
uv run train <n_iterations> <filename>  # Train the crew
uv run replay <task_id>  # Replay specific task
uv run test <n_iterations> <eval_llm>   # Crew testing mode
```

### Testing
```bash
uv run pytest                          # Run all 72 tests
uv run pytest tests/test_api.py -v     # Run API tests with verbose output
uv run pytest tests/test_crew_runner.py -v  # Run crew runner tests
uv run pytest --cov=contentagency --cov-report=html  # Coverage report
```

### Dependency Management
```bash
uv sync                # Sync dependencies (primary method)
crewai install         # Alternative: install via crewAI CLI
```

## Architecture

### Three-Layer Architecture

**Interface Layer** (3 entry points):
- **CLI**: `src/contentagency/main.py` - Brainstorm, train, replay, test modes
- **REST API**: `src/contentagency/api/main.py` - 5 endpoints with OpenAPI docs
- **Web UI**: `src/contentagency/web_ui.py` - Interactive interface with Jinja2 templates

**Service Layer** (orchestration & data):
- **Crew Runner**: `src/contentagency/services/crew_runner.py` - Core execution logic, markdown parsing, result structuring
- **Data Service**: `src/contentagency/services/data_service.py` - Data abstraction (file-based, migration-ready for database)

**Agent Layer** (crewAI):
- **Crew Definition**: `src/contentagency/crew.py` - Agent and task wiring with decorators
- **Configuration**: `src/contentagency/config/agents.yaml` and `tasks.yaml`
- **Models**: `src/contentagency/api/models.py` - Pydantic request/response schemas

### Agent Flow
1. **Trend Researcher Agent**:
   - Uses SerperDevTool for web search
   - Finds trending topics from last 60-90 days (recency enforced)
   - Outputs to `output/trend_research.md`
2. **Brainstorming Strategist Agent**:
   - Analyzes trend research output + user interests + recent posts
   - Generates 8-10 platform-specific content ideas
   - Outputs to `output/brainstorm_suggestions.md`
3. **Process**: Sequential execution → markdown parsing → structured JSON → saved to `data/brainstorm_results.json`

### Key Patterns
- Uses crewAI decorators (@agent, @task, @crew, @before_kickoff, @after_kickoff)
- YAML-based configuration for agents and tasks
- Template variables (`{topic}`, `{current_year}`) for dynamic content
- Built-in hooks for pre/post-processing
- Custom tools extend `BaseTool` from crewai.tools

### Template Variables in YAML Configs
Dynamic variables injected at runtime (see `services/crew_runner.py`):
- `{user_interests}` - Formatted user interest areas
- `{recent_posts}` - User's recent post performance data
- `{current_year}` - Auto-populated current year
- `{current_date}` - Full current date for recency validation

### Data Service Abstraction (Cloud-Migration Ready)
The `data_service.py` uses a **Protocol-based interface** with factory pattern:
- **Current**: `FileDataService` - JSON files in `data/` directory
- **Future**: `DatabaseDataService` - Stub for cloud database (PostgreSQL, MongoDB, etc.)
- **Factory**: `create_data_service(service_type="file")` enables runtime switching

**Data Files**:
- `data/user_interests.json` - User interest topics
- `data/recent_posts.json` - Past content performance
- `data/brainstorm_results.json` - Session history with suggestions

**Key Methods**:
- `get_user_interests(user_id)` / `save_user_interests(data)`
- `get_recent_posts(user_id, limit)` / `save_recent_posts(data)`
- `get_brainstorm_results(user_id)` / `save_brainstorm_results(user_id, results)`

### Crew Execution Modes
- **Brainstorm Mode**: Main workflow (trend research → content ideas)
- **Sequential Process**: Default execution (tasks run one after another)
- **Hierarchical Process**: Alternative mode (commented out in crew.py)
- **Training Mode**: Iterative agent performance improvement
- **Replay Mode**: Re-execute specific tasks by ID
- **Test Mode**: Evaluation mode with metrics

## Environment Setup

**Required** environment variables in `.env`:
- `OPENAI_API_KEY` - Required for LLM functionality
- `MODEL` - LLM model to use (default: gpt-4o)
- `SERPER_API_KEY` - Required for web search (Trend Researcher agent)

**Optional** configuration in `.env`:
- `API_HOST` - Server binding (default: 0.0.0.0)
- `API_PORT` - Server port (default: 8000)
- `DEFAULT_USER_ID` - Default user identifier (default: user_001)
- `CORS_ORIGINS` - Comma-separated allowed origins for CORS

Python version: >=3.10, <3.14

## Critical Implementation Details

### Markdown Parsing & Structured Output
The `crew_runner.py:parse_brainstorm_markdown()` function converts agent markdown output to JSON using regex patterns. When modifying task output formats in `tasks.yaml`, ensure:
- Field names match regex patterns (e.g., "**Title:**", "**Platform Fit:**")
- Resource links follow format: `[Title](URL) - Published: Month Year`
- No triple backticks in markdown output (breaks parsing)

### Recency Enforcement
Trend Researcher agent has **strict 60-90 day recency requirement**:
- Backstory emphasizes "NEVER cite articles >3 months old"
- Task description includes current_date variable for validation
- Publication dates required in all resource links

### Multi-User Support
All data operations support user isolation via `user_id` parameter:
- API requests can include `user_id` (defaults to `DEFAULT_USER_ID`)
- Data service filters by user_id when retrieving results
- Each brainstorm session tagged with user_id + timestamp

### Testing Architecture
72 tests across 4 files using pytest + pytest-mock:
- `test_api.py` - FastAPI endpoint testing with TestClient
- `test_crew_runner.py` - Core logic including markdown parsing
- `test_data_service.py` - Data layer with temporary directories
- `test_models.py` - Pydantic validation rules

Run single test: `uv run pytest tests/test_api.py::TestHealthEndpoint::test_health_endpoint -v`

## Development Notes

- **Dependency Management**: UV with lockfile (`uv.lock`) - use `uv sync` not `pip install`
- **Output Structure**: Agents write markdown to `output/` directory, parsed to JSON, saved to `data/`
- **Custom Tools**: Follow pattern in `src/contentagency/tools/custom_tool.py` (extends BaseTool)
- **Agent Verbosity**: Set to `True` for debugging crew execution
- **Legacy Agents**: `researcher` and `reporting_analyst` preserved in YAML comments for future multi-workflow expansion
- **Cloud Migration**: Data service abstraction allows swapping FileDataService → DatabaseDataService without changing interface layer

## Cloud Deployment Considerations

Current design supports cloud migration:
- **Stateless API**: No in-memory session state
- **Environment-based Config**: Uses Pydantic Settings
- **Data Abstraction**: Protocol-based interface ready for database swap
- **Multi-user Isolation**: User ID tracking throughout system
- **Containerization Ready**: HTTP interfaces on configurable ports
- **CORS Support**: Configurable allowed origins for frontend hosting