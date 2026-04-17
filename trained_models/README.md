# Trained Models

This folder stores model artifacts produced after training on MillionAnimals data.

The structure mirrors the model-artifact organization used in MillionTrees and is intended
to keep DeepForest runs reproducible and easy to compare across experiments.

## Layout

- `deepforest/checkpoints/` - Model checkpoints (`.ckpt`, `.pt`)
- `deepforest/lightning_logs/` - PyTorch Lightning logs and metrics
- `deepforest/configs/` - Training configs used to create each run
- `deepforest/exports/` - Exported inference-ready model files
- `deepforest/predictions/` - Validation/test predictions from trained checkpoints
- `slurm/` - Optional SLURM job scripts for training/evaluation

## Suggested Naming

Use experiment IDs with date and geometry:

- `df_YYYYMMDD_boxes_v01`
- `df_YYYYMMDD_points_v01`
- `df_YYYYMMDD_polygons_v01`

This folder is scaffolding only; no model files are committed yet.
