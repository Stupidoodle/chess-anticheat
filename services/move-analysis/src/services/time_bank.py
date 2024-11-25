from dataclasses import dataclass
from typing import List, Dict
import numpy as np


@dataclass
class TimeBankMetrics:
    usage_pattern: float  # How effectively time is being used
    critical_decisions: float  # Time used in critical positions
    time_pressure_handling: float  # How well player handles time pressure


class TimeBankAnalyzer:
    def __init__(self):
        self.pressure_threshold = 30  # seconds

    def analyze_time_management(
        self,
        move_times: List[float],
        remaining_time: List[float],
        position_complexity: List[float],
    ) -> TimeBankMetrics:
        return TimeBankMetrics(
            usage_pattern=self._analyze_usage_pattern(move_times, remaining_time),
            critical_decisions=self._analyze_critical_decisions(
                move_times, position_complexity, remaining_time
            ),
            time_pressure_handling=self._analyze_time_pressure(
                move_times, remaining_time
            ),
        )

    def _analyze_usage_pattern(
        self, move_times: List[float], remaining_time: List[float]
    ) -> float:
        """Analyze how effectively time is being used throughout the game."""
        if len(move_times) < 2:
            return 1.0

        # Calculate time usage rate
        usage_rates = [
            t / r if r > 0 else 1.0 for t, r in zip(move_times, remaining_time)
        ]

        # Look for consistency in usage rate
        std_dev = np.std(usage_rates)
        return 1 - min(std_dev, 1.0)

    def _analyze_critical_decisions(
        self,
        move_times: List[float],
        complexity: List[float],
        remaining_time: List[float],
    ) -> float:
        """Analyze time usage in critical positions."""
        if not move_times:
            return 1.0

        # Identify critical positions (high complexity)
        mean_complexity = np.mean(complexity)
        critical_positions = [
            i
            for i, c in enumerate(complexity)
            if c > mean_complexity + np.std(complexity)
        ]

        if not critical_positions:
            return 1.0

        # Calculate average time usage in critical positions
        critical_times = [move_times[i] for i in critical_positions]
        normal_times = [
            t for i, t in enumerate(move_times) if i not in critical_positions
        ]

        if not normal_times:
            return 1.0

        # Compare time usage
        avg_critical = np.mean(critical_times)
        avg_normal = np.mean(normal_times)

        return min(avg_critical / avg_normal if avg_normal > 0 else 1.0, 1.0)

    def _analyze_time_pressure(
        self, move_times: List[float], remaining_time: List[float]
    ) -> float:
        """Analyze how well a player handles time pressure."""
        if not move_times or not remaining_time:
            return 1.0  # Default score if there's no data.

        # Identify indices of moves under time pressure
        pressure_indices = [
            i for i, r in enumerate(remaining_time) if r < self.pressure_threshold
        ]

        if not pressure_indices:
            return 1.0  # Perfect handling if no time pressure occurred.

        # Calculate average move time under and not under time pressure
        pressure_move_times = [move_times[i] for i in pressure_indices]
        normal_move_times = [
            t for i, t in enumerate(move_times) if i not in pressure_indices
        ]

        avg_pressure_time = np.mean(pressure_move_times) if pressure_move_times else 0.0
        avg_normal_time = np.mean(normal_move_times) if normal_move_times else 0.0

        # Normalize the ratio: players who maintain similar move times under pressure score higher
        pressure_handling_ratio = (
            avg_normal_time / avg_pressure_time if avg_pressure_time > 0 else 1.0
        )

        # Return a score where 1.0 means great handling (consistent move times) and lower is worse
        return min(pressure_handling_ratio, 1.0)
