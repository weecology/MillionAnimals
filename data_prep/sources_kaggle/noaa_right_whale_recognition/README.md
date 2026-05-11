# NOAA Right Whale Recognition (Kaggle)

Competition overview: [NOAA Right Whale Recognition](https://www.kaggle.com/competitions/noaa-right-whale-recognition/overview).

The official bundle includes `train.csv` (columns include `Image` and `whaleID`) and an `imgs/` directory of JPEGs. The original task is identification of individual North Atlantic right whales from aerial photographs, not a full aerial survey detection benchmark. For AnimalBoxes packaging we emit one bounding box per row: by default the box is the **entire image**; you can optionally merge a forum-provided head box CSV (see `--bbox-csv` in `format_for_animalboxes.py`).

## HPC: credentials and download

1. Create a Kaggle API token (Account → API → Create New Token). You get `kaggle.json` with `username` and `key`.
2. On the cluster, use a private path (never commit this file):

   ```bash
   mkdir -p ~/.kaggle
   chmod 700 ~/.kaggle
   # copy kaggle.json here, then:
   chmod 600 ~/.kaggle/kaggle.json
   ```

3. Install the CLI in your job environment (`pip install kaggle` or your image/conda env).

4. Download and unzip into a **scratch** directory (large `imgs` archive):

   ```bash
   COMP=noaa-right-whale-recognition
   DEST=/scratch/$USER/$COMP
   mkdir -p "$DEST" && cd "$DEST"
   kaggle competitions download -c "$COMP"
   unzip -q '*.zip'   # or unzip each archive; ensure train.csv and imgs/ end up in DEST
   ```

5. Point `--data-root` at the directory that contains both `train.csv` and `imgs/`.

## Build annotations and package AnimalBoxes

From the repo root (with your env and `pip install -r requirements.txt`):

```bash
python data_prep/sources_kaggle/noaa_right_whale_recognition/format_for_animalboxes.py \
  --data-root /scratch/$USER/noaa-right-whale-recognition \
  --output workflows/kaggle_noaa_right_whale/annotations.csv \
  --label-mode animal

python data_prep/package_datasets.py \
  --bootstrap-annotations workflows/kaggle_noaa_right_whale/annotations.csv \
  --bootstrap-version 0.3 \
  --bootstrap-base-dir workflows/kaggle_noaa_right_whale/packaged
```

Then train (example):

```bash
python training/boxes/train_animalboxes_deepforest.py \
  --root-dir workflows/kaggle_noaa_right_whale/packaged \
  --version 0.3
```

Adjust `--bootstrap-base-dir`, paths, and SLURM resource requests for your site. A template job script lives under `workflows/kaggle_noaa_right_whale/train.slurm`.

## Notes

- **Do not commit** downloaded images or `kaggle.json`; those paths should stay in ignored or scratch storage.
- The bundled `AnimalBoxes` dataloader uses a single detection class internally; `--label-mode animal` aligns with that. Use `species` or `individual` only if your downstream tooling reads the annotation CSV before packaging.
- Forum threads linked from historical solutions describe optional head localization CSVs; if column names differ from `Image`, `x`, `y`, `width`, `height`, adapt the CSV or extend `format_for_animalboxes.py`.
