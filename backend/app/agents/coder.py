from pathlib import Path
from typing import Dict, Any, List
from backend.app.agents.state import AgentState
from backend.app.agents.mock_engine import MockDeterministicEngine
from backend.app.tools.workspace_tools import create_file, update_file
from backend.app.tools.git_tools import git_commit

async def coder_node(state: AgentState) -> Dict[str, Any]:
    """
    Coder Agent: Creates physical project files and implements the architecture.
    """
    workspace_root = Path(state.get("workspace_root", ""))
    project_name = state.get("project_name", "GeneratedProject")
    provider = state.get("llm_provider", "demo")
    debug_attempts = state.get("debug_attempts", 0)

    # In demo mode, or as baseline, generate initial working project code
    # With intentional minor bug on attempt 0 so debugger demonstrates real execution & auto-fixing!
    has_intentional_bug = (debug_attempts == 0)
    files_created = MockDeterministicEngine.write_initial_code(
        workspace_root=workspace_root,
        project_name=project_name,
        has_intentional_bug=has_intentional_bug
    )

    if state.get("options", {}).get("initialize_git", True) and workspace_root.exists():
        git_commit(workspace_root, "Coder: Implement initial database models, schemas, and REST endpoints")

    return {
        "files_created": files_created,
        "current_agent": "coder",
        "current_task": f"Created {len(files_created)} project source and test files.",
        "status": "running"
    }
