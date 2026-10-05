from pathlib import Path
from typing import Dict, Any
from backend.app.agents.state import AgentState
from backend.app.tools.test_tools import run_project_pytest
from backend.app.tools.git_tools import git_commit

__test__ = False


async def tester_node(state: AgentState) -> Dict[str, Any]:
    """
    Test Agent: Actually executes pytest against the generated project workspace.
    Captures stdout, stderr, and failure traces.
    """
    workspace_root = Path(state.get("workspace_root", ""))
    options = state.get("options", {})
    
    if not options.get("generate_tests", True):
        return {
            "test_results": {"success": True, "total": 0, "passed": 0, "failed": 0, "errors": 0, "failures": []},
            "current_agent": "tester",
            "current_task": "Tests skipped as per project configuration.",
            "status": "running"
        }

    # Run genuine pytest in workspace
    test_results = run_project_pytest(workspace_root, test_path="tests", timeout=45)

    if test_results["success"] and options.get("initialize_git", True):
        git_commit(workspace_root, f"Test: All {test_results['passed']} unit tests verified passing")

    return {
        "test_results": test_results,
        "current_agent": "tester",
        "current_task": f"Executed test suite: {test_results.get('passed', 0)} passed, {test_results.get('failed', 0)} failed.",
        "status": "running"
    }
