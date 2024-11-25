from typing import Dict, List, Optional
import asyncio
from dataclasses import dataclass
import chess.engine
from prometheus_client import Counter, Gauge, Histogram


@dataclass
class EngineConfig:
    min_pool_size: int = 3
    max_pool_size: int = 10
    scaling_threshold: float = 0.8
    cooldown_period: int = 60  # seconds
    engine_path: str = "stockfish"


class AdaptiveEnginePool:
    def __init__(self, config: EngineConfig):
        self.config = config
        self.engines: List[chess.engine.SimpleEngine] = []
        self.active_engines: Dict[str, bool] = {}
        self.last_scale_time = 0

        # Metrics
        self.pool_size = Gauge("engine_pool_size", "Current number of engines")
        self.engine_wait_time = Histogram(
            "engine_wait_seconds", "Time waiting for engine availability"
        )
        self.analysis_queue_size = Gauge(
            "analysis_queue_size", "Current analysis queue size"
        )

    async def initialize(self):
        """Initialize the engine pool."""
        for _ in range(self.config.min_pool_size):
            await self.add_engine()

    async def add_engine(self):
        """Add a new engine to the pool."""
        engine = await chess.engine.SimpleEngine.popen_uci(self.config.engine_path)
        engine_id = f"engine_{len(self.engines)}"
        self.engines.append(engine)
        self.active_engines[engine_id] = False
        self.pool_size.inc()

    async def get_engine(self) -> tuple[str, chess.engine.SimpleEngine]:
        """Get an available engine from the pool."""
        start_time = asyncio.get_event_loop().time()

        while True:
            # Find available engine
            for engine_id, active in self.active_engines.items():
                if not active:
                    self.active_engines[engine_id] = True
                    wait_time = asyncio.get_event_loop().time() - start_time
                    self.engine_wait_time.observe(wait_time)
                    return engine_id, self.engines[int(engine_id.split("_")[1])]

            # Check if we should scale up
            if self.should_scale_up():
                await self.scale_up()

            await asyncio.sleep(0.1)

    def release_engine(self, engine_id: str):
        """Release an engine back to the pool."""
        self.active_engines[engine_id] = False

    def should_scale_up(self) -> bool:
        """Determine if we should scale up the engine pool."""
        current_time = asyncio.get_event_loop().time()
        if current_time - self.last_scale_time < self.config.cooldown_period:
            return False

        active_count = sum(1 for active in self.active_engines.values() if active)
        utilization = active_count / len(self.engines)

        return (
            utilization > self.config.scaling_threshold
            and len(self.engines) < self.config.max_pool_size
        )

    async def scale_up(self):
        """Scale up the engine pool."""
        self.last_scale_time = asyncio.get_event_loop().time()
        await self.add_engine()
