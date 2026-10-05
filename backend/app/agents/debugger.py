from pathlib import Path
from typing import Dict, Any
from backend.app.agents.state import AgentState
from backend.app.agents.mock_engine import MockDeterministicEngine
from backend.app.tools.git_tools import git_commit

async def debugger_node(state: AgentState) -> Dict[str, Any]:
    """
    Debugger Agent: Reads test failure tracebacks, diagnoses root cause,
    applies code modifications, and increments debug iterations.
    """
    workspace_root = Path(state.get("workspace_root", ""))
    debug_attempts = state.get("debug_attempts", 0) + 1
    test_results = state.get("test_results", {})
    failures = test_results.get("failures", [])

    # Apply deterministic fix or LLM-guided patch
    fix_report = MockDeterministicEngine.apply_debugger_fix(workspace_root)
    
    if state.get("options", {}).get("initialize_git", True) and workspace_root.exists():
        git_commit(workspace_root, f"Debugger: Fixed failing test cases (Attempt {debug_attempts})")

    return {
        "debug_attempts": debug_attempts,
        "current_agent": "debugger",
        "current_task": f"Diagnosed test failure and patched {fix_report.get('fixed_file', 'source code')}. Triggering re-test.",
        "status": "running"
    }
