[![Github Actions](https://github.com/weecology/MillionAnimals/actions/workflows/python-package.yml/badge.svg)](https://github.com/weecology/MillionAnimals/actions/workflows/python-package.yml)
[![Documentation Status](https://readthedocs.org/projects/millionanimals/badge/?version=latest)](https://millionanimals.readthedocs.io/en/latest/?badge=latest)
[![Version](https://img.shields.io/pypi/v/MillionAnimals.svg)](https://pypi.python.org/pypi/MillionAnimals)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/MillionAnimals)](https://pypi.python.org/pypi/MillionAnimals)

# Overview

The MillionAnimals benchmark is designed to provide *open*, *reproducible* and *rigorous* evaluation of animal detection algorithms from aerial imagery. This repo is the python package for rapid data sharing and evaluation.

The MillionAnimals project is an adaptation of the [MillionTrees](https://github.com/weecology/MillionTrees) benchmark, focusing on animal detection instead of tree detection.

# Current status

We are in the process of releasing public data, these are datasets that have previously been published and have a DOI. We will follow up this release, likely with a 1.0 tag, of the previously unpublished parts of the dataset along with a scientific manuscript.

We are actively collecting datasets for inclusion in the benchmark. See our [dataset collection spreadsheet](https://docs.google.com/spreadsheets/d/12D3BnlE1car_CzngrwoPG7uySKoaKweYkneEBkgrRKw/edit?usp=sharing) for current datasets under consideration.

# Dataloaders

Currently available dataloaders (numbers to be updated as datasets are added):
- AnimalBoxes: Bounding box annotations of animals from aerial imagery
- AnimalPolygons: Precise polygon annotations of animals
- AnimalPoints: Point locations marking animal positions

## Why MillionAnimals?

There has been a tremendous number of animal detection benchmarks, but a lack of progress towards a single algorithm that can be used globally across acquisition sensors, habitat types and annotation geometry. Our view is that the hundreds of animal detection algorithms for RGB data published in the last 10 years are all data starved. There are many good models, but they can only be so useful with the small datasets any research team can collect. The result is years of effort in model development, but ultimately a lacking solution for a large audience. The MillionAnimals dataset seeks to collect a million annotations across point, polygon and box geometries at a global scale, covering diverse species and habitats.

## Installation

```
pip install MillionAnimals
```

### Dev Requirements

To build from the GitHub source and install the required dependencies, follow these instructions:

1. Clone the GitHub repository:
    ```
    git clone https://github.com/weecology/MillionAnimals.git
    ```

2. Change to the repository directory:
    ```
    cd MillionAnimals
    ```

3. Install the required dependencies using pip:
    ```
    pip install -r requirements.txt
    ```

4. (Optional) Build and install the package:
    ```
    python setup.py install
    ```

Once the installation is complete, you can use the MillionAnimals package in your Python projects.

# Datasets

Datasets are documented on ReadTheDocs with sample images overlayed with annotations.
https://millionanimals.idanimals.org/en/latest/datasets.html

# Citing MillionAnimals

(Citation information will be added upon publication)

## Acknowledgements
The design of the MillionAnimals benchmark was inspired by the [WILDS benchmark](https://github.com/p-lambda/wilds), and we are grateful to their work, as well as Sara Beery for suggesting the use of this template. This project is adapted from the [MillionTrees](https://github.com/weecology/MillionTrees) benchmark.
