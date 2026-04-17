"""Dataset prep scaffold for: WildlifeMapper: Aerial Image Analysis for Multi-Species Detection and Identification.

Auto-generated from the MillionAnimals airborne worksheet.
NOTE: This file is a template only; no downloads are performed here.
"""

from pathlib import Path
import pandas as pd


SOURCE_TITLE = 'WildlifeMapper: Aerial Image Analysis for Multi-Species Detection and Identification'
SOURCE_SLUG = 'wildlifemapper_aerial_image_analysis_for_multi_species_detection_and_identification'
WORKSHEET_LINK = 'https://openaccess.thecvf.com/content/CVPR2024/html/Kumar_WildlifeMapper_Aerial_Image_Analysis_for_Multi-Species_Detection_and_Identification_CVPR_2024_paper.html'
CANDIDATE_DOWNLOAD_LINKS = 'https://openaccess.thecvf.com/content/CVPR2024/html/Kumar_WildlifeMapper_Aerial_Image_Analysis_for_Multi-Species_Detection_and_Identification_CVPR_2024_paper.html; https://github.com/UCSB-VRL/WildlifeMapper'


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
