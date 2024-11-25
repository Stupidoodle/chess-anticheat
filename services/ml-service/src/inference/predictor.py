from typing import Dict, List
import torch
import numpy as np
from dataclasses import dataclass


@dataclass
class PredictionResult:
    move_quality: float
    time_correlation: float
    pattern_score: float
    suspicious_score: float
    confidence: float


class ChessPredictor:
    def __init__(self, model: torch.nn.Module, config: Dict):
        self.model = model
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()

    async def predict(
        self, game_state: Dict, player_history: Optional[Dict] = None
    ) -> PredictionResult:
        """Make predictions for current game state."""
        with torch.no_grad():
            # Prepare input data
            inputs = self.prepare_inputs(game_state)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Get model predictions
            outputs = self.model(**inputs)

            # Process predictions
            move_quality = outputs["move_quality"].mean().item()
            time_correlation = outputs["time_correlation"].mean().item()
            pattern_score = outputs["pattern_score"].mean().item()

            # Calculate confidence
            confidence = self.calculate_confidence(outputs)

            # Calculate suspicious score
            suspicious_score = self.calculate_suspicious_score(
                move_quality, time_correlation, pattern_score, player_history
            )

            return PredictionResult(
                move_quality=move_quality,
                time_correlation=time_correlation,
                pattern_score=pattern_score,
                suspicious_score=suspicious_score,
                confidence=confidence,
            )
