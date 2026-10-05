import os
import fnmatch
from pathlib import Path
from typing import Dict, Any, List, Optional
from backend.app.tools.security import validate_workspace_path, SecurityError

def create_file(workspace_root: Path, rel_path: str, content: str) -> Dict[str, Any]:
    """Creates a new file at rel_path with content. Creates parent directories if needed."""
    try:
        target = validate_workspace_path(workspace_root, rel_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return {
            "success": True,
            "path": rel_path,
            "size": len(content),
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "path": rel_path,
            "error": str(e)
        }

def read_file(workspace_root: Path, rel_path: str) -> Dict[str, Any]:
    """Reads content from a file at rel_path."""
    try:
        target = validate_workspace_path(workspace_root, rel_path)
        if not target.exists():
            return {"success": False, "path": rel_path, "error": f"File not found: {rel_path}"}
        if not target.is_file():
            return {"success": False, "path": rel_path, "error": f"Path is not a file: {rel_path}"}
        
        content = target.read_text(encoding="utf-8", errors="replace")
        return {
            "success": True,
            "path": rel_path,
            "content": content,
            "size": target.stat().st_size,
            "error": None
        }
    except Exception as e:
        return {"success": False, "path": rel_path, "error": str(e)}

def update_file(workspace_root: Path, rel_path: str, content: str) -> Dict[str, Any]:
    """Overwrites an existing file at rel_path."""
    return create_file(workspace_root, rel_path, content)

def delete_file(workspace_root: Path, rel_path: str) -> Dict[str, Any]:
    """Deletes a file or directory at rel_path."""
    try:
        target = validate_workspace_path(workspace_root, rel_path)
        if not target.exists():
            return {"success": False, "path": rel_path, "error": "File or directory not found"}
        
        if target.is_file():
            target.unlink()
        elif target.is_dir():
            import shutil
            shutil.rmtree(target)
            
        return {"success": True, "path": rel_path, "error": None}
    except Exception as e:
        return {"success": False, "path": rel_path, "error": str(e)}

def list_directory(workspace_root: Path, rel_path: str = "") -> Dict[str, Any]:
    """Lists files and folders under rel_path in workspace."""
    try:
        target = validate_workspace_path(workspace_root, rel_path)
        if not target.exists():
            return {"success": False, "error": f"Directory not found: {rel_path}"}
        
        entries = []
        for item in sorted(target.iterdir()):
            if item.name in [".git", "__pycache__", ".pytest_cache", ".venv"]:
                continue
            is_dir = item.is_dir()
            entries.append({
                "name": item.name,
                "path": str(item.relative_to(workspace_root)).replace("\\", "/"),
                "type": "directory" if is_dir else "file",
                "size": item.stat().st_size if not is_dir else None
            })
        return {"success": True, "entries": entries, "error": None}
    except Exception as e:
        return {"success": False, "entries": [], "error": str(e)}

def search_code(workspace_root: Path, query: str, file_glob: str = "*") -> Dict[str, Any]:
    """Searches for text pattern across all project files."""
    try:
        matches = []
        workspace_resolved = workspace_root.resolve()
        for root, dirs, files in os.walk(workspace_resolved):
            # Skip hidden and cache folders
            dirs[:] = [d for d in dirs if d not in [".git", "__pycache__", ".pytest_cache", "node_modules", ".venv"]]
            for file in files:
                if fnmatch.fnmatch(file, file_glob):
                    full_path = Path(root) / file
                    try:
                        content = full_path.read_text(encoding="utf-8", errors="ignore")
                        lines = content.splitlines()
                        for i, line in enumerate(lines, start=1):
                            if query.lower() in line.lower():
                                rel = full_path.relative_to(workspace_resolved)
                                matches.append({
                                    "file": str(rel).replace("\\", "/"),
                                    "line": i,
                                    "content": line.strip()
                                })
                    except Exception:
                        continue
        return {"success": True, "query": query, "matches": matches, "count": len(matches), "error": None}
    except Exception as e:
        return {"success": False, "matches": [], "count": 0, "error": str(e)}

def get_file_tree(workspace_root: Path) -> List[Dict[str, Any]]:
    """Returns a full recursive tree structure for UI file explorer."""
    def build_tree(current_path: Path) -> List[Dict[str, Any]]:
        nodes = []
        if not current_path.exists():
            return nodes
        try:
            items = sorted(current_path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
            for item in items:
                if item.name in [".git", "__pycache__", ".pytest_cache", ".venv"]:
                    continue
                rel_str = str(item.relative_to(workspace_root)).replace("\\", "/")
                if item.is_dir():
                    children = build_tree(item)
                    nodes.append({
                        "name": item.name,
                        "path": rel_str,
                        "type": "directory",
                        "children": children
                    })
                else:
                    nodes.append({
                        "name": item.name,
                        "path": rel_str,
                        "type": "file",
                        "size": item.stat().st_size
                    })
        except Exception:
            pass
        return nodes

    return build_tree(workspace_root)
