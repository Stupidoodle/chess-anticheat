from typing import Dict, List, Tuple
import torch
import numpy as np
from sklearn.metrics import roc_auc_score, precision_recall_curve
from dataclasses import dataclass
import json
import chess.engine
import asyncio


@dataclass
class TestResult:
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    auc_roc: float
    confusion_matrix: np.ndarray
    false_positives: List[Dict]
    false_negatives: List[Dict]
    threshold_analysis: Dict[str, float]


class ModelTester:
    def __init__(
        self,
        model: torch.nn.Module,
        test_loader: torch.utils.data.DataLoader,
        engine: chess.engine.SimpleEngine,
        config: Dict,
    ):
        self.model = model
        self.test_loader = test_loader
        self.engine = engine
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    async def run_comprehensive_test(self) -> TestResult:
        """Run comprehensive model testing."""
        all_predictions = []
        all_labels = []
        false_positives = []
        false_negatives = []

        self.model.eval()
        with torch.no_grad():
            for batch in self.test_loader:
                # Get model predictions
                predictions = await self._get_predictions(batch)
                labels = batch["is_cheating"].numpy()

                # Store results
                all_predictions.extend(predictions)
                all_labels.extend(labels)

                # Store misclassifications for analysis
                self._store_misclassifications(
                    batch, predictions, labels, false_positives, false_negatives
                )

        # Calculate metrics
        metrics = self._calculate_metrics(
            np.array(all_predictions), np.array(all_labels)
        )

        # Analyze thresholds
        threshold_analysis = self._analyze_thresholds(
            np.array(all_predictions), np.array(all_labels)
        )

        return TestResult(
            accuracy=metrics["accuracy"],
            precision=metrics["precision"],
            recall=metrics["recall"],
            f1_score=metrics["f1"],
            auc_roc=metrics["auc_roc"],
            confusion_matrix=metrics["confusion_matrix"],
            false_positives=false_positives,
            false_negatives=false_negatives,
            threshold_analysis=threshold_analysis,
        )

    async def _get_predictions(self, batch: Dict) -> np.ndarray:
        """Get model predictions with engine verification."""
        batch = {k: v.to(self.device) for k, v in batch.items()}
        outputs = self.model(**batch)

        # Get primary predictions
        predictions = outputs["suspicious_score"].cpu().numpy()

        # Verify high-confidence predictions with engine
        for i, pred in enumerate(predictions):
            if pred > self.config["engine_verification_threshold"]:
                engine_verification = await self._verify_with_engine(
                    batch["moves"][i], batch["times"][i]
                )
                predictions[i] *= engine_verification

        return predictions

    def _calculate_metrics(self, predictions: np.ndarray, labels: np.ndarray) -> Dict:
        """Calculate comprehensive metrics."""
        # Apply threshold
        binary_predictions = predictions > self.config["decision_threshold"]

        # Calculate basic metrics
        metrics = {
            "accuracy": np.mean(binary_predictions == labels),
            "precision": precision_score(labels, binary_predictions),
            "recall": recall_score(labels, binary_predictions),
            "f1": f1_score(labels, binary_predictions),
            "auc_roc": roc_auc_score(labels, predictions),
        }

        # Calculate confusion matrix
        metrics["confusion_matrix"] = confusion_matrix(labels, binary_predictions)

        return metrics
