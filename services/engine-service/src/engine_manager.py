from typing import Dict, List
import chess.engine
import asyncio
from contextlib import asynccontextmanager


class EngineManager:
    def __init__(self, engine_path: str = "stockfish"):
        self.engine_path = engine_path
        self.engine_pool: List[chess.engine] = []
        self.pool_size = 3

    async def initialize(self):
        for _ in range(self.pool_size):
            engine = await chess.engine.popen_uci(self.engine_path)
            self.engine_pool.append(engine)

    @asynccontextmanager
    async def get_engine(self):
        engine = self.engine_pool.pop()
        try:
            yield engine
        finally:
            self.engine_pool.append(engine)

    async def analyze_position(
        self, fen: str, depth: int = 20, multipv: int = 3
    ) -> List[Dict]:
        async with self.get_engine() as engine:
            board = chess.Board(fen)
            result = await engine.analyse(
                board, chess.engine.Limit(depth=depth), multipv=multipv
            )
            return self._process_analysis(result)

    @staticmethod
    def _process_analysis(analysis_result) -> List[Dict]:
        return [
            {
                "move": pv.moves[0].uci(),
                "score": pv.score.relative.score(mate_score=10000),
                "depth": pv.depth,
                "pv": [move.uci() for move in pv.moves[:3]],
            }
            for pv in analysis_result
        ]
