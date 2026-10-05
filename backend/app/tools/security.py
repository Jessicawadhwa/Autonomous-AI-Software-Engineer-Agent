import os
from pathlib import Path
from typing import Tuple, Optional

class SecurityError(Exception):
    """Raised when an operation violates workspace security constraints."""
    pass

# Commands that are strictly forbidden under all circumstances
FORBIDDEN_PATTERNS = [
    "rm -rf /",
    "rm -rf /*",
    "rmdir /s /q c:\\",
    ":(){ :|:& };:",
    "format c:",
    "format /fs",
    "mkfs",
    "dd if=",
    "> /dev/sda",
    "shutdown",
    "reboot",
    "init 0",
    "del /f /s /q c:\\",
    "net user",
    "reg add",
    "reg delete",
    "powershell -encodedcommand",
]

# Commands that require human approval if auto_approve is False
SENSITIVE_PATTERNS = [
    "pip install",
    "npm install",
    "apt-get",
    "curl",
    "wget",
    "rm -rf",
    "del /s",
    "git push",
    "git remote",
    "drop database",
    "delete from",
]

def validate_workspace_path(workspace_root: Path, rel_path: str) -> Path:
    """
    Validates that rel_path resolves strictly within workspace_root.
    Prevents directory traversal attacks and absolute path escapes outside workspace.
    """
    workspace_resolved = workspace_root.resolve()
    clean_str = str(rel_path).strip()
    
    # Check if path attempts absolute jump (leading slash, backslash, or drive letter)
    if clean_str.startswith("/") or clean_str.startswith("\\") or (len(clean_str) > 1 and clean_str[1] == ":"):
        target_path = Path(clean_str).resolve()
    else:
        target_path = (workspace_resolved / clean_str).resolve()
        
    try:
        target_path.relative_to(workspace_resolved)
    except ValueError:
        raise SecurityError(f"Access denied: path '{rel_path}' resolves outside project workspace.")
        
    return target_path

def is_command_forbidden(command: str) -> Tuple[bool, Optional[str]]:
    cmd_lower = command.lower().strip()
    for pattern in FORBIDDEN_PATTERNS:
        if pattern in cmd_lower:
            return True, f"Command contains strictly forbidden pattern: '{pattern}'"
    return False, None

def is_approval_required(command: str, action_type: str = "execute_command") -> Tuple[bool, Optional[str]]:
    cmd_lower = command.lower().strip()
    for pattern in SENSITIVE_PATTERNS:
        if pattern in cmd_lower:
            return True, f"Operation contains sensitive action: '{pattern}'"
    
    if action_type in ["install_package", "delete_files", "network_request"]:
        return True, f"Action type '{action_type}' requires confirmation."
        
    return False, None
