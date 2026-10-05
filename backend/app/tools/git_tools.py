import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from backend.app.tools.command_tools import run_workspace_command

def git_init(workspace_root: Path) -> Dict[str, Any]:
    """Initializes a git repo and configures a default author."""
    r1 = run_workspace_command(workspace_root, "git init")
    if not r1["success"]:
        return r1
    
    # Configure user name/email locally
    run_workspace_command(workspace_root, 'git config user.name "Autonomous AI Engineer"')
    run_workspace_command(workspace_root, 'git config user.email "agent@autonomous.engineer"')
    
    # Create .gitignore if none exists
    gitignore_path = workspace_root / ".gitignore"
    if not gitignore_path.exists():
        gitignore_content = "__pycache__/\n*.pyc\n.pytest_cache/\n.env\n*.db\n.venv/\n"
        gitignore_path.write_text(gitignore_content, encoding="utf-8")
        
    return {"success": True, "output": "Git repository initialized successfully"}

def git_commit(workspace_root: Path, message: str, author: str = "Autonomous AI Engineer") -> Dict[str, Any]:
    """Adds all files and creates a git commit."""
    # Stage all
    r_add = run_workspace_command(workspace_root, "git add -A")
    if not r_add["success"]:
        return r_add
    
    # Escape message double quotes
    escaped_msg = message.replace('"', '\\"')
    r_commit = run_workspace_command(workspace_root, f'git commit -m "{escaped_msg}" --allow-empty')
    
    # Get latest commit hash
    r_hash = run_workspace_command(workspace_root, "git rev-parse --short HEAD")
    commit_hash = r_hash.get("stdout", "").strip() or "HEAD"
    
    return {
        "success": r_commit["success"],
        "commit_hash": commit_hash,
        "message": message,
        "stdout": r_commit.get("stdout", ""),
        "error": r_commit.get("error")
    }

def git_status(workspace_root: Path) -> Dict[str, Any]:
    """Gets short status of changed/untracked files."""
    r = run_workspace_command(workspace_root, "git status --short")
    lines = [line.strip() for line in r.get("stdout", "").splitlines() if line.strip()]
    return {
        "success": r["success"],
        "has_changes": len(lines) > 0,
        "changes": lines,
        "raw": r.get("stdout", "")
    }

def git_log(workspace_root: Path, limit: int = 10) -> List[Dict[str, Any]]:
    """Gets recent git commits in reverse chronological order."""
    r = run_workspace_command(workspace_root, f'git log -n {limit} --pretty=format:"%h|%an|%ad|%s" --date=iso')
    if not r["success"] or not r.get("stdout"):
        return []
    
    commits = []
    for line in r["stdout"].splitlines():
        parts = line.strip().split("|", 3)
        if len(parts) == 4:
            commits.append({
                "commit_hash": parts[0],
                "author": parts[1],
                "timestamp": parts[2],
                "message": parts[3]
            })
    return commits

def git_diff(workspace_root: Path, commit_hash: Optional[str] = None) -> str:
    """Gets git diff of unstaged changes or against a specific commit."""
    cmd = f"git diff {commit_hash}" if commit_hash else "git diff HEAD"
    r = run_workspace_command(workspace_root, cmd)
    return r.get("stdout", "")
