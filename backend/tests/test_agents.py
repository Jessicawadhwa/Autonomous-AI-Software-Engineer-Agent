import pytest
from pathlib import Path
from backend.app.agents.mock_engine import MockDeterministicEngine
from backend.app.agents.planner import planner_node
from backend.app.agents.architect import architect_node
from backend.app.agents.coder import coder_node
from backend.app.agents.tester import tester_node as agent_tester_node
from backend.app.agents.debugger import debugger_node
from backend.app.agents.reviewer import reviewer_node
from backend.app.agents.documenter import documenter_node
from backend.app.agents.state import AgentState

@pytest.mark.asyncio
async def test_multi_agent_workflow_cycle(tmp_path):
    # Setup state
    state: AgentState = {
        "project_id": "test_proj_1",
        "run_id": "test_run_1",
        "workspace_root": str(tmp_path),
        "requirement": "Build a FastAPI Task API with SQLite and Pytest",
        "project_name": "TaskMaster",
        "options": {"generate_tests": True, "initialize_git": True, "run_code_review": True},
        "llm_provider": "demo",
        "debug_attempts": 0,
        "max_debug_attempts": 5,
        "files_created": [],
        "git_commits": [],
        "review_results": [],
        "status": "running"
    }

    # 1. Planner
    p_out = await planner_node(state)
    state.update(p_out)
    assert "plan" in state
    assert len(state["plan"]["tasks"]) > 0

    # 2. Architect
    a_out = await architect_node(state)
    state.update(a_out)
    assert "architecture" in state
    assert "tech_stack" in state["architecture"]

    # 3. Coder (with intentional bug for debugging verification)
    c_out = await coder_node(state)
    state.update(c_out)
    assert len(state["files_created"]) > 0
    assert (tmp_path / "app" / "main.py").exists()

    # 4. Tester (Attempt 1: detects the intentional bug)
    t_out = await agent_tester_node(state)
    state.update(t_out)
    assert "test_results" in state
    assert state["test_results"]["total"] > 0
    assert state["test_results"]["failed"] == 1

    # 5. Debugger (Fixes the bug)
    d_out = await debugger_node(state)
    state.update(d_out)
    assert state["debug_attempts"] == 1

    # 6. Tester (Attempt 2: tests pass 100%!)
    t2_out = await agent_tester_node(state)
    state.update(t2_out)
    assert state["test_results"]["failed"] == 0
    assert state["test_results"]["passed"] > 0
    assert state["test_results"]["success"] is True

    # 7. Reviewer
    r_out = await reviewer_node(state)
    state.update(r_out)
    assert len(state["review_results"]) > 0

    # 8. Documenter
    doc_out = await documenter_node(state)
    state.update(doc_out)
    assert (tmp_path / "README.md").exists()
    assert state["status"] == "completed"
