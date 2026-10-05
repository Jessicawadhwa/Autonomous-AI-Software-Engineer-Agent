import pytest
from pathlib import Path
from backend.app.tools.security import validate_workspace_path, is_command_forbidden, is_approval_required, SecurityError

def test_validate_workspace_path_safe(tmp_path):
    safe_path = validate_workspace_path(tmp_path, "app/main.py")
    assert str(safe_path).startswith(str(tmp_path.resolve()))

def test_validate_workspace_path_traversal_attack(tmp_path):
    with pytest.raises(SecurityError):
        validate_workspace_path(tmp_path, "../../outside_file.txt")

def test_validate_workspace_path_absolute_escape(tmp_path):
    with pytest.raises(SecurityError):
        validate_workspace_path(tmp_path, "/etc/passwd")

def test_forbidden_commands():
    forbidden_cmd = "rm -rf /"
    is_bad, reason = is_command_forbidden(forbidden_cmd)
    assert is_bad is True
    assert "strictly forbidden" in reason

    safe_cmd = "pytest tests/ -v"
    is_bad, _ = is_command_forbidden(safe_cmd)
    assert is_bad is False

def test_approval_required_commands():
    pip_cmd = "pip install pandas"
    req, _ = is_approval_required(pip_cmd)
    assert req is True

    safe_cmd = "python app/main.py"
    req, _ = is_approval_required(safe_cmd)
    assert req is False
