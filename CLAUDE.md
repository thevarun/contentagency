# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a ContentAgency project built with crewAI framework. The project creates multi-agent AI systems where specialized agents collaborate on research and reporting tasks. The long-term vision is to evolve this into a full agentic content agency for multi-platform publishing (see `agentic_content_agency_vision_feature_requirements.md`).

## Common Commands

### Running the Crew
```bash
crewai run
```
Executes the main crew workflow with default inputs (topic: "AI LLMs")

### Project-Specific Commands (via pyproject.toml)
```bash
uv run contentagency  # Run the crew
uv run run_crew       # Alternative run command
uv run train <n_iterations> <filename>  # Train the crew
uv run replay <task_id>  # Replay specific task
uv run test <n_iterations> <eval_llm>   # Test the crew
```

### Dependency Management
```bash
crewai install        # Install dependencies using crewAI CLI
uv sync               # Sync dependencies with uv
```

## Architecture

### Core Structure
- **Main Entry**: `src/contentagency/main.py` - Contains run(), train(), replay(), test() functions
- **Crew Definition**: `src/contentagency/crew.py` - Defines the Contentagency crew class with agents and tasks
- **Configuration**:
  - `src/contentagency/config/agents.yaml` - Agent definitions (researcher, reporting_analyst)
  - `src/contentagency/config/tasks.yaml` - Task definitions (research_task, reporting_task)
- **Tools**: `src/contentagency/tools/` - Custom tool implementations for agents

### Agent Flow
1. **Researcher Agent**: Conducts thorough research on given topics
2. **Reporting Analyst Agent**: Creates detailed reports from research findings
3. **Process**: Sequential execution with final output to `report.md`

### Key Patterns
- Uses crewAI decorators (@agent, @task, @crew, @before_kickoff, @after_kickoff)
- YAML-based configuration for agents and tasks
- Template variables (`{topic}`, `{current_year}`) for dynamic content
- Built-in hooks for pre/post-processing
- Custom tools extend `BaseTool` from crewai.tools

### Configuration Variables
The system uses template variables in YAML configs:
- `{topic}` - Research/content topic (default: "AI LLMs")
- `{current_year}` - Automatically populated with current year

### Crew Execution Modes
- **Sequential Process**: Default execution where tasks run one after another
- **Hierarchical Process**: Alternative execution mode (commented in crew.py:75)
- **Training Mode**: Iterative improvement of agent performance
- **Replay Mode**: Re-execute specific tasks by ID
- **Test Mode**: Evaluation mode with metrics

## Environment Setup

Required environment variables in `.env`:
- `OPENAI_API_KEY` - Required for LLM functionality
- `MODEL` - LLM model to use (default: gpt-4o)
- `SERPER_API_KEY` - For web search capabilities

Python version requirement: >=3.10, <3.14

## Development Notes

- The project uses UV for dependency management with lockfile (`uv.lock`)
- Main workflow outputs research reports to `report.md` in markdown format
- Agents are configured to be verbose for debugging
- No test framework currently implemented (empty `tests/` directory)
- Custom tools should follow the pattern in `src/contentagency/tools/custom_tool.py`
- Agent configurations support dynamic role assignment based on topic
- Output files are generated in project root (e.g., `report.md`)

## File Structure Patterns

- All source code in `src/contentagency/`
- Configuration files in `src/contentagency/config/`
- Custom tools in `src/contentagency/tools/`
- Generated outputs in project root
- Vision and requirements documented in markdown files


## Notes
- We are developing this locally at the moment but later we'd like to deploy it to the cloud. Make migration-friendly choices for this