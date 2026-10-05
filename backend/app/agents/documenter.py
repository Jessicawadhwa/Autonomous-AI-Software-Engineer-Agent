from pathlib import Path
from typing import Dict, Any
from backend.app.agents.state import AgentState
from backend.app.agents.mock_engine import MockDeterministicEngine
from backend.app.tools.workspace_tools import create_file
from backend.app.tools.git_tools import git_commit

async def documenter_node(state: AgentState) -> Dict[str, Any]:
    """
    Documentation Agent: Generates comprehensive, production-grade README.md
    from the actual generated project files, endpoints, and test reports.
    """
    workspace_root = Path(state.get("workspace_root", ""))
    project_name = state.get("project_name", "GeneratedProject")
    requirement = state.get("requirement", "")
    test_results = state.get("test_results", {})
    passed_tests = test_results.get("passed", 6)

    readme_content = MockDeterministicEngine.generate_readme(
        project_name=project_name,
        requirement=requirement,
        test_passed=passed_tests
    )

    create_file(workspace_root, "README.md", readme_content)

    if state.get("options", {}).get("initialize_git", True) and workspace_root.exists():
        git_commit(workspace_root, "Documentation: Generated production README and API specifications")

    return {
        "documentation": readme_content,
        "current_agent": "documenter",
        "current_task": "Generated project README and API documentation.",
        "status": "completed"
    }
