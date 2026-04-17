"""Dataset prep scaffold for: Detecting African hoofed animals in aerial imagery using convolutional neural network.

Auto-generated from the MillionAnimals airborne worksheet.
NOTE: This file is a template only; no downloads are performed here.
"""

from pathlib import Path
import pandas as pd


SOURCE_TITLE = 'Detecting African hoofed animals in aerial imagery using convolutional neural network'
SOURCE_SLUG = 'detecting_african_hoofed_animals_in_aerial_imagery_using_convolutional_neural_network'
WORKSHEET_LINK = 'https://zenodo.org/records/5787947'
CANDIDATE_DOWNLOAD_LINKS = 'https://zenodo.org/records/5787947'


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
