"""Dataset prep scaffold for: An experimental approach to evaluate the potential of drones in terrestrial mammal research: a gregarious ungulate as a study model.

Auto-generated from the MillionAnimals airborne worksheet.
NOTE: This file is a template only; no downloads are performed here.
"""

from pathlib import Path
import pandas as pd


SOURCE_TITLE = 'An experimental approach to evaluate the potential of drones in terrestrial mammal research: a gregarious ungulate as a study model'
SOURCE_SLUG = 'an_experimental_approach_to_evaluate_the_potential_of_drones_in_terrestrial_mammal_researc'
WORKSHEET_LINK = 'https://royalsocietypublishing.org/doi/full/10.1098/rsos.191482'
CANDIDATE_DOWNLOAD_LINKS = 'https://royalsocietypublishing.org/doi/full/10.1098/rsos.191482; https://rs.figshare.com/collections/Supplementary_material_from_An_experimental_approach_to_evaluate_the_potential_of_drones_in_terrestrial_mammal_research_a_gregarious_ungulate_as_a_study_model_/4784556'


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
