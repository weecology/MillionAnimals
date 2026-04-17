"""Train DeepForest (RetinaNet) on MillionAnimals AnimalBoxes.

This script expects a packaged dataset directory like:
    <root_dir>/AnimalBoxes_v<version>/
      - official.csv
      - images/

Use this workflow to generate a local package:
1) data_prep/sources_airborne/bootstrap_animalboxes_v01.py
2) data_prep/package_datasets.py --bootstrap-annotations ...
3) run this script
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import pytorch_lightning as pl
import torch

# Allow running without editable install.
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from millionanimals import get_dataset
from millionanimals.common.data_loaders import get_eval_loader, get_train_loader


class MillionAnimalsBatchAdapter:
    """Adapt MillionAnimals box batches to DeepForest expected training format."""

    def __init__(self, loader, filename_id_to_path=None):
        self.loader = loader
        self.filename_id_to_path = filename_id_to_path or {}

    def __iter__(self):
        for metadata, images, targets in self.loader:
            paths = [
                self.filename_id_to_path.get(int(metadata[i, 0]), str(int(metadata[i, 0])))
                for i in range(len(metadata))
            ]
            adapted = []
            for t in targets:
                boxes = t["y"]
                if boxes.dim() == 1:
                    boxes = boxes.unsqueeze(0)
                if len(boxes) == 0:
                    boxes = torch.zeros((0, 4), dtype=torch.float32)
                labels = t["labels"]
                if not isinstance(labels, torch.Tensor):
                    labels = torch.tensor(labels, dtype=torch.int64)
                else:
                    labels = labels.long()
                adapted.append({"boxes": boxes.float(), "labels": labels})
            yield paths, images, adapted

    def __len__(self):
        return len(self.loader)


def predict_batch(model, images):
    """Run DeepForest inference and return MillionAnimals-style prediction dicts."""
    device = next(model.parameters()).device
    images = images.to(device) if isinstance(images, torch.Tensor) else torch.tensor(images).to(device)
    model.model.eval()
    with torch.no_grad():
        predictions = model.model(images)

    result = []
    for pred in predictions:
        boxes = pred.get("boxes", torch.zeros((0, 4)))
        if len(boxes) == 0:
            result.append({
                "y": torch.zeros((0, 4), dtype=torch.float32),
                "labels": torch.zeros((0,), dtype=torch.int64),
                "scores": torch.zeros((0,), dtype=torch.float32),
            })
        else:
            result.append({
                "y": boxes.detach().float().cpu(),
                "labels": pred["labels"].detach().cpu().long(),
                "scores": pred["scores"].detach().float().cpu(),
            })
    return result


def evaluate(model, dataset, test_subset, batch_size=4, num_workers=0):
    test_loader = get_eval_loader(
        "standard",
        test_subset,
        batch_size=batch_size,
        num_workers=num_workers,
    )
    all_y_pred, all_y_true = [], []
    for _, images, targets in test_loader:
        preds = predict_batch(model, images)
        all_y_pred.extend(preds)
        all_y_true.extend(targets)
    results, results_str = dataset.eval(
        all_y_pred, all_y_true, test_subset.metadata_array[:len(all_y_true)]
    )
    return results, results_str


def main():
    parser = argparse.ArgumentParser(description="Train DeepForest on AnimalBoxes.")
    parser.add_argument(
        "--root-dir",
        type=str,
        default="workflows/animalboxes_bootstrap/packaged",
        help="Directory containing AnimalBoxes_v<version>/",
    )
    parser.add_argument("--version", type=str, default="0.3")
    parser.add_argument(
        "--split-scheme",
        type=str,
        default="official",
        choices=["official", "zeroshot", "crossgeometry"],
    )
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--max-epochs", type=int, default=1)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--output-dir", type=str, default="trained_models/deepforest")
    parser.add_argument("--devices", type=int, default=1)
    parser.add_argument("--accelerator", type=str, default="auto")
    parser.add_argument("--limit-train-batches", type=float, default=1.0)
    parser.add_argument("--limit-val-batches", type=float, default=1.0)
    parser.add_argument(
        "--use-deepforest-validation",
        action="store_true",
        help="Enable DeepForest internal validation loop during trainer.fit().",
    )
    parser.add_argument(
        "--pretrained-model",
        type=str,
        default="weecology/deepforest-tree",
        help="DeepForest model identifier used by model.load_model(); set to 'none' to skip.",
    )
    args = parser.parse_args()

    try:
        from deepforest import main as df_main
    except ImportError as exc:
        raise SystemExit(
            "deepforest is required for training. Install with `pip install deepforest`."
        ) from exc

    os.makedirs(args.output_dir, exist_ok=True)

    dataset = get_dataset(
        "AnimalBoxes",
        version=args.version,
        download=False,
        root_dir=args.root_dir,
        split_scheme=args.split_scheme,
    )
    train_subset = dataset.get_subset("train")
    test_subset = dataset.get_subset("test")

    if len(train_subset) == 0:
        raise SystemExit("Training subset is empty; check your packaging/splits.")
    if len(test_subset) == 0:
        print("Warning: test subset is empty; training will proceed without validation.")

    train_loader = get_train_loader(
        "standard",
        train_subset,
        batch_size=args.batch_size,
        num_workers=args.num_workers,
    )
    val_loader = get_eval_loader(
        "standard",
        test_subset,
        batch_size=args.batch_size,
        num_workers=args.num_workers,
    )
    has_val = len(val_loader) > 0

    filename_id_to_path = dataset._filename_id_to_code
    train_adapted = MillionAnimalsBatchAdapter(train_loader, filename_id_to_path)
    val_adapted = MillionAnimalsBatchAdapter(val_loader, filename_id_to_path) if has_val else None
    train_with_val = args.use_deepforest_validation and has_val

    images_dir = str(Path(dataset._data_dir) / "images")
    split_csv = str(Path(dataset._data_dir) / f"{args.split_scheme}.csv")
    model = df_main.deepforest(
        config_args={
            # DeepForest currently validates config csv_file/root_dir during on_fit_start,
            # even when existing dataloaders are provided.
            "train": {
                "epochs": args.max_epochs,
                "lr": args.lr,
                "csv_file": split_csv,
                "root_dir": images_dir,
            },
            "validation": {
                "root_dir": images_dir,
                "csv_file": split_csv if train_with_val else None,
            },
            "batch_size": args.batch_size,
            "devices": args.devices,
            "accelerator": args.accelerator,
            "workers": args.num_workers,
        },
        existing_train_dataloader=train_adapted,
        existing_val_dataloader=val_adapted if train_with_val else None,
    )
    if args.pretrained_model and args.pretrained_model.lower() != "none":
        model.load_model(args.pretrained_model)

    callbacks = []
    checkpoint_cb = None
    if train_with_val:
        checkpoint_cb = pl.callbacks.ModelCheckpoint(
            dirpath=os.path.join(args.output_dir, "checkpoints"),
            filename="animalboxes-best",
            monitor="val_bbox_regression",
            mode="min",
            save_last=True,
            save_top_k=1,
        )
        callbacks.append(checkpoint_cb)

    model.create_trainer(
        callbacks=callbacks,
        default_root_dir=args.output_dir,
        limit_train_batches=args.limit_train_batches,
        limit_val_batches=args.limit_val_batches if train_with_val else 0,
        num_sanity_val_steps=0,
    )
    model.trainer.fit(model)

    # Evaluate best/last checkpoint if available, otherwise current model.
    if checkpoint_cb is not None:
        best_path = checkpoint_cb.best_model_path or checkpoint_cb.last_model_path
        if best_path:
            # Adapter class was pickled under __main__; register it for restore.
            sys.modules["__main__"].MillionAnimalsBatchAdapter = MillionAnimalsBatchAdapter
            model = df_main.deepforest.load_from_checkpoint(best_path, weights_only=False)

    _, results_str = evaluate(
        model=model,
        dataset=dataset,
        test_subset=test_subset,
        batch_size=args.batch_size,
        num_workers=args.num_workers,
    )
    print(results_str)
    results_path = os.path.join(args.output_dir, f"results_{args.split_scheme}.txt")
    with open(results_path, "w") as f:
        f.write(results_str)
    print(f"Saved evaluation results to {results_path}")


if __name__ == "__main__":
    main()
