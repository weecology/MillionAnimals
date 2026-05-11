#!/bin/bash
#SBATCH --job-name=noaa-whale-boxes
#SBATCH --time=04:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --gres=gpu:1
#SBATCH --output=slurm-%j.out
#SBATCH --error=slurm-%j.err

# Edit for your cluster (modules, partitions, account).
set -euo pipefail

REPO="${REPO:-$HOME/MillionAnimals}"
DATA_ROOT="${DATA_ROOT:-/scratch/$USER/noaa-right-whale-recognition}"
WORKDIR="${WORKDIR:-$REPO/workflows/kaggle_noaa_right_whale}"

# module load cuda cudnn python  # example

cd "$REPO"
python -m pip install -q -r requirements.txt

python data_prep/sources_kaggle/noaa_right_whale_recognition/format_for_animalboxes.py \
  --data-root "$DATA_ROOT" \
  --output "$WORKDIR/annotations.csv" \
  --label-mode animal

python data_prep/package_datasets.py \
  --bootstrap-annotations "$WORKDIR/annotations.csv" \
  --bootstrap-version 0.3 \
  --bootstrap-base-dir "$WORKDIR/packaged"

python training/boxes/train_animalboxes_deepforest.py \
  --root-dir "$WORKDIR/packaged" \
  --version 0.3
