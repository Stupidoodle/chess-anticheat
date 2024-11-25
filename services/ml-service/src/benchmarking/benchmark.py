from typing import Dict, List
import time
import asyncio
import numpy as np
from dataclasses import dataclass


@dataclass
class BenchmarkResult:
    average_response_time: float
    percentile_95: float
    percentile_99: float
    max_response_time: float
    throughput: float
    memory_usage: float
    cpu_usage: float


class SystemBenchmark:
    def __init__(self, pipeline: AnalysisPipeline):
        self.pipeline = pipeline

    async def run_benchmark(
        self, test_cases: List[Dict], concurrent_users: int = 10
    ) -> BenchmarkResult:
        """Run system performance benchmark."""
        start_time = time.time()
        response_times = []

        # Create task groups for concurrent processing
        tasks = []
        for i in range(0, len(test_cases), concurrent_users):
            batch = test_cases[i : i + concurrent_users]
            batch_tasks = [self._process_game(game, response_times) for game in batch]
            tasks.extend(batch_tasks)
            await asyncio.gather(*tasks)
            tasks = []

        total_time = time.time() - start_time

        return BenchmarkResult(
            average_response_time=np.mean(response_times),
            percentile_95=np.percentile(response_times, 95),
            percentile_99=np.percentile(response_times, 99),
            max_response_time=max(response_times),
            throughput=len(test_cases) / total_time,
            memory_usage=self._get_memory_usage(),
            cpu_usage=self._get_cpu_usage(),
        )
