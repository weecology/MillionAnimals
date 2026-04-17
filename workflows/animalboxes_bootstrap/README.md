# AnimalBoxes Bootstrap Workflow

This is a minimal end-to-end path for testing:

1. data_prep download + format
2. package into `AnimalBoxes_v*` dataloader layout
3. train DeepForest on `AnimalBoxes`

For this bootstrap, we use `MiniTreeBoxes_v0.10` as a lightweight proxy source to validate
the pipeline plumbing before animal-specific datasets are downloaded.

## 1) Download + format annotations

```bash
python3 data_prep/sources_airborne/bootstrap_animalboxes_v01.py
```

This writes:

- `workflows/animalboxes_bootstrap/raw/MiniTreeBoxes_v0.10/` (downloaded bootstrap source files)
- `data_prep/annotations/bootstrap_animalboxes_v01_annotations.csv`

## 2) Package for dataloader

```bash
python3 data_prep/package_datasets.py \
  --bootstrap-annotations data_prep/annotations/bootstrap_animalboxes_v01_annotations.csv \
  --bootstrap-version 0.3 \
  --bootstrap-base-dir workflows/animalboxes_bootstrap/packaged
```

This writes:

- `workflows/animalboxes_bootstrap/packaged/AnimalBoxes_v0.3/`
- `workflows/animalboxes_bootstrap/packaged/MiniAnimalBoxes_v0.3/`

## 3) Train DeepForest on AnimalBoxes

Install DeepForest if needed:

```bash
pip install deepforest
```

Train:

```bash
python3 training/boxes/train_animalboxes_deepforest.py \
  --root-dir workflows/animalboxes_bootstrap/packaged \
  --version 0.3 \
  --split-scheme official \
  --max-epochs 1 \
  --batch-size 4 \
  --output-dir trained_models/deepforest
```

## One-command run

```bash
bash workflows/animalboxes_bootstrap/run_end_to_end.sh
```
