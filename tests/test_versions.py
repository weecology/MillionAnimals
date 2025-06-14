import pytest
import os
from millionanimals.datasets import AnimalPolygons, AnimalBoxes, AnimalPoints
import urllib.request

DATASET_CLASSES = [AnimalPolygons.AnimalPolygonsDataset, AnimalBoxes.AnimalBoxesDataset, AnimalPoints.AnimalPointsDataset]

@pytest.mark.parametrize("dataset_class", DATASET_CLASSES)
def test_dataset_url_exists(dataset_class, tmpdir):
    """Test that dataset URLs exist but don't actually download"""
    versions = dataset_class._versions_dict
    for version in versions:
        url = versions[version]['download_url']
        fpath = os.path.join(tmpdir, "test_data", "raw", os.path.basename(url))
        try:
            with urllib.request.urlopen(url) as response:
                assert response.status == 200
        except urllib.error.URLError as e:
            pytest.fail(f"URL {url} is not accessible: {e}")
            


        
