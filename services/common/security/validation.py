from typing import Dict, Any, Optional
from pydantic import BaseModel, field_validator, ValidationError
import chess


class MoveRequest(BaseModel):
    game_id: str
    position_fen: str
    move_uci: str
    time_taken: float
    player_id: str

    @field_validator("position_fen")
    def validate_fen(cls, v):
        try:
            board = chess.Board(v)
            return v
        except ValueError:
            raise ValueError("Invalid FEN string")

    @field_validator("move_uci")
    def validate_move(cls, v, values):
        if "position_fen" in values:
            board = chess.Board(values["position_fen"])
            try:
                move = chess.Move.from_uci(v)
                if move not in board.legal_moves:
                    raise ValueError("Illegal move")
                return v
            except ValueError:
                raise ValueError("Invalid UCI move")


class RequestValidator:
    def __init__(self):
        self.validators = {
            "move": MoveRequest,
            # Add other validators as needed
        }

    async def validate_request(
        self, request_type: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Validate incoming request data."""
        if validator := self.validators.get(request_type):
            try:
                validated = validator(**data)
                return validated.model_dump()
            except ValueError as e:
                raise ValidationError(str(e))
        return None
