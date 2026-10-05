from fastapi import APIRouter, HTTPException, Query
from backend.app.schemas.schemas import FileNode, FileContent, FileSaveRequest
from backend.app.services.project_service import project_service

router = APIRouter(prefix="/api/projects/{project_id}/files", tags=["files"])

@router.get("", response_model=list)
async def get_project_files(project_id: str):
    """Returns the full recursive directory tree for the Monaco File Explorer."""
    return project_service.get_tree(project_id)

@router.get("/content")
async def get_file_content(project_id: str, path: str = Query(..., description="Relative file path")):
    result = project_service.read_project_file(project_id, path)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "File not found"))
    return result

@router.post("/content")
async def save_file_content(project_id: str, payload: FileSaveRequest):
    result = project_service.write_project_file(project_id, payload.path, payload.content)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Could not save file"))
    return result

@router.delete("/content")
async def delete_file_endpoint(project_id: str, path: str = Query(..., description="Relative file path")):
    result = project_service.delete_project_file(project_id, path)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Could not delete file"))
    return result
