"""Build AnimalBoxes-style annotations from the Kaggle NOAA Right Whale Recognition release.

The competition is primarily *individual* identification (fine-grained classification) on
roughly centered whale crops. For MillionAnimals / DeepForest box packaging we emit one
box per training row. By default the box spans the full image (weak localization). If you
have a forum CSV with head bounding boxes (e.g. columns Image, x, y, width, height), pass
``--bbox-csv``; rows are merged with ``train.csv`` on the image filename.

Output columns: geometry, image_path, label, source

Do not commit Kaggle data; keep downloads on scratch or another ignored directory.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from PIL import Image
from shapely.geometry import box


def _norm_cols(df: pd.DataFrame) -> dict[str, str]:
    """Map lowercased column names to actual column names."""
    return {c.lower(): c for c in df.columns}


def _pick_image_column(df: pd.DataFrame) -> str:
    nc = _norm_cols(df)
    for key in ("image", "filename", "filepath"):
        if key in nc:
            return nc[key]
    raise ValueError(
        f"Could not infer image filename column from columns: {list(df.columns)}. "
        "Expected something like 'Image'."
    )


def _pick_whale_id_column(df: pd.DataFrame) -> str | None:
    nc = _norm_cols(df)
    for key in ("whaleid", "whale_id", "label", "individual"):
        if key in nc:
            return nc[key]
    return None


def _full_image_box(path: Path) -> str:
    with Image.open(path) as im:
        w, h = im.size
    return box(0, 0, w, h).wkt


def _xywh_box(row, xcol: str, ycol: str, wcol: str, hcol: str) -> str:
    x0 = float(row[xcol])
    y0 = float(row[ycol])
    ww = float(row[wcol])
    hh = float(row[hcol])
    return box(x0, y0, x0 + ww, y0 + hh).wkt


def build_annotations(
    data_root: Path,
    output_csv: Path,
    imgs_subdir: str = "imgs",
    bbox_csv: Path | None = None,
    label_mode: str = "species",
) -> Path:
    data_root = data_root.resolve()
    imgs_dir = data_root / imgs_subdir
    train_csv = data_root / "train.csv"
    if not train_csv.exists():
        raise FileNotFoundError(f"Missing train.csv under {data_root}")
    if not imgs_dir.is_dir():
        raise FileNotFoundError(f"Missing images directory {imgs_dir}")

    train = pd.read_csv(train_csv)
    img_col = _pick_image_column(train)
    wid_col = _pick_whale_id_column(train)

    if bbox_csv is not None:
        bb = pd.read_csv(bbox_csv)
        bb_img = _pick_image_column(bb)
        nc = _norm_cols(bb)
        for req in ("x", "y", "width", "height"):
            if req not in nc:
                raise ValueError(
                    f"--bbox-csv must contain x, y, width, height columns; got {list(bb.columns)}"
                )
        xcol, ycol, wcol, hcol = nc["x"], nc["y"], nc["width"], nc["height"]
        merged = train.merge(bb, left_on=img_col, right_on=bb_img, how="inner", suffixes=("", "_bbox"))
        if merged.empty:
            raise ValueError("No rows after merging train.csv with --bbox-csv on image filename.")
        use_bbox = True
        work = merged
        image_key = img_col if img_col in merged.columns else bb_img
    else:
        use_bbox = False
        work = train.copy()
        image_key = img_col

    rows = []
    for _, row in work.iterrows():
        fname = str(row[image_key]).strip()
        ipath = imgs_dir / fname
        if not ipath.is_file():
            continue
        if use_bbox:
            geom = _xywh_box(row, xcol, ycol, wcol, hcol)
        else:
            geom = _full_image_box(ipath)

        whale_part = ""
        if wid_col and wid_col in row.index and pd.notna(row[wid_col]):
            whale_part = f";whale_id={row[wid_col]}"
        source = f"noaa_right_whale_kaggle{whale_part}"

        if label_mode == "species":
            label = "RightWhale"
        elif label_mode == "animal":
            label = "Animal"
        elif label_mode == "individual":
            if not wid_col or wid_col not in row.index or pd.isna(row[wid_col]):
                raise ValueError("label_mode=individual requires a whale id column in train.csv")
            label = str(row[wid_col])
        else:
            raise ValueError(label_mode)

        rows.append(
            {
                "geometry": geom,
                "image_path": str(ipath.resolve()),
                "label": label,
                "source": source,
            }
        )

    if not rows:
        raise ValueError("No valid rows (check that filenames in train.csv match files in imgs/).")

    out = pd.DataFrame(rows)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output_csv, index=False)
    return output_csv


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--data-root",
        type=Path,
        required=True,
        help="Directory containing train.csv and the images folder (default name: imgs/).",
    )
    p.add_argument(
        "--imgs-subdir",
        default="imgs",
        help="Subdirectory of data-root with JPEGs (default: imgs).",
    )
    p.add_argument(
        "--bbox-csv",
        type=Path,
        default=None,
        help="Optional CSV with Image + x,y,width,height merged to train.csv on filename.",
    )
    p.add_argument(
        "--label-mode",
        choices=("species", "animal", "individual"),
        default="species",
        help="species=RightWhale; animal=Animal (matches AnimalBoxes single-class training); "
        "individual uses whale id strings (unusual for DeepForest).",
    )
    p.add_argument(
        "--output",
        type=Path,
        default=Path("annotations_noaa_right_whale.csv"),
        help="Output CSV path.",
    )
    args = p.parse_args()
    path = build_annotations(
        data_root=args.data_root,
        output_csv=args.output,
        imgs_subdir=args.imgs_subdir,
        bbox_csv=args.bbox_csv,
        label_mode=args.label_mode,
    )
    print(f"Wrote {path} with {len(pd.read_csv(path))} rows.")


if __name__ == "__main__":
    main()
