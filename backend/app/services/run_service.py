import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import select, update
from backend.app.database import AsyncSessionLocal
from backend.app.models.models import (
    Project,
    AgentRun,
    AgentMessage,
    TestResult,
    ReviewFinding,
    GitCommit,
    ApprovalRequest
)
from backend.app.services.project_service import project_service
from backend.app.services.websocket_manager import ws_manager
from backend.app.agents.graph import agent_executor
from backend.app.agents.state import AgentState

logger = logging.getLogger("run_service")

class RunService:
    def __init__(self):
        self._active_tasks: Dict[str, asyncio.Task] = {}
        self._pending_approvals: Dict[str, asyncio.Event] = {}

    async def start_run(
        self,
        project_id: str,
        provider: Optional[str] = "demo",
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ) -> str:
        async with AsyncSessionLocal() as session:
            # Fetch project
            stmt = select(Project).where(Project.id == project_id)
            result = await session.execute(stmt)
            project = result.scalar_one_or_none()
            if not project:
                raise ValueError("Project not found")

            # Initialize workspace
            workspace_dir = project_service.initialize_workspace(project_id)
            project.workspace_path = str(workspace_dir)
            project.status = "running"

            # Create AgentRun
            run = AgentRun(
                project_id=project_id,
                status="running",
                current_agent="planner",
                current_task="Starting agent orchestration workflow...",
                metrics={"start_time": datetime.utcnow().isoformat()}
            )
            session.add(run)
            await session.commit()
            await session.refresh(run)
            run_id = run.id

        # Launch background execution task
        task = asyncio.create_task(
            self._execute_workflow(
                run_id=run_id,
                project_id=project_id,
                project_name=project.name,
                requirement=project.requirement,
                options=project.options or {},
                workspace_dir=str(workspace_dir),
                provider=provider or "demo",
                api_key=api_key,
                model=model
            )
        )
        self._active_tasks[run_id] = task
        return run_id

    async def stop_run(self, run_id: str):
        if run_id in self._active_tasks:
            task = self._active_tasks[run_id]
            task.cancel()
            del self._active_tasks[run_id]

        async with AsyncSessionLocal() as session:
            stmt = update(AgentRun).where(AgentRun.id == run_id).values(
                status="stopped",
                completed_at=datetime.utcnow()
            )
            await session.execute(stmt)
            await session.commit()

    async def approve_action(self, approval_id: str, decision: str):
        async with AsyncSessionLocal() as session:
            stmt = select(ApprovalRequest).where(ApprovalRequest.id == approval_id)
            result = await session.execute(stmt)
            req = result.scalar_one_or_none()
            if not req:
                raise ValueError("Approval request not found")

            req.status = "approved" if decision == "approve" else "rejected"
            req.resolved_at = datetime.utcnow()
            await session.commit()

            # Resume execution event
            if req.run_id in self._pending_approvals:
                self._pending_approvals[req.run_id].set()

            await ws_manager.broadcast(
                req.project_id,
                "approval_resolved",
                {"approval_id": approval_id, "status": req.status}
            )

    async def _execute_workflow(
        self,
        run_id: str,
        project_id: str,
        project_name: str,
        requirement: str,
        options: Dict[str, Any],
        workspace_dir: str,
        provider: str,
        api_key: Optional[str],
        model: Optional[str]
    ):
        initial_state: AgentState = {
            "project_id": project_id,
            "run_id": run_id,
            "workspace_root": workspace_dir,
            "requirement": requirement,
            "project_name": project_name,
            "options": options,
            "llm_provider": provider,
            "api_key": api_key,
            "model": model,
            "temperature": 0.2,
            "debug_attempts": 0,
            "max_debug_attempts": 5,
            "files_created": [],
            "git_commits": [],
            "review_results": [],
            "status": "running"
        }

        try:
            # Broadcast start
            await ws_manager.broadcast(project_id, "run_started", {"run_id": run_id, "status": "running"})

            # Stream LangGraph state graph execution
            async for step_output in agent_executor.astream(initial_state):
                for node_name, node_state in step_output.items():
                    current_agent = node_state.get("current_agent", node_name)
                    current_task = node_state.get("current_task", f"Executing {node_name}")
                    
                    # Update database run state
                    async with AsyncSessionLocal() as session:
                        stmt = update(AgentRun).where(AgentRun.id == run_id).values(
                            current_agent=current_agent,
                            current_task=current_task,
                            debug_iterations=node_state.get("debug_attempts", 0)
                        )
                        await session.execute(stmt)

                        # Record message
                        msg = AgentMessage(
                            run_id=run_id,
                            project_id=project_id,
                            agent_name=current_agent,
                            message_type="agent_step",
                            content=current_task,
                            data={"node": node_name}
                        )
                        session.add(msg)

                        # If test node completed, persist test results
                        if node_name == "tester" and "test_results" in node_state:
                            tr = node_state["test_results"]
                            db_test = TestResult(
                                run_id=run_id,
                                project_id=project_id,
                                iteration=node_state.get("debug_attempts", 0) + 1,
                                total=tr.get("total", 0),
                                passed=tr.get("passed", 0),
                                failed=tr.get("failed", 0),
                                errors=tr.get("errors", 0),
                                details=tr,
                                stdout=tr.get("stdout"),
                                stderr=tr.get("stderr")
                            )
                            session.add(db_test)
                            
                            # Broadcast real terminal output & test diagnostics
                            await ws_manager.broadcast(
                                project_id,
                                "terminal_output",
                                {
                                    "command": "pytest tests/ -v",
                                    "stdout": tr.get("stdout", ""),
                                    "stderr": tr.get("stderr", "")
                                }
                            )
                            await ws_manager.broadcast(project_id, "test_results", tr)

                        # If reviewer node completed, persist review findings
                        if node_name == "reviewer" and "review_results" in node_state:
                            for item in node_state["review_results"]:
                                rf = ReviewFinding(
                                    run_id=run_id,
                                    project_id=project_id,
                                    severity=item.get("severity", "medium"),
                                    file=item.get("file", ""),
                                    line=item.get("line"),
                                    issue=item.get("issue", ""),
                                    recommendation=item.get("recommendation", "")
                                )
                                session.add(rf)
                            await ws_manager.broadcast(project_id, "review_results", node_state["review_results"])

                        # Sync git commits
                        git_info = project_service.get_git_info(project_id)
                        for c in git_info.get("log", []):
                            stmt_c = select(GitCommit).where(GitCommit.commit_hash == c["commit_hash"])
                            exists = (await session.execute(stmt_c)).scalar_one_or_none()
                            if not exists:
                                session.add(GitCommit(
                                    project_id=project_id,
                                    commit_hash=c["commit_hash"],
                                    message=c["message"],
                                    author=c["author"],
                                    timestamp=datetime.utcnow()
                                ))

                        await session.commit()

                    # Broadcast real-time step update to UI
                    await ws_manager.broadcast(
                        project_id,
                        "agent_step",
                        {
                            "agent": current_agent,
                            "task": current_task,
                            "node": node_name,
                            "debug_attempts": node_state.get("debug_attempts", 0),
                            "tree": project_service.get_tree(project_id),
                            "git": project_service.get_git_info(project_id)
                        }
                    )

                    # Micro delay for smooth UI timeline animation
                    await asyncio.sleep(0.8)

            # Workflow successfully completed
            async with AsyncSessionLocal() as session:
                stmt_run = update(AgentRun).where(AgentRun.id == run_id).values(
                    status="success",
                    completed_at=datetime.utcnow(),
                    current_agent="completed",
                    current_task="Project generated, tested, and reviewed successfully."
                )
                await session.execute(stmt_run)

                stmt_proj = update(Project).where(Project.id == project_id).values(
                    status="completed"
                )
                await session.execute(stmt_proj)
                await session.commit()

            await ws_manager.broadcast(
                project_id,
                "run_completed",
                {
                    "run_id": run_id,
                    "status": "success",
                    "tree": project_service.get_tree(project_id),
                    "git": project_service.get_git_info(project_id)
                }
            )

        except asyncio.CancelledError:
            logger.info(f"Run {run_id} was cancelled.")
        except Exception as e:
            logger.exception(f"Error during agent execution for run {run_id}: {e}")
            async with AsyncSessionLocal() as session:
                stmt = update(AgentRun).where(AgentRun.id == run_id).values(
                    status="failed",
                    error=str(e),
                    completed_at=datetime.utcnow()
                )
                await session.execute(stmt)
                stmt_proj = update(Project).where(Project.id == project_id).values(
                    status="failed"
                )
                await session.execute(stmt_proj)
                await session.commit()

            await ws_manager.broadcast(
                project_id,
                "run_failed",
                {"run_id": run_id, "error": str(e)}
            )
        finally:
            if run_id in self._active_tasks:
                del self._active_tasks[run_id]

run_service = RunService()
