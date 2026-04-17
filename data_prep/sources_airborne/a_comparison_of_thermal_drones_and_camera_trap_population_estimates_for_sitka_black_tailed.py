"""Dataset prep scaffold for: A comparison of thermal drones and camera trap population estimates for Sitka black‐tailed deer in Alaska.

Auto-generated from the MillionAnimals airborne worksheet.
NOTE: This file is a template only; no downloads are performed here.
"""

from pathlib import Path
import pandas as pd


SOURCE_TITLE = 'A comparison of thermal drones and camera trap population estimates for Sitka black‐tailed deer in Alaska'
SOURCE_SLUG = 'a_comparison_of_thermal_drones_and_camera_trap_population_estimates_for_sitka_black_tailed'
WORKSHEET_LINK = 'https://www.researchgate.net/publication/386173097_A_comparison_of_thermal_drones_and_camera_trap_population_estimates_for_Sitka_black-tailed_deer_in_Alaska'
CANDIDATE_DOWNLOAD_LINKS = 'https://www.researchgate.net/publication/386173097_A_comparison_of_thermal_drones_and_camera_trap_population_estimates_for_Sitka_black-tailed_deer_in_Alaska; https://datadryad.org/stash/dataset/doi:10.5061/dryad.brv15dvk2'


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
