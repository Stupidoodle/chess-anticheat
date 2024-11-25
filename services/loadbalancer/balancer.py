from typing import Dict, List
import asyncio
from dataclasses import dataclass


@dataclass
class ServiceHealth:
    service_id: str
    load: float
    response_time: float
    error_rate: float
    last_check: float


class LoadBalancer:
    def __init__(self):
        self.services: Dict[str, ServiceHealth] = {}
        self.weights = {"load": 0.4, "response_time": 0.4, "error_rate": 0.2}

    def get_optimal_service(self) -> str:
        """Get the optimal service based on health metrics."""
        if not self.services:
            raise NoAvailableServiceError("No services registered")

        scores = {}
        for service_id, health in self.services.items():
            score = (
                health.load * self.weights["load"]
                + health.response_time * self.weights["response_time"]
                + health.error_rate * self.weights["error_rate"]
            )
            scores[service_id] = score

        return min(scores.items(), key=lambda x: x[1])[0]

    async def update_service_health(self, service_id: str, metrics: Dict[str, float]):
        """Update service health metrics."""
        self.services[service_id] = ServiceHealth(
            service_id=service_id,
            load=metrics["load"],
            response_time=metrics["response_time"],
            error_rate=metrics["error_rate"],
            last_check=asyncio.get_event_loop().time(),
        )
