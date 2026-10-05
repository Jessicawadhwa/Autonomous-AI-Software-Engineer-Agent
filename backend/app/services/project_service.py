import io
import shutil
import zipfile
from pathlib import Path
from typing import Optional, Dict, Any, List
from backend.app.config import settings
from backend.app.tools.workspace_tools import (
    create_file,
    read_file,
    update_file,
    delete_file,
    get_file_tree
)
from backend.app.tools.git_tools import git_init, git_log, git_status, git_diff

class ProjectService:
    @staticmethod
    def get_project_dir(project_id: str) -> Path:
        p_dir = settings.WORKSPACE_ROOT / project_id
        p_dir.mkdir(parents=True, exist_ok=True)
        return p_dir

    @classmethod
    def initialize_workspace(cls, project_id: str) -> Path:
        p_dir = cls.get_project_dir(project_id)
        git_init(p_dir)
        return p_dir

    @classmethod
    def get_tree(cls, project_id: str) -> List[Dict[str, Any]]:
        p_dir = cls.get_project_dir(project_id)
        return get_file_tree(p_dir)

    @classmethod
    def read_project_file(cls, project_id: str, rel_path: str) -> Dict[str, Any]:
        p_dir = cls.get_project_dir(project_id)
        return read_file(p_dir, rel_path)

    @classmethod
    def write_project_file(cls, project_id: str, rel_path: str, content: str) -> Dict[str, Any]:
        p_dir = cls.get_project_dir(project_id)
        return update_file(p_dir, rel_path, content)

    @classmethod
    def delete_project_file(cls, project_id: str, rel_path: str) -> Dict[str, Any]:
        p_dir = cls.get_project_dir(project_id)
        return delete_file(p_dir, rel_path)

    @classmethod
    def get_git_info(cls, project_id: str) -> Dict[str, Any]:
        p_dir = cls.get_project_dir(project_id)
        return {
            "status": git_status(p_dir),
            "log": git_log(p_dir),
            "diff": git_diff(p_dir)
        }

    @classmethod
    def export_as_zip(cls, project_id: str, project_name: str) -> io.BytesIO:
        """Packages the project directory (excluding cache/git) into an in-memory zip archive."""
        p_dir = cls.get_project_dir(project_id)
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for item in p_dir.rglob("*"):
                if any(part in [".git", "__pycache__", ".pytest_cache", ".venv"] for part in item.parts):
                    continue
                if item.is_file():
                    arcname = f"{project_name}/{item.relative_to(p_dir)}"
                    zip_file.write(item, arcname=arcname)
                    
        zip_buffer.seek(0)
        return zip_buffer

    @classmethod
    def delete_project_workspace(cls, project_id: str):
        p_dir = settings.WORKSPACE_ROOT / project_id
        if p_dir.exists():
            shutil.rmtree(p_dir, ignore_errors=True)

project_service = ProjectService()
