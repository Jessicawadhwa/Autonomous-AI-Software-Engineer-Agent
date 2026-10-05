import os
import sys
import time
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from backend.app.config import settings
from backend.app.tools.security import is_command_forbidden

def run_workspace_command(
    workspace_root: Path,
    command: str,
    timeout: Optional[int] = None,
    extra_env: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Executes a shell command in the context of the workspace directory.
    Enforces timeout, output size limit, and security checks.
    """
    forbidden, reason = is_command_forbidden(command)
    if forbidden:
        return {
            "success": False,
            "exit_code": -1,
            "stdout": "",
            "stderr": f"Security Violation: {reason}",
            "duration": 0.0,
            "error": "SECURITY_VIOLATION"
        }

    timeout_val = timeout or settings.COMMAND_TIMEOUT_SECONDS
    workspace_resolved = str(workspace_root.resolve())
    
    # Prepare sanitized environment
    env = os.environ.copy()
    env["PYTHONPATH"] = workspace_resolved + os.pathsep + env.get("PYTHONPATH", "")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    if extra_env:
        env.update(extra_env)

    start_time = time.time()
    try:
        # Run subprocess with timeout
        result = subprocess.run(
            command,
            cwd=workspace_resolved,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout_val,
            env=env
        )
        duration = round(time.time() - start_time, 2)
        
        stdout = result.stdout[:settings.MAX_OUTPUT_SIZE_BYTES]
        stderr = result.stderr[:settings.MAX_OUTPUT_SIZE_BYTES]
        
        return {
            "success": result.returncode == 0,
            "exit_code": result.returncode,
            "stdout": stdout,
            "stderr": stderr,
            "duration": duration,
            "error": None if result.returncode == 0 else f"Command exited with code {result.returncode}"
        }
    except subprocess.TimeoutExpired:
        duration = round(time.time() - start_time, 2)
        return {
            "success": False,
            "exit_code": -1,
            "stdout": "",
            "stderr": f"Execution timed out after {timeout_val} seconds.",
            "duration": duration,
            "error": "TIMEOUT"
        }
    except Exception as e:
        duration = round(time.time() - start_time, 2)
        return {
            "success": False,
            "exit_code": -1,
            "stdout": "",
            "stderr": str(e),
            "duration": duration,
            "error": str(e)
        }
