# MillionAnimals Data Preparation

This directory contains utilities for preparing and packaging animal detection datasets for the MillionAnimals benchmark.

## Directory Structure

- **package_datasets.py** - Main script that combines and packages all datasets
- **utilities.py** - General utility functions
- **label_studio_utils.py** - Utilities for working with Label Studio annotations
- **annotation_loop.py** - Script for iterative annotation workflow
- **preprocess_polygons.py** - Utilities for processing polygon annotations
- **Dataset scripts** - Individual Python scripts for each dataset (to be added)

## Adding a New Animal Dataset

1. **Create a dataset script**: Copy `DATASET_TEMPLATE.py` and rename it for your dataset (e.g., `WildlifeDrones2024.py`)

2. **Process your data**: In your dataset script, load and process your data to create an `annotations.csv` file with these required columns:
   - `geometry`: Spatial geometry (WKT format) - polygon, point, or bounding box
   - `image_path`: Path to the image file
   - `label`: Always "Animal" for this benchmark
   - `source`: Dataset name/citation (e.g., "Wildlife Drones 2024")

3. **Add to package_datasets.py**: Add the path to your `annotations.csv` file to the appropriate list in `package_datasets.py`:
   - `AnimalBoxes` - for bounding box annotations
   - `AnimalPoints` - for point annotations  
   - `AnimalPolygons` - for polygon annotations

## Example Dataset Script

```python
from deepforest.utilities import read_file
import pandas as pd
import geopandas as gpd

# Load your annotations (CSV, shapefile, etc.)
gdf = gpd.read_file("/path/to/your/annotations.shp")

# Add required columns
gdf["image_path"] = "drone_image_001.tif"  # or map to appropriate images
gdf["label"] = "Animal"
gdf["source"] = "Wildlife Survey 2024"

# Convert to DataFrame with proper geometry
df = read_file(gdf, root_dir="/path/to/images/")

# Save annotations
df.to_csv("/path/to/output/annotations.csv", index=False)
```

## Running the Packaging Script

Once you've added your dataset paths to `package_datasets.py`:

```bash
python package_datasets.py
```

This will:
- Combine all datasets
- Create train/test splits (official, cross-geometry, zero-shot)
- Generate mini datasets for visualization
- Package everything into zip files

## Dataset Requirements

- **Images**: RGB images in standard formats (TIFF, PNG, JPG)
- **Annotations**: Must include geometry, image_path, label, and source
- **Coordinate System**: Annotations should be in pixel coordinates relative to the image

## Notes

- The `label` field should always be "Animal" for consistency
- The `source` field should identify the dataset for proper attribution
- Images with alpha channels will be automatically converted to RGB