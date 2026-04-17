"""Dataset prep scaffold for: Drone and ground-truth data collection, image annotation and machine learning: A protocol for coastal habitat mapping and classification.

Auto-generated from the MillionAnimals airborne worksheet.
NOTE: This file is a template only; no downloads are performed here.
"""

from pathlib import Path
import pandas as pd


SOURCE_TITLE = 'Drone and ground-truth data collection, image annotation and machine learning: A protocol for coastal habitat mapping and classification'
SOURCE_SLUG = 'drone_and_ground_truth_data_collection_image_annotation_and_machine_learning_a_protocol_fo'
WORKSHEET_LINK = 'https://www.sciencedirect.com/science/article/pii/S2215016124003868'
CANDIDATE_DOWNLOAD_LINKS = 'https://www.sciencedirect.com/science/article/pii/S2215016124003868; https://github.com/SeaBee-no/annotation/blob/main/README.md; https://seabee-no.github.io/documentation/'


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
