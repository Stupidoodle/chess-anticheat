from typing import Dict, List
import asyncpg
from datetime import datetime


class DatabaseOptimizer:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create_indexes(self):
        """Create optimized indexes."""
        async with self.pool.acquire() as conn:
            # Game analysis indexes
            await conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_game_analysis_timestamp 
                ON game_analysis (timestamp DESC);

                CREATE INDEX IF NOT EXISTS idx_game_analysis_score 
                ON game_analysis (suspicious_score DESC)
                WHERE suspicious_score > 0.8;

                CREATE INDEX IF NOT EXISTS idx_game_behavioral 
                ON behavioral_data (game_id, timestamp)
                INCLUDE (mouse_patterns, tab_switches);
                """
            )

    async def optimize_tables(self):
        """Optimize table structure and settings."""
        async with self.pool.acquire() as conn:
            # Partition large tables
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS game_analysis_partition OF game_analysis
                FOR VALUES FROM (DATE '2024-01-01')
                TO (DATE '2025-01-01')
                PARTITION BY RANGE (timestamp);
                """
            )

            # Set table storage parameters
            await conn.execute(
                """
                ALTER TABLE game_analysis 
                SET (autovacuum_vacuum_scale_factor = 0.1);
                """
            )
