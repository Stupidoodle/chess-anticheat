from dataclasses import dataclass
import chess
from typing import Dict, Set


@dataclass
class ComplexityMetrics:
    mobility: float
    piece_tension: float
    king_safety: float
    pawn_structure: float
    material_imbalance: float
    total_score: float


class ComplexityAnalyzer:
    def __init__(self):
        self.piece_values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
        }

    def analyze_position(self, board: chess.Board) -> ComplexityMetrics:
        mobility = self._calculate_mobility(board)
        piece_tension = self._calculate_piece_tension(board)
        king_safety = self._calculate_king_safety(board)
        pawn_structure = self._calculate_pawn_structure(board)
        material_imbalance = self._calculate_material_imbalance(board)

        total_score = (
            mobility * 0.25
            + piece_tension * 0.25
            + king_safety * 0.2
            + pawn_structure * 0.15
            + material_imbalance * 0.15
        )

        return ComplexityMetrics(
            mobility=mobility,
            piece_tension=piece_tension,
            king_safety=king_safety,
            pawn_structure=pawn_structure,
            material_imbalance=material_imbalance,
            total_score=total_score,
        )

    def _calculate_mobility(self, board: chess.Board) -> float:
        """Calculate piece mobility as a ratio of legal moves to maximum possible."""
        return len(list(board.legal_moves)) / 218.0  # Normalized by max possible moves

    def _calculate_piece_tension(self, board: chess.Board) -> float:
        """Calculate tension based on attacked and defending pieces."""
        tension = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                attackers = board.attackers(not piece.color, square)
                defenders = board.attackers(piece.color, square)
                tension += len(attackers) * len(defenders)
        return min(tension / 20.0, 1.0)  # Normalized with a cap

    def _calculate_king_safety(self, board: chess.Board) -> float:
        """Evaluate king safety based on pawn shield and attacking pieces."""
        safety_score = 0
        for color in [chess.WHITE, chess.BLACK]:
            king_square = board.king(color)
            if king_square:
                # Check pawn shield
                pawn_shield = self._evaluate_pawn_shield(board, king_square, color)
                # Check attacking pieces
                attacking_pieces = len(board.attackers(not color, king_square))
                safety_score += pawn_shield - (attacking_pieces * 0.2)
        return max(min(safety_score / 2.0, 1.0), 0.0)
