import json
import logging
from typing import Dict, Set, Any
from fastapi import WebSocket

logger = logging.getLogger("websocket_manager")

class WebSocketManager:
    def __init__(self):
        # Map project_id -> Set of active WebSocket connections
        self._active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, project_id: str, websocket: WebSocket):
        await websocket.accept()
        if project_id not in self._active_connections:
            self._active_connections[project_id] = set()
        self._active_connections[project_id].add(websocket)
        logger.info(f"WebSocket client connected to project {project_id}. Total: {len(self._active_connections[project_id])}")

    def disconnect(self, project_id: str, websocket: WebSocket):
        if project_id in self._active_connections:
            self._active_connections[project_id].discard(websocket)
            if not self._active_connections[project_id]:
                del self._active_connections[project_id]
        logger.info(f"WebSocket client disconnected from project {project_id}")

    async def broadcast(self, project_id: str, event_type: str, data: Any):
        """Broadcasts a structured JSON event to all listeners of project_id."""
        if project_id not in self._active_connections:
            return
            
        payload = {
            "event": event_type,
            "project_id": project_id,
            "data": data
        }
        message = json.dumps(payload, default=str)
        dead_sockets = set()
        
        for ws in self._active_connections[project_id]:
            try:
                await ws.send_text(message)
            except Exception as e:
                logger.warning(f"Error sending message to websocket: {e}")
                dead_sockets.add(ws)
                
        for ws in dead_sockets:
            self.disconnect(project_id, ws)

ws_manager = WebSocketManager()
