"""Dataset prep scaffold for: Iguanas from above: Citizen scientists provide reliable counts of endangered Galápagos marine iguanas from drone imagery.

Auto-generated from the MillionAnimals airborne worksheet.
NOTE: This file is a template only; no downloads are performed here.
"""

from pathlib import Path
import pandas as pd


SOURCE_TITLE = 'Iguanas from above: Citizen scientists provide reliable counts of endangered Galápagos marine iguanas from drone imagery'
SOURCE_SLUG = 'iguanas_from_above_citizen_scientists_provide_reliable_counts_of_endangered_gal_pagos_mari'
WORKSHEET_LINK = 'https://www.biorxiv.org/content/10.1101/2024.02.09.579637v1.full.pdf'
CANDIDATE_DOWNLOAD_LINKS = 'https://www.biorxiv.org/content/10.1101/2024.02.09.579637v1.full.pdf; https://figshare.com/articles/dataset/Gold_Standard_Dataset_-_Iguanas_from_Above_Project/25196306'


def build_annotations(raw_dir: str = "data/raw", output_dir: str = "data_prep/annotations") -> Path:
    """Create an annotation CSV scaffold for this source."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(columns=["geometry", "image_path", "label", "source"])
    target = output_path / f"{SOURCE_SLUG}_annotations.csv"
    df.to_csv(target, index=False)
    return target


if __name__ == "__main__":
    out = build_annotations()
    print(f"Wrote scaffold annotations to: {out}")
