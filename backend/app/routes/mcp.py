from fastapi import APIRouter
from typing import Dict, Any
from backend.app.mcp.server import mcp_server

router = APIRouter(prefix="/api/mcp", tags=["mcp"])

@router.get("/tools")
async def list_mcp_tools():
    """Returns list of MCP tools exposed by the agent workspace."""
    return {"tools": mcp_server.list_tools()}

@router.post("/call")
async def call_mcp_tool(payload: Dict[str, Any]):
    """Executes an MCP tool call."""
    name = payload.get("name", "")
    args = payload.get("arguments", {})
    result = await mcp_server.call_tool(name, args)
    return {"result": result}
