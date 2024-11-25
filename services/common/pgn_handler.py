import chess.pgn
import io
from typing import List, Dict, Generator
from datetime import datetime


class PGNHandler:
    def __init__(self):
        self.cache = {}  # Optional caching of processed games

    def process_pgn_file(self, pgn_content: str) -> Generator[Dict, None, None]:
        """Process a PGN file and yield game data."""
        pgn_io = io.StringIO(pgn_content)

        while True:
            game = chess.pgn.read_game(pgn_io)
            if game is None:
                break

            yield {
                "event": game.headers.get("Event", "Unknown"),
                "white": {
                    "name": game.headers.get("White", "Unknown"),
                    "elo": game.headers.get("WhiteElo", "?"),
                },
                "black": {
                    "name": game.headers.get("Black", "Unknown"),
                    "elo": game.headers.get("BlackElo", "?"),
                },
                "result": game.headers.get("Result", "*"),
                "date": game.headers.get("Date", "????:??:??"),
                "moves": self._process_moves(game),
                "eco": game.headers.get("ECO", ""),
                "time_control": game.headers.get("TimeControl", ""),
            }

    def _process_moves(self, game: chess.pgn.Game) -> List[Dict]:
        """Process moves with timing information if available."""
        moves = []
        board = game.board()

        for node in game.mainline():
            move_data = {
                "move": node.move.uci(),
                "san": board.san(node.move),
                "fen": board.fen(),
                "clock": node.clock() if node.clock() is not None else None,
                "eval": node.eval() if node.eval() is not None else None,
            }
            moves.append(move_data)
            board.push(node.move)

        return moves

    async def import_pgn_database(self, file_path: str) -> int:
        """Import a large PGN database for training."""
        imported_count = 0

        with open(file_path) as pgn_file:
            while True:
                game = chess.pgn.read_game(pgn_file)
                if game is None:
                    break

                # Process and store game data
                game_data = self._process_game(game)
                await self.store_game_data(game_data)
                imported_count += 1

        return imported_count
