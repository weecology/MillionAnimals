"""
Template for processing animal dataset: YourDatasetName
"""
from deepforest.utilities import read_file
from deepforest.preprocess import split_raster
from deepforest.visualize import plot_results
import os
import geopandas as gpd
import pandas as pd
import rasterio as rio

def process_yourdatasetname():
    """Process YourDatasetName dataset for MillionAnimals benchmark."""
    
    # Load your data here (shapefile, CSV, etc.)
    # Example:
    # gdf = gpd.read_file("/path/to/your/data.shp")
    
    # Required columns:
    # - geometry: The spatial geometry (polygon, point, or box)
    # - image_path: Path to the image file
    # - label: Always "Animal" for this benchmark
    # - source: Citation or dataset name
    
    # Example processing:
    # gdf["image_path"] = "your_image.tif"
    # gdf["label"] = "Animal"
    # gdf["source"] = "YourDatasetName"
    
    # Save annotations
    # df.to_csv("/path/to/output/annotations.csv", index=False)
    
    pass

if __name__ == "__main__":
    process_yourdatasetname()
