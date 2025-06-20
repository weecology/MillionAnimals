from millionanimals.datasets.AnimalBoxes import AnimalBoxesDataset
from millionanimals.common.data_loaders import get_train_loader, get_eval_loader

import torch
import pytest
import os
import numpy as np

# Check if running on hipergator
if os.path.exists("/orange"):
    on_hipergator = True
else:
    on_hipergator = False

# Test structure without real annotation data to ensure format is correct
def test_AnimalBoxes_generic(dataset):
    ds = AnimalBoxesDataset(download=False, root_dir=dataset,version="0.0") 
    for metadata, image, targets in ds:
        boxes, labels = targets["y"], targets["labels"]
        assert image.shape == (100, 100, 3)
        assert image.dtype == np.float32
        assert image.min() >= 0.0 and image.max() <= 1.0
        assert boxes.shape == (2, 4)
        assert labels.shape == (2,)
        assert metadata.shape == (2,)
        break

    train_dataset = ds.get_subset("train")
     
    for metadata, image, targets in train_dataset:
        boxes, labels = targets["y"], targets["labels"]
        assert image.shape == (3, 448, 448)
        assert image.dtype == torch.float32
        assert image.min() >= 0.0 and image.max() <= 1.0
        assert torch.is_tensor(boxes)
        assert boxes.shape == (2,4)
        assert len(labels) == 2
        assert metadata.shape == (2,)
        break

# confirm that we can change target name is needed
def test_get_dataset_with_geometry_name(dataset):
    ds = AnimalBoxesDataset(download=False, root_dir=dataset, geometry_name="boxes",version="0.0") 
    train_dataset = ds.get_subset("train")

    for metadata, image, targets in train_dataset:
        boxes, labels = targets["boxes"], targets["labels"]
        break

    # Test the dataloader
    train_loader = get_train_loader('standard', train_dataset, batch_size=2)

    all_y_pred = []
    all_y_true = []
    # Get predictions for the full test set
    for metadata, x, y_true in train_loader:
        labels = torch.zeros(x.shape[0])
        pred_tensor = [[30, 70, 35, 75]]
        scores = torch.stack([torch.tensor(0.54) for x in range(len(pred_tensor))])
        y_pred = [{'boxes': torch.tensor(pred_tensor), 'label': labels, 'scores': scores} for _ in range(x.shape[0])]
        all_y_true.extend(y_true)
        all_y_pred.extend(y_pred)

    # Concat and Evaluate
    eval_results, eval_string = ds.eval(y_pred=all_y_pred,y_true=all_y_true, metadata=train_dataset.metadata_array)

@pytest.mark.parametrize("batch_size", [1, 2])
def test_get_train_dataloader(dataset, batch_size):
    ds = AnimalBoxesDataset(download=False, root_dir=dataset, version="0.0") 
    train_dataset = ds.get_subset("train")
    train_loader = get_train_loader('standard', train_dataset, batch_size=batch_size)
    for metadata, x, targets in train_loader:
        y = targets[0]["y"]
        assert torch.is_tensor(targets[0]["y"])
        assert x.shape == (batch_size, 3, 448, 448)
        assert x.dtype == torch.float32
        assert x.min() >= 0.0 and x.max() <= 1.0
        assert y.shape[1] == 4
        assert len(metadata) == batch_size
        break

def test_get_test_dataloader(dataset):
    ds = AnimalBoxesDataset(download=False, root_dir=dataset,version="0.0") 
    test_dataset = ds.get_subset("test")
    
    for metadata, image, targets in test_dataset:
        boxes, labels = targets["y"], targets["labels"]
        assert image.shape == (3,448, 448)
        assert image.dtype == torch.float32
        assert image.min() >= 0.0 and image.max() <= 1.0
        assert boxes.shape == (2, 4)
        assert labels.shape == (2,)
        assert metadata.shape == (2,)
        break
    
    # Assert that test_dataset[0] == "image3.jpg"
    metadata, image, targets = test_dataset[0]
    assert metadata[1] == 1
    assert ds._filename_id_to_code[int(metadata[0])] == "image3.jpg"

    test_loader = get_eval_loader('standard', test_dataset, batch_size=2)
    for metadata, x, targets in test_loader:
        y = targets[0]["y"]
        assert torch.is_tensor(targets[0]["y"])
        assert x.shape == (2, 3, 448, 448)
        assert x.dtype == torch.float32
        assert x.min() >= 0.0 and x.max() <= 1.0
        assert y.shape[1] == 4
        assert metadata.shape[0] == 2
        break
    
@pytest.mark.parametrize("pred_tensor", [[[134, 156, 313, 336]], [[30, 70, 35, 75],[30, 20, 35, 55]]], ids=["single", "multiple"])
def test_AnimalBoxes_eval(dataset, pred_tensor):
    ds = AnimalBoxesDataset(download=False, root_dir=dataset,version="0.0") 
    test_dataset = ds.get_subset("test")
    test_loader = get_eval_loader('standard', test_dataset, batch_size=2)

    all_y_pred = []
    all_y_true = []
    # Get predictions for the full test set
    for metadata, x, y_true in test_loader:
        labels = torch.zeros(x.shape[0])
        scores = torch.stack([torch.tensor(0.54) for x in range(len(pred_tensor))])
        y_pred = [{'y': torch.tensor(pred_tensor), 'label': labels, 'scores': scores} for _ in range(x.shape[0])]
        all_y_true.extend(y_true)
        all_y_pred.extend(y_pred)

    # Concat and Evaluate
    eval_results, eval_string = ds.eval(y_pred=all_y_pred,y_true=all_y_true, metadata=test_dataset.metadata_array)

    if pred_tensor == [[134, 156, 313, 336]]:
        # One image is 0.5, and in the other one of the boxes is correct. Averaged over 2 images = 0.75
        assert eval_results["accuracy"]["detection_accuracy_avg"] == 0.75

    assert len(eval_results) 
    assert "accuracy" in eval_results.keys()
    assert "recall" in eval_results.keys()

def test_AnimalBoxes_download(tmpdir):
    ds = AnimalBoxesDataset(download=True, root_dir=tmpdir, version="0.0")
    train_dataset = ds.get_subset("train")
     
    for metadata, image, targets in train_dataset:
        boxes = targets["y"]
        assert image.shape == (3, 448, 448)
        assert image.dtype == torch.float32
        assert image.min() >= 0.0 and image.max() <= 1.0
        assert boxes.shape[1] == 4
        assert metadata.shape[0] == 2
        break