# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a ContentAgency project built with crewAI framework. The project creates multi-agent AI systems where specialized agents collaborate on research and reporting tasks.

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

### Agent Flow
1. **Researcher Agent**: Conducts thorough research on given topics
2. **Reporting Analyst Agent**: Creates detailed reports from research findings
3. **Process**: Sequential execution with final output to `report.md`

### Key Patterns
- Uses crewAI decorators (@agent, @task, @crew, @before_kickoff, @after_kickoff)
- YAML-based configuration for agents and tasks
- Template variables (`{topic}`, `{current_year}`) for dynamic content
- Built-in hooks for pre/post-processing

## Environment Setup

Add `OPENAI_API_KEY` to `.env` file for LLM functionality.

Python version requirement: >=3.10, <3.14

## Development Notes

- The project uses UV for dependency management
- Main workflow outputs research reports to `report.md` in markdown format
- Agents are configured to be verbose for debugging
- Sequential process execution (can be changed to hierarchical)