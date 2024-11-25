import psutil
import time
from typing import Dict, Any
import asyncio


class PerformanceMonitor:
    def __init__(self, metrics: ChessMetrics):
        self.metrics = metrics
        self.sampling_interval = 10  # seconds

    async def start_monitoring(self):
        """Start continuous performance monitoring."""
        while True:
            self.collect_metrics()
            await asyncio.sleep(self.sampling_interval)

    def collect_metrics(self):
        """Collect system performance metrics."""
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        self.metrics.record_cpu_usage(cpu_percent)

        # Memory metrics
        memory = psutil.virtual_memory()
        self.metrics.record_memory_usage(memory.percent)

        # Process metrics
        process = psutil.Process()
        with process.oneshot():
            self.metrics.record_process_metrics(
                {
                    "cpu_percent": process.cpu_percent(),
                    "memory_percent": process.memory_percent(),
                    "threads": len(process.threads()),
                    "open_files": len(process.open_files()),
                    "connections": len(process.connections()),
                }
            )
