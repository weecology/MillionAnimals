from deepforest.preprocess import split_raster, read_file
from deepforest.visualize import plot_results
import pandas as pd
import geopandas as gpd
import rasterio
import numpy as np
import random
import os
import cv2

def clean_up_rgb():
    rgb = "/orange/ewhite/DeepForest/Hickman2021/RCD105_MA14_21_orthomosaic_20141023_reprojected_full_res_crop1.tif"
    src = rasterio.open(rgb)
    r = src.read()
    print(r.shape)
    r = r[:3,:,:]
    r = r/65535.0 * 255
    # Set no data to 0
    r[np.isnan(r)] = 0
    r = r.astype(int)

    # Save raster
    meta = src.meta.copy()
    meta.update(count = 3)
    meta.update(dtype=rasterio.uint8)
    meta.update(nodata=0)

    with rasterio.open("/orange/ewhite/DeepForest/Hickman2021/RCD105_MA14_21_orthomosaic_20141023_reprojected_full_res_crop1_rgb_corrected.tif", 'w', **meta) as dst:
        dst.write(r)

    rgb = "/orange/ewhite/DeepForest/Hickman2021/RCD105_MA14_21_orthomosaic_20141023_reprojected_full_res_crop2.tif"
    src = rasterio.open(rgb)
    r = src.read()
    print(r.shape)
    r = r[:3,:,:]
    r = r/65535.0 * 255
    r[np.isnan(r)] = 0
    r = r.astype(int)

    # Save raster
    meta = src.meta.copy()
    meta.update(count = 3)
    meta.update(dtype=rasterio.uint8)
    meta.update(nodata=0)

    with rasterio.open("/orange/ewhite/DeepForest/Hickman2021/RCD105_MA14_21_orthomosaic_20141023_reprojected_full_res_crop2_rgb_corrected.tif", 'w', **meta) as dst:
        dst.write(r)

def Hickman2021():
    rgb = "/orange/ewhite/DeepForest/Hickman2021/RCD105_MA14_21_orthomosaic_20141023_reprojected_full_res_crop1_rgb_corrected.tif"
    shp = "/orange/ewhite/DeepForest/Hickman2021/manual_crowns_sepilok.shp"
    gdf = gpd.read_file(shp)
    gdf["image_path"] = rgb
    gdf["label"] = "Animal"
    annotations = read_file(gdf)
    annotations = annotations[annotations.is_valid]
    annotations["image_path"] = os.path.basename(rgb)
    annotations = read_file(annotations, root_dir="/orange/ewhite/DeepForest/Hickman2021/")

    train_annotations = split_raster(
        annotations,
        path_to_raster=rgb,
        patch_size=1500,
        allow_empty=False,
        base_dir="/orange/ewhite/DeepForest/Hickman2021/pngs/")
    
    rgb = "/orange/ewhite/DeepForest/Hickman2021/RCD105_MA14_21_orthomosaic_20141023_reprojected_full_res_crop2_rgb_corrected.tif"
    annotations["image_path"] = os.path.basename(rgb)
    test_annotations = split_raster(
        annotations,
        path_to_raster=rgb,
        patch_size=1500,
        allow_empty=False,  
        base_dir="/orange/ewhite/DeepForest/Hickman2021/pngs/")

    test_annotations["split"] = "test"
    train_annotations["split"] = "train"
    annotations = pd.concat([test_annotations, train_annotations])
    # Make full path
    annotations["image_path"] = "/orange/ewhite/DeepForest/Hickman2021/pngs/" + annotations["image_path"]
    annotations["source"] = "Hickman 2021"
    annotations.to_csv("/orange/ewhite/DeepForest/Hickman2021/annotations.csv")

    return annotations

if __name__ == "__main__":
    #clean_up_rgb()
    annotations_base_path = Hickman2021()    
    annotations_base_path["image_path"] = annotations_base_path["image_path"].apply(lambda x: os.path.basename(x))
    annotations_base_path.root_dir = "/orange/ewhite/DeepForest/Hickman2021/pngs/"

    # plot 5 samples in a panel  
    images_to_plot = random.sample(annotations_base_path.image_path.unique().tolist(), 5)
    for image in images_to_plot:
        df_to_plot = annotations_base_path[annotations_base_path.image_path == image]
        df_to_plot = read_file(df_to_plot)
        df_to_plot.root_dir = "/orange/ewhite/DeepForest/Hickman2021/pngs/"
        df_to_plot["score"] =1 
        height, width, channels = cv2.imread(df_to_plot.root_dir + df_to_plot.image_path.iloc[0]).shape
        plot_results(df_to_plot, height=height,width=width)
