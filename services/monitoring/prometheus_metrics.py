from prometheus_client import Counter, Histogram, Gauge, Summary
import time
from functools import wraps
from typing import Dict, Any


class ChessMetrics:
    def __init__(self):
        # Analysis metrics
        self.analysis_duration = Histogram(
            "chess_analysis_duration_seconds",
            "Time spent on move analysis",
            ["analysis_type", "complexity"],
        )

        self.suspicious_moves = Counter(
            "suspicious_moves_total",
            "Number of suspicious moves detected",
            ["severity"],
        )

        self.model_inference_time = Histogram(
            "model_inference_seconds", "Time spent on model inference", ["model_type"]
        )

        # Resource metrics
        self.engine_pool_size = Gauge(
            "chess_engine_pool_size", "Number of available chess engines"
        )

        self.analysis_queue_size = Gauge(
            "analysis_queue_size", "Number of positions waiting for analysis"
        )

        # Error metrics
        self.analysis_errors = Counter(
            "analysis_errors_total", "Number of analysis errors", ["error_type"]
        )

    def track_analysis_time(self, analysis_type: str):
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    duration = time.time() - start_time
                    complexity = self._get_complexity(result)
                    self.analysis_duration.labels(
                        analysis_type=analysis_type, complexity=complexity
                    ).observe(duration)
                    return result
                except Exception as e:
                    self.analysis_errors.labels(error_type=type(e).__name__).inc()
                    raise

            return wrapper

        return decorator
