from typing import Dict, Any, List
import asyncio
from datetime import datetime
import json
from redis import Redis
from dataclasses import dataclass


@dataclass
class GameEvent:
    game_id: str
    event_type: str
    timestamp: datetime
    data: Dict[str, Any]
    source_service: str


class EventProcessor:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.processors: Dict[str, callable] = {}
        self.event_buffer: List[GameEvent] = []
        self.buffer_size = 100

    async def process_event(self, event: GameEvent):
        """Process a single game event."""
        # Add to buffer for batch processing
        self.event_buffer.append(event)

        # Process buffer if full
        if len(self.event_buffer) >= self.buffer_size:
            await self.process_buffer()

        # Process individual event
        if processor := self.processors.get(event.event_type):
            try:
                result = await processor(event)
                await self.publish_result(result)
            except Exception as e:
                await self.handle_processing_error(event, e)

    async def process_buffer(self):
        """Process events in buffer."""
        try:
            # Group events by game
            game_events = {}
            for event in self.event_buffer:
                if event.game_id not in game_events:
                    game_events[event.game_id] = []
                game_events[event.game_id].append(event)

            # Process each game's events
            for game_id, events in game_events.items():
                await self.process_game_events(game_id, events)

            # Clear buffer
            self.event_buffer = []
        except Exception as e:
            print(f"Error processing buffer: {e}")
