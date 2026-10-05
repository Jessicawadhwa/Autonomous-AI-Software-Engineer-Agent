from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict, total=False):
    project_id: str
    run_id: str
    workspace_root: str
    requirement: str
    project_name: str
    options: Dict[str, Any]
    
    # LLM config
    llm_provider: str
    api_key: Optional[str]
    model: Optional[str]
    temperature: float
    
    # Workflow intermediate artifacts
    plan: Dict[str, Any]
    architecture: Dict[str, Any]
    files_created: List[str]
    current_task: Optional[str]
    current_agent: str
    
    # Testing & Debugging
    test_results: Dict[str, Any]
    debug_attempts: int
    max_debug_attempts: int
    
    # Review & Documentation
    review_results: List[Dict[str, Any]]
    documentation: str
    git_commits: List[str]
    
    # Human-in-the-loop & status
    pending_approval: Optional[Dict[str, Any]]
    status: str  # running, completed, failed, paused
    error: Optional[str]
