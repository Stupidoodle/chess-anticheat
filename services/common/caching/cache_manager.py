from typing import Dict, Any, Optional
import redis
import json
from datetime import timedelta
import hashlib


class CacheManager:
    def __init__(self, redis_client: redis.Redis, default_ttl: int = 3600):  # 1 hour
        self.redis = redis_client
        self.default_ttl = default_ttl

    def generate_key(self, components: Dict[str, Any]) -> str:
        """Generate a cache key from components."""
        key_str = json.dumps(components, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()

    async def get_cached_analysis(self, position: str, depth: int) -> Optional[Dict]:
        """Get cached analysis result."""
        key = self.generate_key({"position": position, "depth": depth})

        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)
        return None

    async def cache_analysis(
        self, position: str, depth: int, result: Dict, ttl: Optional[int] = None
    ):
        """Cache analysis result."""
        key = self.generate_key({"position": position, "depth": depth})

        await self.redis.setex(key, ttl or self.default_ttl, json.dumps(result))
