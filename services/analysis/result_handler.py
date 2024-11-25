from typing import Dict, Any
import asyncio
from datetime import datetime
import json


class AnalysisResultHandler:
    def __init__(self, redis_client, db_client):
        self.redis = redis_client
        self.db = db_client
        self.threshold = 0.8

    async def handle_result(self, game_id: str, result: Dict[str, Any]):
        """Handle analysis results and trigger appropriate actions."""
        # Store result
        await self.store_result(game_id, result)

        # Check for suspicious activity
        if result["total_score"] > self.threshold:
            await self.handle_suspicious_activity(game_id, result)

        # Update real-time monitoring
        await self.update_monitoring(game_id, result)

        # Notify relevant services
        await self.notify_services(game_id, result)

    async def handle_suspicious_activity(self, game_id: str, result: Dict):
        """Handle cases of suspicious activity."""
        # Create incident report
        incident = {
            "game_id": game_id,
            "timestamp": datetime.utcnow().isoformat(),
            "score": result["total_score"],
            "factors": {
                "move_strength": result["move_analysis"]["score"],
                "behavioral": result["behavioral_analysis"]["score"],
                "historical": result["ml_analysis"]["historical_score"],
            },
            "evidence": self.collect_evidence(result),
        }

        # Store incident
        await self.db.store_incident(incident)

        # Notify moderators if score is very high
        if result["total_score"] > 0.95:
            await self.notify_moderators(incident)
