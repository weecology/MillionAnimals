"""Module for retrieving MillionAnimals dataset instances."""
from typing import Optional
import millionanimals


def get_dataset(dataset: str,
                version: Optional[str] = None,
                unlabeled: bool = False,
                **dataset_kwargs):
    """Brief description of the function.

    Args:
        dataset: Description of dataset.
        version: Description of version.
        unlabeled: Description of unlabeled.
    """
    if version is not None:
        version = str(version)
    if dataset not in millionanimals.supported_datasets:
        raise ValueError(
            f'Dataset {dataset} not recognized. Must be one of {millionanimals.supported_datasets}.'
        )
    if unlabeled and dataset not in millionanimals.unlabeled_datasets:
        raise ValueError(
            f'Unlabeled data not available for {dataset}. Must be one of {millionanimals.unlabeled_datasets}.'
        )
    dataset_classes = {
        'AnimalPoints': {
            'labeled':
                'millionanimals.datasets.AnimalPoints.AnimalPointsDataset',
            'unlabeled':
                'millionanimals.datasets.unlabeled.AnimalPointsUnlabeled.AnimalPoints_Unlabeled_Dataset'
        },
        'AnimalPolygons': {
            'labeled':
                'millionanimals.datasets.AnimalPolygons.AnimalPolygonsDataset',
            'unlabeled':
                'millionanimals.datasets.unlabeled.AnimalPolygonsUnlabeled.AnimalPolygons_Unlabeled_Dataset'
        },
        'AnimalBoxes': {
            'labeled':
                'millionanimals.datasets.AnimalBoxes.AnimalBoxesDataset',
            'unlabeled':
                'millionanimals.datasets.unlabeled.AnimalBoxesUnlabeled.AnimalBoxes_Unlabeled_Dataset'
        }
    }
    if dataset in dataset_classes:
        module_path = dataset_classes[dataset][
            'unlabeled' if unlabeled else 'labeled']
        module_name, class_name = module_path.rsplit('.', 1)
        module = __import__(module_name, fromlist=[class_name])
        dataset_class = getattr(module, class_name)
        return dataset_class(version=version, **dataset_kwargs)
    raise ValueError(f'Dataset {dataset} is not supported.')
