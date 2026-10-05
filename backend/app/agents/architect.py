import time
from typing import Dict, Any
from backend.app.agents.state import AgentState
from backend.app.agents.mock_engine import MockDeterministicEngine
from backend.app.services.llm_factory import get_llm_client, parse_json_response
from backend.app.tools.git_tools import git_commit
from pathlib import Path

async def architect_node(state: AgentState) -> Dict[str, Any]:
    """
    Architect Agent: Designs the system architecture, file hierarchy,
    data models, API endpoints, and security considerations.
    """
    requirement = state.get("requirement", "")
    project_name = state.get("project_name", "GeneratedProject")
    provider = state.get("llm_provider", "demo")
    workspace_root = Path(state.get("workspace_root", ""))
    
    if provider == "demo":
        architecture = MockDeterministicEngine.generate_architecture(requirement, project_name)
    else:
        try:
            llm = get_llm_client(
                provider=provider,
                api_key=state.get("api_key"),
                model=state.get("model"),
                temperature=state.get("temperature", 0.2)
            )
            prompt = f"""You are a Principal Software Architect.
Given this project plan:
{state.get("plan")}

Design the complete modular architecture.
Respond ONLY with valid JSON in this exact structure:
{{
  "tech_stack": {{
    "framework": "FastAPI",
    "database": "SQLite",
    "orm": "SQLAlchemy",
    "validation": "Pydantic V2",
    "testing": "Pytest"
  }},
  "directory_structure": ["app/", "app/main.py", "tests/", "requirements.txt"],
  "modules": {{
    "app.main": "Main entrypoint and routing",
    "app.models": "Database models"
  }},
  "security_considerations": ["..."]
}}
"""
            response = await llm.ainvoke(prompt)
            architecture = parse_json_response(response.content)
        except Exception:
            architecture = MockDeterministicEngine.generate_architecture(requirement, project_name)

    # Make git commit for architecture phase if git is enabled
    if state.get("options", {}).get("initialize_git", True) and workspace_root.exists():
        git_commit(workspace_root, "Architect: Project blueprint and tech stack design")

    return {
        "architecture": architecture,
        "current_agent": "architect",
        "current_task": "System architecture and module boundaries designed.",
        "status": "running"
    }
