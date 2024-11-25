from typing import Dict, List, Tuple
import torch
import numpy as np
from torch.utils.data import Dataset
import chess
import chess.engine
from dataclasses import dataclass


@dataclass
class GameData:
    moves: List[str]
    times: List[float]
    evals: List[float]
    result: str
    white_elo: int
    black_elo: int


class ChessDataset(Dataset):
    def __init__(
        self, games: List[GameData], max_sequence_length: int = 128, tokenizer=None
    ):
        self.games = games
        self.max_sequence_length = max_sequence_length
        self.tokenizer = tokenizer or self._create_default_tokenizer()

    def __len__(self) -> int:
        return len(self.games)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        game = self.games[idx]

        # Tokenize moves
        move_tokens = self.tokenizer.encode(game.moves)

        # Pad sequences
        move_tokens = self._pad_sequence(move_tokens)
        times = self._pad_sequence(game.times)
        evals = self._pad_sequence(game.evals)

        # Create attention mask
        attention_mask = self._create_attention_mask(len(game.moves))

        return {
            "move_ids": torch.tensor(move_tokens),
            "times": torch.tensor(times),
            "evals": torch.tensor(evals),
            "attention_mask": torch.tensor(attention_mask),
            "white_elo": torch.tensor(game.white_elo),
            "black_elo": torch.tensor(game.black_elo),
        }

    def _pad_sequence(self, sequence: List) -> List:
        """Pad sequence to max_sequence_length."""
        if len(sequence) > self.max_sequence_length:
            return sequence[: self.max_sequence_length]
        return sequence + [0] * (self.max_sequence_length - len(sequence))
