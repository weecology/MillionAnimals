"""Bootstrap a small source for AnimalBoxes workflow development.

This script creates a data_prep-friendly annotations CSV with columns:
    geometry, image_path, label, source

It does NOT package data for dataloaders directly; use data_prep/package_datasets.py
with --bootstrap-annotations for that next step.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

import pandas as pd
from shapely.geometry import box

# Allow running without editable install.
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from millionanimals.datasets.download_utils import extract_archive


def build_annotations(download_root: Path, output_csv: Path, source_zip_url: str) -> Path:
    download_root.mkdir(parents=True, exist_ok=True)
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    archive_name = Path(source_zip_url).name
    archive_path = download_root / archive_name
    extracted_dir = download_root / archive_name.replace(".zip", "")

    # Download with curl for broad TLS compatibility across local Python builds.
    if not archive_path.exists():
        os_cmd = f'curl -L "{source_zip_url}" -o "{archive_path}"'
        rc = os.system(os_cmd)
        if rc != 0:
            raise RuntimeError(f"Download failed for {source_zip_url}")

    if not extracted_dir.exists():
        extract_archive(str(archive_path), str(download_root), remove_finished=False)

    csv_candidates = [
        extracted_dir / "official.csv",
        extracted_dir / "random.csv",
        download_root / "official.csv",
        download_root / "random.csv",
    ]
    official_csv = next((p for p in csv_candidates if p.exists()), None)
    if official_csv is None:
        raise FileNotFoundError("Could not find official.csv or random.csv after extraction.")

    images_candidates = [extracted_dir / "images", download_root / "images"]
    images_dir = next((p for p in images_candidates if p.exists()), None)
    if images_dir is None:
        raise FileNotFoundError("Could not find extracted images/ directory.")

    if not images_dir.exists():
        raise FileNotFoundError(f"Expected {images_dir} after extraction.")

    df = pd.read_csv(official_csv)
    required = {"xmin", "ymin", "xmax", "ymax", "filename", "source"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"official.csv is missing required columns: {missing}")

    # Convert boxes to polygon WKT for the generic data_prep schema.
    df["geometry"] = df.apply(
        lambda row: box(row["xmin"], row["ymin"], row["xmax"], row["ymax"]).wkt,
        axis=1,
    )
    df["image_path"] = df["filename"].apply(lambda x: str((images_dir / x).resolve()))
    df["label"] = "Animal"
    df["source"] = df["source"].astype(str) + " (bootstrap_from_milliontrees)"

    out = df[["geometry", "image_path", "label", "source"]].copy()
    out.to_csv(output_csv, index=False)
    return output_csv


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download AnimalBoxes v0.1 and format to data_prep annotation schema."
    )
    parser.add_argument(
        "--download-root",
        type=Path,
        default=Path("workflows/animalboxes_bootstrap/raw"),
        help="Directory for raw downloaded/extracted release data.",
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=Path("data_prep/annotations/bootstrap_animalboxes_v01_annotations.csv"),
        help="Output annotations CSV path (data_prep schema).",
    )
    parser.add_argument(
        "--source-zip-url",
        type=str,
        default="https://data.rc.ufl.edu/pub/ewhite/MillionTrees/MiniTreeBoxes_v0.10.zip",
        help="Zip URL containing official.csv and images/ for bootstrap.",
    )
    args = parser.parse_args()

    out = build_annotations(args.download_root, args.output_csv, args.source_zip_url)
    print(f"Wrote formatted annotations: {out}")


if __name__ == "__main__":
    main()
