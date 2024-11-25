from typing import Dict, List
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.optim import AdamW
from torch.optim.lr_scheduler import OneCycleLR
import wandb
from tqdm import tqdm


class ChessModelTrainer:
    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        config: Dict,
    ):
        self.model = model
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.config = config

        self.optimizer = AdamW(
            model.parameters(),
            lr=config["learning_rate"],
            weight_decay=config["weight_decay"],
        )

        self.scheduler = OneCycleLR(
            self.optimizer,
            max_lr=config["learning_rate"],
            epochs=config["num_epochs"],
            steps_per_epoch=len(train_loader),
        )

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

    def train_epoch(self) -> Dict[str, float]:
        self.model.train()
        total_loss = 0

        for batch in tqdm(self.train_loader):
            # Move batch to device
            batch = {k: v.to(self.device) for k, v in batch.items()}

            # Forward pass
            outputs = self.model(
                batch["move_ids"],
                batch["times"],
                batch["evals"],
                batch["attention_mask"],
            )

            # Calculate losses
            move_quality_loss = self.calculate_move_quality_loss(
                outputs["move_quality"], batch["engine_scores"]
            )

            time_correlation_loss = self.calculate_time_correlation_loss(
                outputs["time_correlation"], batch["times"]
            )

            pattern_loss = self.calculate_pattern_loss(
                outputs["pattern_score"], batch["is_engine_move"]
            )

            # Combine losses
            loss = (
                move_quality_loss * self.config["move_quality_weight"]
                + time_correlation_loss * self.config["time_correlation_weight"]
                + pattern_loss * self.config["pattern_weight"]
            )

            # Backward pass
            self.optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(
                self.model.parameters(), self.config["max_grad_norm"]
            )
            self.optimizer.step()
            self.scheduler.step()

            total_loss += loss.item()

        return {"train_loss": total_loss / len(self.train_loader)}
