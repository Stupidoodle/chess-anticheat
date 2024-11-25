# tests/integration/test_analysis_pipeline.py
import pytest
import asyncio
from typing import Dict, List
import chess
import chess.pgn
import io


class TestAnalysisPipeline:
    @pytest.fixture
    async def setup_pipeline(self):
        """Set up complete analysis pipeline."""
        move_analyzer = MoveAnalyzer()
        behavioral_analyzer = BehavioralAnalyzer()
        ml_analyzer = MLAnalyzer()

        return AnalysisPipeline(move_analyzer, behavioral_analyzer, ml_analyzer)

    @pytest.mark.asyncio
    async def test_known_engine_games(self, setup_pipeline, engine_games: List[Dict]):
        """Test pipeline against known engine games."""
        pipeline = await setup_pipeline

        results = []
        for game in engine_games:
            result = await pipeline.analyze_game(game)
            results.append(result)

        # Verify detection rate
        detection_rate = sum(r["suspicious_score"] > 0.8 for r in results) / len(
            results
        )

        assert detection_rate > 0.95, f"Detection rate {detection_rate} below threshold"

    @pytest.mark.asyncio
    async def test_legitimate_games(self, setup_pipeline, legitimate_games: List[Dict]):
        """Test pipeline against legitimate games."""
        pipeline = await setup_pipeline

        false_positives = []
        for game in legitimate_games:
            result = await pipeline.analyze_game(game)
            if result["suspicious_score"] > 0.8:
                false_positives.append(
                    {"game": game, "score": result["suspicious_score"]}
                )

        false_positive_rate = len(false_positives) / len(legitimate_games)
        assert (
            false_positive_rate < 0.01
        ), f"False positive rate {false_positive_rate} above threshold"
