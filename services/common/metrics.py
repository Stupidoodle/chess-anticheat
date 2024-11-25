from prometheus_client import Counter, Histogram, start_http_server


class MetricsCollector:
    def __init__(self, service_name: str):
        self.move_analysis_duration = Histogram(
            "move_analysis_duration_seconds",
            "Time spent analyzing moves",
            ["service", "endpoint"],
        )

        self.suspicion_levels = Counter(
            "suspicion_levels_total", "Number of detected suspicion levels", ["level"]
        )

    def record_analysis_duration(self, duration: float, endpoint: str):
        self.move_analysis_duration.labels(
            service="move_analysis", endpoint=endpoint
        ).observe(duration)
