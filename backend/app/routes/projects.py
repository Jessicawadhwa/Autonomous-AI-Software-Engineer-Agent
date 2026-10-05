from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from backend.app.database import get_db
from backend.app.models.models import (
    Project,
    AgentRun,
    AgentMessage,
    TestResult,
    ReviewFinding,
    GitCommit,
    ApprovalRequest
)
from backend.app.schemas.schemas import (
    ProjectCreate,
    ProjectResponse,
    AgentRunResponse,
    ApprovalDecision,
    DashboardStats
)
from backend.app.services.project_service import project_service
from backend.app.services.run_service import run_service

router = APIRouter(prefix="/api/projects", tags=["projects"])

@router.get("", response_model=List[ProjectResponse])
async def list_projects(db: AsyncSession = Depends(get_db)):
    stmt = select(Project).order_by(desc(Project.created_at))
    result = await db.execute(stmt)
    projects = result.scalars().all()
    
    responses = []
    for p in projects:
        # Get latest run stats
        run_stmt = select(AgentRun).where(AgentRun.project_id == p.id).order_by(desc(AgentRun.created_at)).limit(1)
        latest_run = (await db.execute(run_stmt)).scalar_one_or_none()
        
        # Count test stats
        test_stmt = select(
            func.max(TestResult.passed).label("passed"),
            func.max(TestResult.failed).label("failed")
        ).where(TestResult.project_id == p.id)
        test_stats = (await db.execute(test_stmt)).first()
        
        responses.append(ProjectResponse(
            id=p.id,
            name=p.name,
            description=p.description,
            requirement=p.requirement,
            status=p.status,
            options=p.options or {},
            workspace_path=p.workspace_path,
            created_at=p.created_at,
            updated_at=p.updated_at,
            last_run_status=latest_run.status if latest_run else None,
            total_tests_passed=test_stats.passed if test_stats and test_stats.passed else 0,
            total_tests_failed=test_stats.failed if test_stats and test_stats.failed else 0
        ))
    return responses

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(req: ProjectCreate, db: AsyncSession = Depends(get_db)):
    project = Project(
        name=req.name,
        description=req.description,
        requirement=req.requirement,
        options=req.options
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)

    # Initialize workspace filesystem
    p_dir = project_service.initialize_workspace(project.id)
    project.workspace_path = str(p_dir)
    await db.commit()

    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        requirement=project.requirement,
        status=project.status,
        options=project.options or {},
        workspace_path=project.workspace_path,
        created_at=project.created_at,
        updated_at=project.updated_at
    )

@router.get("/{project_id}")
async def get_project_details(project_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Project).where(Project.id == project_id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Fetch runs
    runs_stmt = select(AgentRun).where(AgentRun.project_id == project_id).order_by(desc(AgentRun.created_at))
    runs = (await db.execute(runs_stmt)).scalars().all()

    # Fetch test results
    tests_stmt = select(TestResult).where(TestResult.project_id == project_id).order_by(desc(TestResult.created_at))
    tests = (await db.execute(tests_stmt)).scalars().all()

    # Fetch review findings
    reviews_stmt = select(ReviewFinding).where(ReviewFinding.project_id == project_id).order_by(desc(ReviewFinding.created_at))
    reviews = (await db.execute(reviews_stmt)).scalars().all()

    # Fetch approvals
    approvals_stmt = select(ApprovalRequest).where(ApprovalRequest.project_id == project_id).order_by(desc(ApprovalRequest.created_at))
    approvals = (await db.execute(approvals_stmt)).scalars().all()

    # Fetch git commits
    git_info = project_service.get_git_info(project_id)
    tree = project_service.get_tree(project_id)

    return {
        "project": {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "requirement": project.requirement,
            "status": project.status,
            "options": project.options or {},
            "workspace_path": project.workspace_path,
            "created_at": project.created_at,
            "updated_at": project.updated_at
        },
        "runs": runs,
        "tests": tests,
        "reviews": reviews,
        "approvals": approvals,
        "git": git_info,
        "tree": tree
    }

@router.delete("/{project_id}")
async def delete_project(project_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Project).where(Project.id == project_id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Remove workspace directory from disk
    project_service.delete_project_workspace(project_id)

    # Delete DB records (cascade will clean children)
    await db.delete(project)
    await db.commit()
    return {"success": True, "message": "Project deleted successfully"}

@router.post("/{project_id}/run")
async def start_project_run(
    project_id: str,
    payload: Optional[Dict[str, Any]] = None,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Project).where(Project.id == project_id)
    project = (await db.execute(stmt)).scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    provider = payload.get("provider", "demo") if payload else "demo"
    api_key = payload.get("api_key") if payload else None
    model = payload.get("model") if payload else None

    run_id = await run_service.start_run(
        project_id=project_id,
        provider=provider,
        api_key=api_key,
        model=model
    )
    return {"success": True, "run_id": run_id, "status": "started"}

@router.post("/{project_id}/stop")
async def stop_project_run(project_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(AgentRun).where(AgentRun.project_id == project_id, AgentRun.status == "running").order_by(desc(AgentRun.created_at)).limit(1)
    active_run = (await db.execute(stmt)).scalar_one_or_none()
    if active_run:
        await run_service.stop_run(active_run.id)
    return {"success": True, "status": "stopped"}

@router.post("/{project_id}/approvals/{approval_id}")
async def resolve_approval(project_id: str, approval_id: str, body: ApprovalDecision):
    await run_service.approve_action(approval_id, body.decision)
    return {"success": True, "decision": body.decision}

@router.get("/{project_id}/download")
async def download_project_zip(project_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Project).where(Project.id == project_id)
    project = (await db.execute(stmt)).scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    zip_bytes = project_service.export_as_zip(project_id, project.name)
    sanitized_name = "".join(c for c in project.name if c.isalnum() or c in (' ', '_', '-')).rstrip()
    filename = f"{sanitized_name or 'project'}.zip"

    return StreamingResponse(
        zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    total_projects = (await db.execute(select(func.count(Project.id)))).scalar() or 0
    successful_builds = (await db.execute(select(func.count(Project.id)).where(Project.status == "completed"))).scalar() or 0
    failed_builds = (await db.execute(select(func.count(Project.id)).where(Project.status == "failed"))).scalar() or 0
    total_runs = (await db.execute(select(func.count(AgentRun.id)))).scalar() or 0
    
    test_passed_sum = (await db.execute(select(func.sum(TestResult.passed)))).scalar() or 0

    return DashboardStats(
        total_projects=total_projects,
        successful_builds=successful_builds,
        failed_builds=failed_builds,
        average_build_time_seconds=14.2,
        total_tests_passed=test_passed_sum,
        total_agent_runs=total_runs
    )
