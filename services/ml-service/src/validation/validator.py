from typing import Dict, List, Optional
import numpy as np
from dataclasses import dataclass
import chess.engine
import asyncio


@dataclass
class ValidationResult:
    accuracy: float
    false_positive_rate: float
    false_negative_rate: float
    average_detection_time: float
    confidence_distribution: Dict[str, float]


class SystemValidator:
    def __init__(
        self,
        pipeline: AnalysisPipeline,
        engine: chess.engine.SimpleEngine,
        config: Dict,
    ):
        self.pipeline = pipeline
        self.engine = engine
        self.config = config

    async def validate_system(
        self, test_cases: List[Dict], truth_labels: List[bool]
    ) -> ValidationResult:
        """Run system validation."""
        results = []
        detection_times = []

        for test_case, is_cheating in zip(test_cases, truth_labels):
            start_time = time.time()
            result = await self.pipeline.analyze_game(test_case)
            detection_time = time.time() - start_time

            results.append(
                {
                    "prediction": result["suspicious_score"] > self.config["threshold"],
                    "true_label": is_cheating,
                    "confidence": result["confidence"],
                    "detection_time": detection_time,
                }
            )

            detection_times.append(detection_time)

        # Calculate metrics
        metrics = self._calculate_validation_metrics(results)

        return ValidationResult(
            accuracy=metrics["accuracy"],
            false_positive_rate=metrics["fpr"],
            false_negative_rate=metrics["fnr"],
            average_detection_time=np.mean(detection_times),
            confidence_distribution=self._analyze_confidence(results),
        )

    def _analyze_confidence(self, results: List[Dict]) -> Dict[str, float]:
        """Analyze confidence distribution."""
        confidence_scores = [r["confidence"] for r in results]
        return {
            "mean": np.mean(confidence_scores),
            "std": np.std(confidence_scores),
            "median": np.median(confidence_scores),
            "q1": np.percentile(confidence_scores, 25),
            "q3": np.percentile(confidence_scores, 75),
        }
