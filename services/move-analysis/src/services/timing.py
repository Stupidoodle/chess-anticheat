import numpy as np
from typing import List, Dict
from dataclasses import dataclass
from scipy import stats


@dataclass
class TimingMetrics:
    consistency: float
    correlation_with_complexity: float
    outlier_score: float
    average_time: float
    deviation_pattern: float


class TimingAnalyzer:
    def __init__(self):
        self.window_size = 5
        self.min_moves_for_analysis = 3

    def analyze_move_timing(
        self, move_times: List[float], complexity_scores: List[float]
    ) -> TimingMetrics:
        if len(move_times) < self.min_moves_for_analysis:
            return TimingMetrics(
                consistency=1.0,
                correlation_with_complexity=1.0,
                outlier_score=0.0,
                average_time=np.mean(move_times) if move_times else 0.0,
                deviation_pattern=0.0,
            )

        # Calculate base metrics
        consistency = self._calculate_consistency(move_times)
        correlation = self._calculate_correlation(
            move_times[-self.window_size :], complexity_scores[-self.window_size :]
        )
        outlier_score = self._calculate_outlier_score(move_times)
        avg_time = float(np.mean(move_times))
        deviation = self._calculate_deviation_pattern(move_times)

        return TimingMetrics(
            consistency=consistency,
            correlation_with_complexity=correlation,
            outlier_score=outlier_score,
            average_time=avg_time,
            deviation_pattern=deviation,
        )

    def _calculate_consistency(self, move_times: List[float]) -> float:
        """Calculate how consistent the move times are."""
        if len(move_times) < 2:
            return 1.0

        std_dev = np.std(move_times)
        mean_time = np.mean(move_times)

        # Coefficient of variation - normalized standard deviation
        if mean_time > 0:
            cv = std_dev / mean_time
            # Convert to a 0-1 score where 1 is most consistent
            consistency = 1 - min(cv, 1)
            return consistency
        return 1.0

    def _calculate_correlation(
        self, times: List[float], complexity: List[float]
    ) -> float:
        """Calculate correlation between move times and position complexity."""
        if len(times) < 2 or len(complexity) < 2:
            return 1.0

        correlation, _ = stats.pearsonr(times, complexity)
        # Convert to 0-1 scale where 1 is perfect positive correlation
        return (correlation + 1) / 2

    def _calculate_outlier_score(self, move_times: List[float]) -> float:
        """Detect outliers in move timing."""
        if len(move_times) < self.min_moves_for_analysis:
            return 0.0

        z_scores = stats.zscore(move_times)
        outliers = abs(z_scores) > 2
        return sum(outliers) / len(move_times)

    def _calculate_deviation_pattern(self, move_times: List[float]) -> float:
        """Analyze patterns in timing deviations."""
        if len(move_times) < self.window_size:
            return 0.0

        # Calculate rolling mean and standard deviation
        rolling_mean = np.convolve(move_times, np.ones(3) / 3, mode="valid")
        deviations = np.array(move_times[2:]) - rolling_mean

        # Look for patterns in deviations
        deviation_pattern = np.corrcoef(deviations[:-1], deviations[1:])[0, 1]
        return abs(deviation_pattern if not np.isnan(deviation_pattern) else 0.0)
