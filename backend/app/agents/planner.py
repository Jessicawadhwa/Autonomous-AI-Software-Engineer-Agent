import time
from pathlib import Path
from typing import Dict, Any
from backend.app.agents.state import AgentState
from backend.app.agents.mock_engine import MockDeterministicEngine
from backend.app.services.llm_factory import get_llm_client, parse_json_response

async def planner_node(state: AgentState) -> Dict[str, Any]:
    """
    Planner Agent: Analyzes requirements, decomposes into structured tasks,
    dependencies, and acceptance criteria.
    """
    requirement = state.get("requirement", "")
    project_name = state.get("project_name", "GeneratedProject")
    provider = state.get("llm_provider", "demo")
    
    start_time = time.time()
    
    if provider == "demo":
        plan = MockDeterministicEngine.generate_plan(requirement, project_name)
    else:
        try:
            llm = get_llm_client(
                provider=provider,
                api_key=state.get("api_key"),
                model=state.get("model"),
                temperature=state.get("temperature", 0.2)
            )
            prompt = f"""You are a Lead Software Engineering Planner.
Analyze this user requirement and create a detailed structured implementation plan.

REQUIREMENT:
{requirement}

PROJECT NAME:
{project_name}

Respond ONLY with valid JSON matching this exact structure:
{{
  "project_name": "{project_name}",
  "description": "...",
  "requirements": ["..."],
  "tasks": [
    {{"id": 1, "title": "...", "status": "pending"}}
  ],
  "dependencies": ["..."],
  "acceptance_criteria": ["..."]
}}
"""
            response = await llm.ainvoke(prompt)
            plan = parse_json_response(response.content)
        except Exception as e:
            # Fallback to deterministic plan if LLM fails or keys are not active
            plan = MockDeterministicEngine.generate_plan(requirement, project_name)

    return {
        "plan": plan,
        "current_agent": "planner",
        "current_task": "Requirements breakdown and task planning completed.",
        "status": "running"
    }
