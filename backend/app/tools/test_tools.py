import re
import sys
from pathlib import Path
from typing import Dict, Any, List
from backend.app.tools.command_tools import run_workspace_command

def run_project_pytest(
    workspace_root: Path,
    test_path: str = "tests",
    timeout: int = 45
) -> Dict[str, Any]:
    """
    Executes pytest inside the generated project workspace and parses test outputs.
    """
    # Use current python executable to guarantee pytest is executed with the project PYTHONPATH
    python_exe = sys.executable
    cmd = f'"{python_exe}" -m pytest {test_path} -v --tb=short'
    
    cmd_result = run_workspace_command(workspace_root, cmd, timeout=timeout)
    stdout = cmd_result.get("stdout", "")
    stderr = cmd_result.get("stderr", "")
    
    # Parse pytest output
    passed_count = 0
    failed_count = 0
    error_count = 0
    total_count = 0
    failures: List[Dict[str, str]] = []

    # Regex patterns for pytest summary lines
    # e.g.: "==== 3 passed, 1 failed in 0.12s ====" or "==== 5 passed in 0.05s ===="
    summary_match = re.search(r"=+\s*(.*?)\s*=+\s*$", stdout, re.MULTILINE)
    
    passed_m = re.search(r"(\d+)\s+passed", stdout)
    if passed_m:
        passed_count = int(passed_m.group(1))
        
    failed_m = re.search(r"(\d+)\s+failed", stdout)
    if failed_m:
        failed_count = int(failed_m.group(1))
        
    error_m = re.search(r"(\d+)\s+error", stdout)
    if error_m:
        error_count = int(error_m.group(1))

    total_count = passed_count + failed_count + error_count

    # Extract individual failure blocks
    if failed_count > 0 or error_count > 0:
        # Look for FAILURES / ERRORS sections
        fail_blocks = re.findall(r"_{3,}\s*(.*?)\s*_{3,}\n(.*?)(?=\n_{3,}|\n=+|$)", stdout, re.DOTALL)
        for name, details in fail_blocks:
            failures.append({
                "test_name": name.strip(),
                "traceback": details.strip()
            })
            
        if not failures and (failed_count > 0 or error_count > 0):
            # Fallback snippet
            failures.append({
                "test_name": "Test Run Failure",
                "traceback": (stdout + "\n" + stderr).strip()[:1000]
            })

    success = (cmd_result["success"] or (failed_count == 0 and error_count == 0 and passed_count > 0)) and total_count > 0

    return {
        "success": success,
        "exit_code": cmd_result.get("exit_code", 0),
        "total": total_count,
        "passed": passed_count,
        "failed": failed_count,
        "errors": error_count,
        "failures": failures,
        "duration": cmd_result.get("duration", 0.0),
        "stdout": stdout,
        "stderr": stderr,
        "raw_error": cmd_result.get("error")
    }
