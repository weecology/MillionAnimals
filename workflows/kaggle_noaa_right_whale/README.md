# NOAA Right Whale (Kaggle) → AnimalBoxes on HPC

This folder is a **layout convention** for scratch-backed runs: keep heavy artifacts here (gitignored) or on cluster scratch, not in the git index.

## Quick path

1. Download with the Kaggle CLI (see `data_prep/sources_kaggle/noaa_right_whale_recognition/README.md`).
2. Run `format_for_animalboxes.py` with `--data-root` pointing at the folder that contains `train.csv` and `imgs/`.
3. Run `data_prep/package_datasets.py --bootstrap-annotations ... --bootstrap-base-dir workflows/kaggle_noaa_right_whale/packaged`.
4. Train with `training/boxes/train_animalboxes_deepforest.py --root-dir .../packaged --version 0.3` (note: `root_dir` is the directory that **contains** `AnimalBoxes_v0.3/`, not the dataset folder itself).

Example SLURM driver: `train.slurm` (edit `REPO`, module lines, and partitions for your site).
