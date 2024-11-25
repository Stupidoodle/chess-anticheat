from typing import Dict, Optional
import time
import asyncio
from dataclasses import dataclass
import redis.asyncio as redis


@dataclass
class RateLimitConfig:
    requests_per_minute: int = 60
    burst_size: int = 10
    cooldown_minutes: int = 5


class RateLimiter:
    def __init__(self, redis_client: redis.Redis, config: RateLimitConfig):
        self.redis = redis_client
        self.config = config

    async def check_rate_limit(self, client_id: str, increment: bool = True) -> bool:
        """Check if request is within rate limits."""
        key = f"rate_limit:{client_id}"
        pipe = self.redis.pipeline()

        now = time.time()
        window_start = now - 60

        # Remove old requests
        await pipe.zremrangebyscore(key, 0, window_start)

        # Get current request count
        count = await pipe.zcard(key)

        if count >= self.config.requests_per_minute:
            return False

        if increment:
            # Add new request
            await pipe.zadd(key, {str(now): now})
            # Set expiry
            await pipe.expire(key, 60)

        await pipe.execute()
        return True


class AdaptiveRateLimiter(RateLimiter):
    async def update_limits(self, client_id: str, behavior_score: float):
        """Dynamically adjust rate limits based on behavior."""
        base_limit = self.config.requests_per_minute

        if behavior_score < 0.5:
            new_limit = int(base_limit * 0.5)
        elif behavior_score < 0.8:
            new_limit = int(base_limit * 0.8)
        else:
            new_limit = base_limit

        await self.redis.hset(
            f"client_limits:{client_id}", mapping={"requests_per_minute": new_limit}
        )
