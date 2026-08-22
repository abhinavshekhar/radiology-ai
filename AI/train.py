"""
Model training script for chest X-ray pneumonia detection.
Uses transfer learning with DenseNet121 on RSNA Pneumonia / ChestX-ray14 datasets.

Usage:
    python train.py --data-dir ../datasets/rsna --epochs 10 --batch-size 32
"""

import argparse
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms
from PIL import Image


class ChestXrayDataset(Dataset):
    def __init__(self, data_dir: str, transform=None):
        self.data_dir = Path(data_dir)
        self.transform = transform or transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ])
        self.samples = self._load_samples()

    def _load_samples(self):
        samples = []
        for label_dir, label in [("NORMAL", 0), ("PNEUMONIA", 1)]:
            folder = self.data_dir / label_dir
            if folder.exists():
                for img_path in folder.glob("*"):
                    if img_path.suffix.lower() in {".png", ".jpg", ".jpeg"}:
                        samples.append((str(img_path), label))
        return samples

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, label = self.samples[idx]
        img = Image.open(path).convert("RGB")
        return self.transform(img), label


def train(args):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on {device}")

    dataset = ChestXrayDataset(args.data_dir)
    if len(dataset) == 0:
        print("No training images found. Place images in datasets/rsna/NORMAL and datasets/rsna/PNEUMONIA")
        return

    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True, num_workers=2)
    split = int(0.8 * len(dataset))
    train_set, val_set = torch.utils.data.random_split(dataset, [split, len(dataset) - split])
    train_loader = DataLoader(train_set, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_set, batch_size=args.batch_size)

    model = models.densenet121(weights=models.DenseNet121_Weights.IMAGENET1K_V1)
    model.classifier = nn.Linear(model.classifier.in_features, 2)
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.1)

    best_acc = 0.0
    weights_dir = Path(__file__).parent.parent / "weights"
    weights_dir.mkdir(exist_ok=True)

    for epoch in range(args.epochs):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()

        train_acc = correct / total if total else 0
        scheduler.step()

        # Validation
        model.eval()
        val_correct = 0
        val_total = 0
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                _, predicted = outputs.max(1)
                val_total += labels.size(0)
                val_correct += predicted.eq(labels).sum().item()

        val_acc = val_correct / val_total if val_total else 0
        print(f"Epoch {epoch+1}/{args.epochs} | Loss: {running_loss/len(train_loader):.4f} | "
              f"Train Acc: {train_acc:.3f} | Val Acc: {val_acc:.3f}")

        if val_acc > best_acc:
            best_acc = val_acc
            torch.save(model.state_dict(), weights_dir / "densenet121_pneumonia.pt")
            print(f"  Saved best model (val_acc={val_acc:.3f})")

    print(f"Training complete. Best validation accuracy: {best_acc:.3f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="../datasets/rsna")
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-4)
    args = parser.parse_args()
    train(args)
