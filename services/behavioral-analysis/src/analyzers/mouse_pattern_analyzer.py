from typing import List, Dict
import numpy as np
from scipy.spatial.distance import euclidean
from dataclasses import dataclass


@dataclass
class MouseMetrics:
    smoothness: float
    speed_consistency: float
    direction_changes: float
    hover_patterns: float
    click_accuracy: float


class MousePatternAnalyzer:
    def __init__(self):
        self.min_events = 10
        self.speed_threshold = 1000  # pixels per second

    def analyze_movements(self, events: List[Dict]) -> MouseMetrics:
        if len(events) < self.min_events:
            return MouseMetrics(1.0, 1.0, 1.0, 1.0, 1.0)

        # Calculate movement vectors
        vectors = self._calculate_vectors(events)

        # Analyze patterns
        return MouseMetrics(
            smoothness=self._calculate_smoothness(vectors),
            speed_consistency=self._analyze_speed_consistency(vectors),
            direction_changes=self._analyze_direction_changes(vectors),
            hover_patterns=self._analyze_hover_patterns(events),
            click_accuracy=self._analyze_click_accuracy(events),
        )

    def _calculate_vectors(self, events: List[Dict]) -> List[Dict]:
        vectors = []
        for i in range(1, len(events)):
            prev = events[i - 1]
            curr = events[i]

            dt = (curr["timestamp"] - prev["timestamp"]) / 1000  # to seconds
            dx = curr["x"] - prev["x"]
            dy = curr["y"] - prev["y"]

            if dt > 0:
                vectors.append(
                    {
                        "dx": dx,
                        "dy": dy,
                        "dt": dt,
                        "speed": euclidean([dx, dy]) / dt,
                        "angle": np.arctan2(dy, dx),
                    }
                )

        return vectors

    def _calculate_smoothness(self, vectors: List[Dict]) -> float:
        """Calculate movement smoothness based on acceleration changes."""
        if len(vectors) < 3:
            return 1.0

        accelerations = [
            (v2["speed"] - v1["speed"]) / v2["dt"]
            for v1, v2 in zip(vectors[:-1], vectors[1:])
        ]

        # Normalized jerk (rate of change of acceleration)
        jerks = np.diff(accelerations)
        smoothness = 1 - min(np.std(jerks) / 1000, 1.0)

        return smoothness
