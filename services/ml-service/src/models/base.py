from typing import Dict, List, Optional
import torch
import torch.nn as nn
from dataclasses import dataclass


@dataclass
class ModelConfig:
    hidden_size: int = 256
    num_layers: int = 6
    num_heads: int = 8
    dropout: float = 0.1
    max_sequence_length: int = 128
    vocab_size: int = 8192  # Move vocabulary size


class ChessTransformer(nn.Module):
    def __init__(self, config: ModelConfig):
        super().__init__()
        self.config = config

        # Move embeddings
        self.move_embeddings = nn.Embedding(config.vocab_size, config.hidden_size)

        # Position embeddings
        self.position_embeddings = nn.Embedding(
            config.max_sequence_length, config.hidden_size
        )

        # Transformer layers
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=config.hidden_size,
            nhead=config.num_heads,
            dim_feedforward=config.hidden_size * 4,
            dropout=config.dropout,
        )

        self.transformer = nn.TransformerEncoder(
            encoder_layer, num_layers=config.num_layers
        )

        # Output heads
        self.move_quality_head = nn.Linear(config.hidden_size, 1)
        self.time_correlation_head = nn.Linear(config.hidden_size, 1)
        self.pattern_detection_head = nn.Linear(config.hidden_size, 1)

    def forward(
        self,
        move_ids: torch.Tensor,
        time_taken: torch.Tensor,
        position_evals: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ):
        # Create embeddings
        move_embeds = self.move_embeddings(move_ids)
        pos_embeds = self.position_embeddings(
            torch.arange(move_ids.size(1), device=move_ids.device)
        )

        # Combine embeddings
        embeddings = move_embeds + pos_embeds

        # Add time and evaluation information
        time_features = time_taken.unsqueeze(-1)
        eval_features = position_evals.unsqueeze(-1)
        embeddings = torch.cat([embeddings, time_features, eval_features], dim=-1)

        # Pass through transformer
        transformer_output = self.transformer(
            embeddings.transpose(0, 1), src_key_padding_mask=attention_mask
        ).transpose(0, 1)

        # Get predictions from different heads
        move_quality = self.move_quality_head(transformer_output)
        time_correlation = self.time_correlation_head(transformer_output)
        pattern_score = self.pattern_detection_head(transformer_output)

        return {
            "move_quality": move_quality,
            "time_correlation": time_correlation,
            "pattern_score": pattern_score,
        }
