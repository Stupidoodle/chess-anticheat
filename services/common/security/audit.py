from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import asyncpg
from dataclasses import dataclass


@dataclass
class AuditEvent:
    timestamp: datetime
    event_type: str
    user_id: str
    resource_id: str
    action: str
    status: str
    details: Dict[str, Any]
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AuditLogger:
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool

    async def log_event(self, event: AuditEvent):
        """Log audit event to database."""
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO audit_log (
                    timestamp, event_type, user_id, resource_id,
                    action, status, details, ip_address, user_agent
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """,
                event.timestamp,
                event.event_type,
                event.user_id,
                event.resource_id,
                event.action,
                event.status,
                json.dumps(event.details),
                event.ip_address,
                event.user_agent,
            )

    async def query_events(
        self,
        filters: Dict[str, Any],
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Query audit log events."""
        query = """
            SELECT * FROM audit_log
            WHERE ($1::timestamp IS NULL OR timestamp >= $1)
            AND ($2::timestamp IS NULL OR timestamp <= $2)
        """

        conditions = []
        params = [start_time, end_time]

        for key, value in filters.items():
            params.append(value)
            conditions.append(f"{key} = ${len(params)}")

        if conditions:
            query += " AND " + " AND ".join(conditions)

        async with self.db_pool.acquire() as conn:
            records = await conn.fetch(query, *params)
            return [dict(r) for r in records]
