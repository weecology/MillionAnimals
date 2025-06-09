from millionanimals.datasets.AnimalPolygons import AnimalPolygonsDataset
from millionanimals.datasets.AnimalPoints import AnimalPointsDataset
from millionanimals.datasets.AnimalBoxes import AnimalBoxesDataset
from millionanimals.common.data_loaders import get_train_loader, get_eval_loader

import torch

def test_AnimalPolygons_latest_release(tmpdir):
    print(tmpdir)
    dataset = AnimalPolygonsDataset(download=True, root_dir=tmpdir)
    train_dataset = dataset.get_subset("train")
        
    for metadata, image, targets in train_dataset:
        y = targets["y"]
        labels = targets["labels"]
        assert image.shape == (3, 448, 448)
        assert image.dtype == torch.float32
        assert image.min() >= 0.0 and image.max() <= 1.0
        assert y[0].shape == (448, 448)
        assert metadata.shape[0] == 2
    
    train_loader = get_train_loader('standard', train_dataset, batch_size=2)
    for metadata, x, targets in train_loader:
        len(targets) == 2
        labels = targets[0]["labels"]
        y = targets["y"][0]
        assert x.shape == (2, 3, 448, 448)
        assert x.dtype == torch.float32
        assert x.min() >= 0.0 and x.max() <= 1.0
        assert y[0].shape == (1,448, 448)
        assert len(metadata) == 2
        break

    val_dataset = dataset.get_subset("val")
    val_loader = get_eval_loader('standard', val_dataset, batch_size=2)

    for metadata, x, targets in val_loader:
        len(targets) == 2
        labels = targets[0]["labels"]
        y = targets["y"][0]
        assert x.shape == (2, 3, 448, 448)
        assert x.dtype == torch.float32
        assert x.min() >= 0.0 and x.max() <= 1.0
        assert y[0].shape == (1,448, 448)
        assert len(metadata) == 2
        break

def test_AnimalPoints_latest_release(tmpdir):
    print(tmpdir)
    dataset = AnimalPointsDataset(download=True, root_dir=tmpdir)
    train_dataset = dataset.get_subset("train")
    
    for metadata, image, targets in train_dataset:
        points = targets["y"]
        labels = targets["labels"]
        assert image.shape == (3, 448, 448)
        assert image.dtype == torch.float32
        assert image.min() >= 0.0 and image.max() <= 1.0
        assert points.shape[1] == 2
        assert metadata.shape[0] == 2
    
    train_loader = get_train_loader('standard', train_dataset, batch_size=2)
    for metadata, x, targets in train_loader:
        len(targets) == 2
        points = targets[0]["y"]
        assert x.shape == (2, 3, 448, 448)
        assert x.dtype == torch.float32
        assert x.min() >= 0.0 and x.max() <= 1.0
        assert points.shape[1] == 2
        assert len(metadata) == 2
        break

    val_dataset = dataset.get_subset("val")
    val_loader = get_eval_loader('standard', val_dataset, batch_size=2)

    for metadata, x, targets in val_loader:
        len(targets) == 2
        labels = targets[0]["labels"]
        y = targets["y"][0]
        assert x.shape == (2, 3, 448, 448)
        assert x.dtype == torch.float32
        assert x.min() >= 0.0 and x.max() <= 1.0
        assert y[0].shape == (1,448, 448)
        assert len(metadata) == 2
        break

def test_AnimalBoxes_latest_release(tmpdir):
    print(tmpdir)
    dataset = AnimalBoxesDataset(download=True, root_dir=tmpdir)
    train_dataset = dataset.get_subset("train")
    
    for metadata, image, targets in train_dataset:
        boxes = targets["y"]
        labels = targets["labels"]
        assert image.shape == (3, 448, 448)
        assert image.dtype == torch.float32
        assert image.min() >= 0.0 and image.max() <= 1.0
        assert boxes.shape[1] == 4
        assert metadata.shape[0] == 2
    
    train_loader = get_train_loader('standard', train_dataset, batch_size=2)
    for metadata, x, targets in train_loader:
        len(targets) == 2
        boxes = targets[0]["y"]
        assert x.shape == (2, 3, 448, 448)
        assert x.dtype == torch.float32
        assert x.min() >= 0.0 and x.max() <= 1.0
        assert boxes.shape[1] == 4
        assert len(metadata) == 2
        break

    val_dataset = dataset.get_subset("val")
    val_loader = get_eval_loader('standard', val_dataset, batch_size=2)
    for metadata, x, targets in val_loader:
        len(targets) == 2
        boxes = targets[0]["y"]
        assert x.shape == (2, 3, 448, 448)
        assert x.dtype == torch.float32
        assert x.min() >= 0.0 and x.max() <= 1.0
        assert boxes.shape[1] == 4
        assert len(metadata) == 2
        break
