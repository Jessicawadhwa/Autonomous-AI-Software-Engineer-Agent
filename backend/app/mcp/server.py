from typing import Dict, Any, List, Optional
from backend.app.services.project_service import project_service
from backend.app.tools.test_tools import run_project_pytest
from backend.app.tools.command_tools import run_workspace_command

MCP_TOOLS_MANIFEST = [
    {
        "name": "create_project_file",
        "description": "Creates or updates a file in the project workspace with specified content.",
        "parameters": {
            "type": "object",
            "properties": {
                "project_id": {"type": "string", "description": "The unique ID of the target project"},
                "file_path": {"type": "string", "description": "Relative file path inside the project"},
                "content": {"type": "string", "description": "Text content to write to the file"}
            },
            "required": ["project_id", "file_path", "content"]
        }
    },
    {
        "name": "read_project_file",
        "description": "Reads the content of an existing file in the project workspace.",
        "parameters": {
            "type": "object",
            "properties": {
                "project_id": {"type": "string", "description": "The unique ID of the project"},
                "file_path": {"type": "string", "description": "Relative path of the file to read"}
            },
            "required": ["project_id", "file_path"]
        }
    },
    {
        "name": "run_project_tests",
        "description": "Executes pytest inside the project workspace and returns structured results.",
        "parameters": {
            "type": "object",
            "properties": {
                "project_id": {"type": "string", "description": "The unique ID of the project"}
            },
            "required": ["project_id"]
        }
    },
    {
        "name": "get_project_structure",
        "description": "Retrieves the full directory tree structure of a project workspace.",
        "parameters": {
            "type": "object",
            "properties": {
                "project_id": {"type": "string", "description": "The unique ID of the project"}
            },
            "required": ["project_id"]
        }
    },
    {
        "name": "execute_sandboxed_command",
        "description": "Executes a shell command inside the project workspace under security constraints.",
        "parameters": {
            "type": "object",
            "properties": {
                "project_id": {"type": "string", "description": "The unique ID of the project"},
                "command": {"type": "string", "description": "Shell command to run"}
            },
            "required": ["project_id", "command"]
        }
    }
]

class MCPServer:
    @staticmethod
    def list_tools() -> List[Dict[str, Any]]:
        return MCP_TOOLS_MANIFEST

    @staticmethod
    async def call_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        project_id = arguments.get("project_id")
        if not project_id:
            return {"error": "Missing required parameter 'project_id'"}

        p_dir = project_service.get_project_dir(project_id)

        if name == "create_project_file":
            return project_service.write_project_file(
                project_id,
                arguments.get("file_path", ""),
                arguments.get("content", "")
            )

        elif name == "read_project_file":
            return project_service.read_project_file(
                project_id,
                arguments.get("file_path", "")
            )

        elif name == "run_project_tests":
            return run_project_pytest(p_dir)

        elif name == "get_project_structure":
            return {"tree": project_service.get_tree(project_id)}

        elif name == "execute_sandboxed_command":
            return run_workspace_command(p_dir, arguments.get("command", ""))

        else:
            return {"error": f"Unknown tool: {name}"}

mcp_server = MCPServer()
