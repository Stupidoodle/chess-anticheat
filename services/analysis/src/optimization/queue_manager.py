from typing import Dict, Optional
from dataclasses import dataclass
import asyncio
import aioboto3
from priority_queue import PriorityQueue


@dataclass
class QueueConfig:
    max_queue_size: int = 1000
    batch_size: int = 10
    priority_levels: int = 3
    timeout: int = 30  # seconds


class AnalysisQueueManager:
    def __init__(self, config: QueueConfig):
        self.config = config
        self.queues = [PriorityQueue() for _ in range(config.priority_levels)]
        self.processing = set()

    async def enqueue_analysis(self, game_id: str, position: str, priority: int = 1):
        """Enqueue a position for analysis."""
        if priority >= self.config.priority_levels:
            priority = self.config.priority_levels - 1

        queue_size = sum(q.qsize() for q in self.queues)
        if queue_size >= self.config.max_queue_size:
            raise QueueFullError("Analysis queue is full")

        await self.queues[priority].put((game_id, position))

    async def process_queue(self):
        """Process items in the queue."""
        while True:
            batch = []

            # Try to fill batch with highest priority items first
            for priority in range(self.config.priority_levels):
                while (
                    len(batch) < self.config.batch_size
                    and not self.queues[priority].empty()
                ):
                    item = await self.queues[priority].get()
                    batch.append(item)

                if batch:
                    break

            if not batch:
                await asyncio.sleep(0.1)
                continue

            # Process batch
            try:
                results = await self.process_batch(batch)
                await self.store_results(results)
            except Exception as e:
                # Handle failed items
                await self.handle_failed_items(batch, e)
