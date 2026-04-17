#!/usr/bin/env bash
set -euo pipefail

# End-to-end bootstrap workflow:
# 1) Download + format source annotations
# 2) Package into AnimalBoxes_v0.3 format
# 3) Train a smoke DeepForest run

python3 data_prep/sources_airborne/bootstrap_animalboxes_v01.py

python3 data_prep/package_datasets.py \
  --bootstrap-annotations data_prep/annotations/bootstrap_animalboxes_v01_annotations.csv \
  --bootstrap-version 0.3 \
  --bootstrap-base-dir workflows/animalboxes_bootstrap/packaged

python3 training/boxes/train_animalboxes_deepforest.py \
  --root-dir workflows/animalboxes_bootstrap/packaged \
  --version 0.3 \
  --split-scheme official \
  --max-epochs 1 \
  --batch-size 2 \
  --num-workers 0 \
  --limit-train-batches 0.2 \
  --output-dir trained_models/deepforest/bootstrap_run \
  --pretrained-model none

echo "Workflow complete."
