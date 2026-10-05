from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field

# Project Schemas
class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = None
    requirement: str = Field(..., min_length=5, description="User requirement in natural language")
    options: Dict[str, Any] = Field(
        default_factory=lambda: {
            "generate_tests": True,
            "generate_docs": True,
            "initialize_git": True,
            "run_code_review": True,
            "enable_mcp": True,
            "auto_approve": True
        }
    )
    provider: Optional[Literal["demo", "openai", "gemini"]] = None
    api_key: Optional[str] = None
    model: Optional[str] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    requirement: str
    status: str
    options: Dict[str, Any]
    workspace_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_run_status: Optional[str] = None
    total_tests_passed: Optional[int] = 0
    total_tests_failed: Optional[int] = 0

    class Config:
        from_attributes = True

# Agent Run Schemas
class AgentRunResponse(BaseModel):
    id: str
    project_id: str
    status: str
    current_agent: Optional[str] = None
    current_task: Optional[str] = None
    debug_iterations: int = 0
    error: Optional[str] = None
    metrics: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AgentMessageSchema(BaseModel):
    id: str
    run_id: str
    project_id: str
    agent_name: str
    message_type: str
    content: str
    data: Dict[str, Any] = Field(default_factory=dict)
    duration_seconds: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Test & Review Schemas
class TestResultSchema(BaseModel):
    id: str
    run_id: str
    project_id: str
    iteration: int
    total: int
    passed: int
    failed: int
    errors: int
    details: Dict[str, Any] = Field(default_factory=dict)
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ReviewFindingSchema(BaseModel):
    id: str
    run_id: str
    project_id: str
    severity: Literal["critical", "high", "medium", "low", "info"]
    file: str
    line: Optional[int] = None
    issue: str
    recommendation: str
    created_at: datetime

    class Config:
        from_attributes = True

# Git Schemas
class GitCommitSchema(BaseModel):
    id: str
    project_id: str
    commit_hash: str
    message: str
    author: str
    timestamp: datetime

    class Config:
        from_attributes = True

# Approval Schemas
class ApprovalRequestSchema(BaseModel):
    id: str
    run_id: str
    project_id: str
    action_type: str
    command: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)
    status: str
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ApprovalDecision(BaseModel):
    decision: Literal["approve", "reject"]

# File Explorer Schemas
class FileNode(BaseModel):
    name: str
    path: str
    type: Literal["file", "directory"]
    size: Optional[int] = None
    children: Optional[List["FileNode"]] = None

class FileContent(BaseModel):
    path: str
    content: str
    size: int
    last_modified: Optional[str] = None

class FileSaveRequest(BaseModel):
    path: str
    content: str

# Settings Schema
class LLMSettings(BaseModel):
    provider: Literal["demo", "openai", "gemini"] = "demo"
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o"
    google_api_key: Optional[str] = None
    gemini_model: str = "gemini-1.5-pro"
    temperature: float = 0.2
    max_tokens: int = 4096
    max_debug_iterations: int = 5
    auto_approve: bool = True

# Dashboard Stats Schema
class DashboardStats(BaseModel):
    total_projects: int = 0
    successful_builds: int = 0
    failed_builds: int = 0
    average_build_time_seconds: float = 0.0
    total_tests_passed: int = 0
    total_agent_runs: int = 0
