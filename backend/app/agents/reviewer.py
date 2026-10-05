from pathlib import Path
from typing import Dict, Any, List
from backend.app.agents.state import AgentState
from backend.app.agents.mock_engine import MockDeterministicEngine
from backend.app.tools.git_tools import git_commit

async def reviewer_node(state: AgentState) -> Dict[str, Any]:
    """
    Code Reviewer Agent: Inspects the complete project codebase for security,
    architecture, performance, and best practices.
    """
    workspace_root = Path(state.get("workspace_root", ""))
    options = state.get("options", {})
    
    if not options.get("run_code_review", True):
        return {
            "review_results": [],
            "current_agent": "reviewer",
            "current_task": "Code review skipped as per configuration.",
            "status": "running"
        }

    findings = MockDeterministicEngine.generate_review(workspace_root)

    if options.get("initialize_git", True) and workspace_root.exists():
        git_commit(workspace_root, "Reviewer: Completed code quality and security inspection")

    return {
        "review_results": findings,
        "current_agent": "reviewer",
        "current_task": f"Completed code review with {len(findings)} recommendations.",
        "status": "running"
    }
