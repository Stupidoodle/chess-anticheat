from typing import Dict, Any, List
import asyncio
from datetime import datetime, timedelta
import json


class AnalysisCoordinator:
    def __init__(self):
        self.move_analyzer = MoveAnalyzer()
        self.behavioral_analyzer = BehavioralAnalyzer()
        self.ml_analyzer = MLAnalyzer()
        self.active_games: Dict[str, GameState] = {}

    async def coordinate_analysis(self, game_id: str, event: Dict[str, Any]):
        """Coordinate analysis across different services."""
        game_state = self.active_games.get(game_id)
        if not game_state:
            game_state = await self.initialize_game_state(game_id)
            self.active_games[game_id] = game_state

        # Update game state
        game_state.update(event)

        # Trigger analyses
        results = await asyncio.gather(
            self.move_analyzer.analyze(game_state),
            self.behavioral_analyzer.analyze(game_state),
            self.ml_analyzer.analyze(game_state),
        )

        # Combine results
        combined_result = self.combine_analysis_results(results)

        # Check for suspicious activity
        if self.is_suspicious(combined_result):
            await self.trigger_detailed_analysis(game_id, combined_result)

        return combined_result

    def combine_analysis_results(self, results: List[Dict]) -> Dict:
        """Combine results from different analyzers with weighted scoring."""
        move_analysis, behavioral_analysis, ml_analysis = results

        # Weight factors
        weights = {
            "move_strength": 0.3,
            "behavioral_patterns": 0.3,
            "historical_comparison": 0.2,
            "timing_patterns": 0.2,
        }

        # Calculate combined scores
        combined_score = (
            move_analysis["score"] * weights["move_strength"]
            + behavioral_analysis["score"] * weights["behavioral_patterns"]
            + ml_analysis["historical_score"] * weights["historical_comparison"]
            + ml_analysis["timing_score"] * weights["timing_patterns"]
        )

        return {
            "total_score": combined_score,
            "move_analysis": move_analysis,
            "behavioral_analysis": behavioral_analysis,
            "ml_analysis": ml_analysis,
            "timestamp": datetime.utcnow().isoformat(),
        }
