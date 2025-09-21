"""
WebSocket endpoint for real-time updates.
"""
import json
import logging
from typing import Dict, Any

from fastapi import WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"WebSocket connection established for client: {client_id}")
    
    def disconnect(self, client_id: str):
        """Remove a WebSocket connection."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"WebSocket connection closed for client: {client_id}")
    
    async def send_personal_message(self, message: str, client_id: str):
        """Send a message to a specific client."""
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            if websocket.client_state == WebSocketState.CONNECTED:
                try:
                    await websocket.send_text(message)
                except Exception as e:
                    logger.error(f"Error sending message to {client_id}: {e}")
                    self.disconnect(client_id)
    
    async def broadcast(self, message: str):
        """Broadcast a message to all connected clients."""
        disconnected_clients = []
        for client_id, websocket in self.active_connections.items():
            if websocket.client_state == WebSocketState.CONNECTED:
                try:
                    await websocket.send_text(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to {client_id}: {e}")
                    disconnected_clients.append(client_id)
            else:
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)


# Global connection manager instance
manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time communication.
    
    Handles WebSocket connections and provides real-time updates
    for data structure changes, schema updates, and system events.
    """
    client_id = None
    try:
        # Get client ID from query parameters or generate one
        client_id = websocket.query_params.get("client_id", f"client_{id(websocket)}")
        
        await manager.connect(websocket, client_id)
        
        # Send welcome message
        welcome_msg = {
            "type": "connection",
            "status": "connected",
            "client_id": client_id,
            "message": "WebSocket connection established"
        }
        await websocket.send_text(json.dumps(welcome_msg))
        
        # Listen for messages from client
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                await handle_websocket_message(websocket, client_id, message)
                
            except json.JSONDecodeError:
                error_msg = {
                    "type": "error",
                    "message": "Invalid JSON format"
                }
                await websocket.send_text(json.dumps(error_msg))
                
    except WebSocketDisconnect:
        if client_id:
            manager.disconnect(client_id)
            logger.info(f"WebSocket client {client_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
        if client_id:
            manager.disconnect(client_id)


async def handle_websocket_message(websocket: WebSocket, client_id: str, message: Dict[str, Any]):
    """
    Handle incoming WebSocket messages from clients.
    
    Args:
        websocket: The WebSocket connection
        client_id: The client identifier
        message: The parsed JSON message
    """
    message_type = message.get("type", "unknown")
    
    try:
        if message_type == "ping":
            # Respond to ping with pong
            response = {
                "type": "pong",
                "timestamp": message.get("timestamp")
            }
            await websocket.send_text(json.dumps(response))
            
        elif message_type == "subscribe":
            # Handle subscription to specific topics
            topic = message.get("topic", "general")
            response = {
                "type": "subscription",
                "topic": topic,
                "status": "subscribed",
                "message": f"Subscribed to {topic}"
            }
            await websocket.send_text(json.dumps(response))
            
        elif message_type == "unsubscribe":
            # Handle unsubscription from topics
            topic = message.get("topic", "general")
            response = {
                "type": "subscription",
                "topic": topic,
                "status": "unsubscribed",
                "message": f"Unsubscribed from {topic}"
            }
            await websocket.send_text(json.dumps(response))
            
        elif message_type == "echo":
            # Echo message back to client
            response = {
                "type": "echo",
                "original": message,
                "client_id": client_id
            }
            await websocket.send_text(json.dumps(response))
            
        else:
            # Unknown message type
            response = {
                "type": "error",
                "message": f"Unknown message type: {message_type}"
            }
            await websocket.send_text(json.dumps(response))
            
    except Exception as e:
        logger.error(f"Error handling WebSocket message from {client_id}: {e}")
        error_response = {
            "type": "error",
            "message": "Internal server error"
        }
        await websocket.send_text(json.dumps(error_response))


async def notify_data_change(change_type: str, data: Dict[str, Any]):
    """
    Notify all connected clients about data changes.
    
    Args:
        change_type: Type of change (create, update, delete)
        data: The changed data
    """
    notification = {
        "type": "data_change",
        "change_type": change_type,
        "data": data,
        "timestamp": str(data.get("updated_at", ""))
    }
    await manager.broadcast(json.dumps(notification))


async def notify_schema_change(schema_id: int, change_type: str):
    """
    Notify all connected clients about schema changes.
    
    Args:
        schema_id: ID of the changed schema
        change_type: Type of change (create, update, delete)
    """
    notification = {
        "type": "schema_change",
        "schema_id": schema_id,
        "change_type": change_type,
        "timestamp": str()
    }
    await manager.broadcast(json.dumps(notification))


async def notify_structure_change(structure_id: int, change_type: str):
    """
    Notify all connected clients about structure changes.
    
    Args:
        structure_id: ID of the changed structure
        change_type: Type of change (create, update, delete)
    """
    notification = {
        "type": "structure_change",
        "structure_id": structure_id,
        "change_type": change_type,
        "timestamp": str()
    }
    await manager.broadcast(json.dumps(notification))
