import json
from typing import Dict, Any
import asyncio
from fastapi import FastAPI, WebSocket
from redis.asyncio import Redis
from datetime import datetime


class IntegrationHub:
    def __init__(self):
        self.app = FastAPI()
        self.redis = Redis()
        self.active_connections: Dict[str, WebSocket] = {}
        self.setup_routes()

    def setup_routes(self):
        @self.app.websocket("/ws/{game_id}")
        async def websocket_endpoint(websocket: WebSocket, game_id: str):
            await self.handle_websocket_connection(websocket, game_id)

    async def handle_websocket_connection(self, websocket: WebSocket, game_id: str):
        await websocket.accept()
        self.active_connections[game_id] = websocket

        try:
            while True:
                data = await websocket.receive_json()
                await self.process_websocket_message(game_id, data)
        except Exception as e:
            print(f"WebSocket error: {e}")
        finally:
            del self.active_connections[game_id]

    async def process_websocket_message(self, game_id: str, data: Dict):
        """Process incoming WebSocket messages."""
        event = {
            "game_id": game_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        }

        # Publish to appropriate channels
        await self.redis.publish(f"game:{game_id}", json.dumps(event))

        # Handle different message types
        if data.get("type") == "move":
            await self.handle_move_event(game_id, data)
        elif data.get("type") == "behavioral":
            await self.handle_behavioral_event(game_id, data)
