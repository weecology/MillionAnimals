import pandas as pd
import os
import shutil
import geopandas as gpd
import zipfile
from deepforest.visualize import plot_results
from deepforest.utilities import read_file
import cv2
import rasterio
import glob

def remove_alpha_channel(datasets):
    """Remove alpha channels from images in the dataset."""
    for source in datasets["source"].unique():
        source_images = datasets[datasets["source"] == source]["filename"].unique()
        for image in source_images:
            with rasterio.open(image) as img_src:
                if img_src.count == 4:  # Check if the image has 4 channels
                    data = img_src.read([1, 2, 3])  # Read only the first three channels
                    profile = img_src.profile
                    profile.update(count=3)  # Update profile to reflect 3 channels
                    new_image_path = os.path.splitext(image)[0] + "_no_alpha.tif"
                    with rasterio.open(new_image_path, 'w', **profile) as img_dst:
                        img_dst.write(data)
                    datasets.loc[datasets["filename"] == image, "filename"] = new_image_path


def combine_datasets(dataset_paths, debug=False):
    """Combine multiple datasets into a single DataFrame."""
    datasets = []
    for dataset in dataset_paths:
        datasets.append(pd.read_csv(dataset))
    
    df = pd.concat(datasets)
    df = df.rename(columns={"image_path":"filename"})
    if debug:
        df = df.groupby("source").head()

    return df


def split_dataset(datasets, split_column="filename", frac=0.8):
    """Split the dataset into training and testing sets."""
    train_images = datasets[split_column].drop_duplicates().sample(frac=frac)
    datasets.loc[datasets[split_column].isin(train_images), "split"] = "train"
    datasets.loc[~datasets[split_column].isin(train_images), "split"] = "test"
    
    return datasets


def process_geometry_columns(datasets, geom_type):
    """Process geometry columns based on the dataset type."""
    if geom_type == "box":
        datasets[["xmin", "ymin", "xmax", "ymax"]] = gpd.GeoSeries.from_wkt(datasets["geometry"]).bounds
    elif geom_type == "point":
        datasets["x"] = gpd.GeoSeries.from_wkt(datasets["geometry"]).centroid.x
        datasets["y"] = gpd.GeoSeries.from_wkt(datasets["geometry"]).centroid.y
    elif geom_type == "polygon":
        datasets["polygon"] = gpd.GeoDataFrame(datasets.geometry).to_wkt()
        # Remove multipolygons
        datasets = datasets[datasets["geometry"].apply(lambda x: gpd.GeoSeries.from_wkt([x]).geom_type[0] != "MultiPolygon")]
    return datasets


def create_directories(base_dir, dataset_type):
    """Create directories for the dataset."""
    os.makedirs(f"{base_dir}{dataset_type}_{version}/images", exist_ok=True)
    os.makedirs(f"{base_dir}Mini{dataset_type}_{version}/images", exist_ok=True)


def copy_images(datasets, base_dir, dataset_type):
    """Copy images to the destination folder."""
    for image in datasets["filename"].unique():
        destination = f"{base_dir}{dataset_type}_{version}/images/"
        if not os.path.exists(os.path.join(destination, os.path.basename(image))):
            shutil.copy(image, destination)

def create_mini_datasets(datasets, base_dir, dataset_type, version):
    """Create mini datasets for debugging and generate visualizations."""
    mini_datasets = datasets.groupby("source").first().reset_index(drop=True)
    mini_filenames = mini_datasets["filename"].tolist()
    mini_annotations = datasets[datasets["filename"].isin(mini_filenames)]
    mini_annotations.to_csv(f"{base_dir}Mini{dataset_type}_{version}/official.csv", index=False)
    
    # Copy images for mini datasets
    for image in mini_filenames:
        destination = f"{base_dir}Mini{dataset_type}_{version}/images/"
        shutil.copy(f"{base_dir}{dataset_type}_{version}/images/" + image, destination)

    # Generate visualizations for each source
    for source, group in mini_annotations.groupby("source"):
        group["image_path"] = group["filename"]
        group = read_file(group, root_dir=f"{base_dir}Mini{dataset_type}_{version}/images/")
        group.root_dir = f"{base_dir}Mini{dataset_type}_{version}/images/"
        
        # Remove spaces in source name
        source = source.replace(" ", "_")
        
        # Handle polygons specifically to include image dimensions
        if dataset_type == "AnimalPolygons":
            height, width, channels = cv2.imread(f"{base_dir}Mini{dataset_type}_{version}/images/" + group.image_path.iloc[0]).shape
            plot_results(group, savedir="/home/b.weinstein/MillionAnimals/docs/public/", basename=source, height=height, width=width)
        else:
            plot_results(group, savedir="/home/b.weinstein/MillionAnimals/docs/public/", basename=source)

def create_release_files(base_dir, dataset_type):
    """Create release files for the dataset."""
    with open(f"{base_dir}{dataset_type}_{version}/RELEASE_{version}.txt", "w") as outfile:
        outfile.write(f"Version: {version}")

def zip_directory(folder_path, zip_path):
    """Zip the contents of a directory."""
    # Remove the existing zip file if it exists
    if os.path.exists(zip_path):
        os.remove(zip_path)
    # Create a new zip file
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)

def official_split(AnimalPolygons_datasets, AnimalPoints_datasets, AnimalBoxes_datasets, base_dir, version):
    """Perform official split and save the results."""
    # Randomly split datasets into train and test (80/20 split)
    if not AnimalPolygons_datasets.empty:
        AnimalPolygons_datasets = split_dataset(AnimalPolygons_datasets, split_column="filename", frac=0.8)
        AnimalPolygons_datasets.to_csv(f"{base_dir}AnimalPolygons_{version}/official.csv", index=False)
        print(f"Official split saved: AnimalPolygons_{version}/official.csv")
    
    if not AnimalPoints_datasets.empty:
        AnimalPoints_datasets = split_dataset(AnimalPoints_datasets, split_column="filename", frac=0.8)
        AnimalPoints_datasets.to_csv(f"{base_dir}AnimalPoints_{version}/official.csv", index=False)
        print(f"Official split saved: AnimalPoints_{version}/official.csv")
    
    if not AnimalBoxes_datasets.empty:
        AnimalBoxes_datasets = split_dataset(AnimalBoxes_datasets, split_column="filename", frac=0.8)
        AnimalBoxes_datasets.to_csv(f"{base_dir}AnimalBoxes_{version}/official.csv", index=False)
        print(f"Official split saved: AnimalBoxes_{version}/official.csv")

    print("Official splits completed.")

def cross_geometry_split(AnimalPolygons_datasets, AnimalPoints_datasets, AnimalBoxes_datasets, base_dir, version):
    """Perform cross-geometry split and save the results."""
    # Assign all polygons to train, points to test, and boxes to test
    if not AnimalPolygons_datasets.empty:
        AnimalPolygons_datasets["split"] = "train"
        AnimalPolygons_datasets.to_csv(f"{base_dir}AnimalPolygons_{version}/crossgeometry.csv", index=False)
        print(f"Cross-geometry split saved: AnimalPolygons_{version}/crossgeometry.csv")
    
    if not AnimalPoints_datasets.empty:
        AnimalPoints_datasets["split"] = "test"
        AnimalPoints_datasets.to_csv(f"{base_dir}AnimalPoints_{version}/crossgeometry.csv", index=False)
        print(f"Cross-geometry split saved: AnimalPoints_{version}/crossgeometry.csv")
    
    if not AnimalBoxes_datasets.empty:
        AnimalBoxes_datasets["split"] = "test"
        AnimalBoxes_datasets.to_csv(f"{base_dir}AnimalBoxes_{version}/crossgeometry.csv", index=False)
        print(f"Cross-geometry split saved: AnimalBoxes_{version}/crossgeometry.csv")

    print("Cross-geometry splits completed.")

# Zero-shot split
def zero_shot_split(AnimalPolygons_datasets, AnimalPoints_datasets, AnimalBoxes_datasets, base_dir, version):
    """Perform zero-shot split and save the results."""
    # Define test and train sources - Update these based on your animal datasets
    
    # For polygons - specify which sources should be held out for testing
    test_sources_polygons = []  # e.g., ["Wildlife Survey 2024", "Arctic Animals 2023"]
    train_sources_polygons = [x for x in AnimalPolygons_datasets.source.unique() if x not in test_sources_polygons] if not AnimalPolygons_datasets.empty else []

    # For points - specify which sources should be held out for testing
    test_sources_points = []  # e.g., ["Marine Mammals 2024"]
    train_sources_points = [x for x in AnimalPoints_datasets.source.unique() if x not in test_sources_points] if not AnimalPoints_datasets.empty else []

    # For boxes - specify which sources should be held out for testing
    test_sources_boxes = []  # e.g., ["Savanna Wildlife 2023"]
    train_sources_boxes = [x for x in AnimalBoxes_datasets.source.unique() if x not in test_sources_boxes] if not AnimalBoxes_datasets.empty else []

    # Assign splits for polygons
    if not AnimalPolygons_datasets.empty:
        AnimalPolygons_datasets.loc[AnimalPolygons_datasets.source.isin(train_sources_polygons), "split"] = "train"
        AnimalPolygons_datasets.loc[AnimalPolygons_datasets.source.isin(test_sources_polygons), "split"] = "test"
        AnimalPolygons_datasets.to_csv(f"{base_dir}AnimalPolygons_{version}/zeroshot.csv", index=False)
        print(f"Zero-shot split saved: AnimalPolygons_{version}/zeroshot.csv")

    # Assign splits for points
    if not AnimalPoints_datasets.empty:
        AnimalPoints_datasets.loc[AnimalPoints_datasets.source.isin(train_sources_points), "split"] = "train"
        AnimalPoints_datasets.loc[AnimalPoints_datasets.source.isin(test_sources_points), "split"] = "test"
        AnimalPoints_datasets.to_csv(f"{base_dir}AnimalPoints_{version}/zeroshot.csv", index=False)
        print(f"Zero-shot split saved: AnimalPoints_{version}/zeroshot.csv")

    # Assign splits for boxes
    if not AnimalBoxes_datasets.empty:
        AnimalBoxes_datasets.loc[AnimalBoxes_datasets.source.isin(train_sources_boxes), "split"] = "train"
        AnimalBoxes_datasets.loc[AnimalBoxes_datasets.source.isin(test_sources_boxes), "split"] = "test"
        AnimalBoxes_datasets.to_csv(f"{base_dir}AnimalBoxes_{version}/zeroshot.csv", index=False)
        print(f"Zero-shot split saved: AnimalBoxes_{version}/zeroshot.csv")

    print("Zero-shot splits completed.")

def check_for_updated_annotations(dataset, geometry):
    updated_annotations = [pd.read_csv(x) for x in glob.glob(f"data_prep/annotations/*{geometry}*.csv")]
    updated_annotations = pd.concat(updated_annotations)

    dataset["basename"] = dataset["filename"].apply(lambda x: os.path.basename(x))

    # images to remove
    images_to_remove = updated_annotations[updated_annotations.remove =="Remove image from benchmark"].image_path.unique()
    dataset = dataset[~dataset.basename.isin(images_to_remove)]

    updated_annotations = updated_annotations[~(updated_annotations.label.isnull())]

    # Check the filenames
    updated_filenames = updated_annotations["image_path"].unique()
    dataset_filenames = dataset["basename"].unique()

    # Check if any updated filenames are in the dataset
    for filename in updated_filenames:
        if filename in dataset_filenames:
            print(f"Updated annotation found for {filename}")
            
            # Update the dataset with the new annotation
            original_annotations = dataset[dataset["basename"] == filename]
            updated_image_annotations = updated_annotations[updated_annotations["image_path"] == filename].copy(deep=True)
            updated_image_annotations["source"] = original_annotations["source"].values[0]
            updated_image_annotations = read_file(updated_image_annotations, root_dir=os.path.dirname(dataset["filename"].values[0]))
            
            root_dir = os.path.dirname(dataset["filename"].values[0])
            updated_image_annotations["filename"] = updated_image_annotations["image_path"].apply(lambda x: os.path.join(x,root_dir))
            
            # Remove the original annotations
            dataset = dataset[dataset["basename"] != filename]

            # Append the updated annotations
            dataset = pd.concat([dataset, updated_image_annotations], ignore_index=True)
        else:
            continue

def run(version, base_dir, debug=False):
    # These lists will be populated with animal dataset paths from Dropbox
    AnimalBoxes = [
        # Example: "/path/to/wildlife_drones/annotations.csv",
        # Add your animal bounding box datasets here
    ]

    AnimalPoints = [
        # Example: "/path/to/marine_mammals/annotations.csv",
        # Add your animal point datasets here
    ]

    AnimalPolygons = [
        # Example: "/path/to/livestock_monitoring/annotations.csv",
        # Add your animal polygon datasets here
    ]

    # Check if any datasets are provided
    if not any([AnimalBoxes, AnimalPoints, AnimalPolygons]):
        print("No datasets provided. Please add animal dataset paths to the lists above.")
        return

    # Combine datasets
    AnimalBoxes_datasets = combine_datasets(AnimalBoxes, debug=debug) if AnimalBoxes else pd.DataFrame()
    AnimalPoints_datasets = combine_datasets(AnimalPoints, debug=debug) if AnimalPoints else pd.DataFrame()
    AnimalPolygons_datasets = combine_datasets(AnimalPolygons, debug=debug) if AnimalPolygons else pd.DataFrame()

    # Only process datasets that have data
    if not AnimalBoxes_datasets.empty:
        # Remove rows where xmin equals xmax
        AnimalBoxes_datasets = AnimalBoxes_datasets[AnimalBoxes_datasets["xmin"] != AnimalBoxes_datasets["xmax"]]
        AnimalBoxes_datasets = AnimalBoxes_datasets[AnimalBoxes_datasets["ymin"] != AnimalBoxes_datasets["ymax"]]
        
        # Remove alpha channels
        remove_alpha_channel(AnimalBoxes_datasets)
        
        # Check for updated annotations
        check_for_updated_annotations(AnimalBoxes_datasets, "Boxes")
        
        # Split datasets
        AnimalBoxes_datasets = split_dataset(AnimalBoxes_datasets)
        
        # Process geometry columns
        AnimalBoxes_datasets = process_geometry_columns(AnimalBoxes_datasets, "box")
        
        # Create directories
        create_directories(base_dir, "AnimalBoxes")
        
        # Copy images
        copy_images(AnimalBoxes_datasets, base_dir, "AnimalBoxes")
        
        # change filenames to relative path
        AnimalBoxes_datasets["filename"] = AnimalBoxes_datasets["filename"].apply(os.path.basename)
        
        # Create mini datasets
        create_mini_datasets(AnimalBoxes_datasets, base_dir, "AnimalBoxes", version)

    if not AnimalPoints_datasets.empty:
        # Remove alpha channels
        remove_alpha_channel(AnimalPoints_datasets)
        
        # Check for updated annotations
        check_for_updated_annotations(AnimalPoints_datasets, "Points")
        
        # Split datasets
        AnimalPoints_datasets = split_dataset(AnimalPoints_datasets)
        
        # Process geometry columns
        AnimalPoints_datasets = process_geometry_columns(AnimalPoints_datasets, "point")
        
        # Create directories
        create_directories(base_dir, "AnimalPoints")
        
        # Copy images
        copy_images(AnimalPoints_datasets, base_dir, "AnimalPoints")
        
        # change filenames to relative path
        AnimalPoints_datasets["filename"] = AnimalPoints_datasets["filename"].apply(os.path.basename)
        
        # Create mini datasets
        create_mini_datasets(AnimalPoints_datasets, base_dir, "AnimalPoints", version)

    if not AnimalPolygons_datasets.empty:
        # Remove alpha channels
        remove_alpha_channel(AnimalPolygons_datasets)
        
        # Check for updated annotations
        check_for_updated_annotations(AnimalPolygons_datasets, "Polygons")
        
        # Split datasets
        AnimalPolygons_datasets = split_dataset(AnimalPolygons_datasets)
        
        # Process geometry columns
        AnimalPolygons_datasets = process_geometry_columns(AnimalPolygons_datasets, "polygon")
        
        # Create directories
        create_directories(base_dir, "AnimalPolygons")
        
        # Copy images
        copy_images(AnimalPolygons_datasets, base_dir, "AnimalPolygons")
        
        # change filenames to relative path
        AnimalPolygons_datasets["filename"] = AnimalPolygons_datasets["filename"].apply(os.path.basename)
        
        # Create mini datasets
        create_mini_datasets(AnimalPolygons_datasets, base_dir, "AnimalPolygons", version)

    # Only perform splits and create release files if we have data
    if any([not df.empty for df in [AnimalPolygons_datasets, AnimalPoints_datasets, AnimalBoxes_datasets]]):
        # Perform splits
        zero_shot_split(AnimalPolygons_datasets, AnimalPoints_datasets, AnimalBoxes_datasets, base_dir, version)
        official_split(AnimalPolygons_datasets, AnimalPoints_datasets, AnimalBoxes_datasets, base_dir, version)
        cross_geometry_split(AnimalPolygons_datasets, AnimalPoints_datasets, AnimalBoxes_datasets, base_dir, version)
        
        # Create release files
        if not AnimalBoxes_datasets.empty:
            create_release_files(base_dir, "AnimalBoxes")
            zip_directory(f"{base_dir}AnimalBoxes_{version}", f"{base_dir}AnimalBoxes_{version}.zip")
            zip_directory(f"{base_dir}MiniAnimalBoxes_{version}", f"{base_dir}MiniAnimalBoxes_{version}.zip")
            
        if not AnimalPoints_datasets.empty:
            create_release_files(base_dir, "AnimalPoints")
            zip_directory(f"{base_dir}AnimalPoints_{version}", f"{base_dir}AnimalPoints_{version}.zip")
            zip_directory(f"{base_dir}MiniAnimalPoints_{version}", f"{base_dir}MiniAnimalPoints_{version}.zip")
            
        if not AnimalPolygons_datasets.empty:
            create_release_files(base_dir, "AnimalPolygons")
            zip_directory(f"{base_dir}AnimalPolygons_{version}", f"{base_dir}AnimalPolygons_{version}.zip")
            zip_directory(f"{base_dir}MiniAnimalPolygons_{version}", f"{base_dir}MiniAnimalPolygons_{version}.zip")


if __name__ == "__main__":
    version = "v0.4"
    base_dir = "/orange/ewhite/web/public/"
    debug = False
    run(version, base_dir, debug)