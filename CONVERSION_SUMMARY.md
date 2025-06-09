# MillionTrees to MillionAnimals Conversion Summary

This document summarizes the conversion of the MillionTrees project to MillionAnimals, focusing on animal detection instead of tree detection from aerial imagery.

## Repository Changes

1. **Repository Structure**
   - Cloned from: https://github.com/weecology/MillionTrees
   - New repository: MillionAnimals

2. **Directory Renaming**
   - `src/milliontrees/` → `src/millionanimals/`

3. **File Renaming**
   - Dataset files:
     - `TreeBoxes.py` → `AnimalBoxes.py`
     - `TreePoints.py` → `AnimalPoints.py`
     - `TreePolygons.py` → `AnimalPolygons.py`
     - `milliontrees_dataset.py` → `millionanimals_dataset.py`
   - Test files:
     - `test_milliontrees.py` → `test_millionanimals.py`
     - `test_TreeBoxes.py` → `test_AnimalBoxes.py`
     - `test_TreePoints.py` → `test_AnimalPoints.py`
     - `test_TreePolygons.py` → `test_AnimalPolygons.py`
   - Documentation files:
     - `milliontrees*.rst` → `millionanimals*.rst`

4. **Content Updates**
   - Updated 82 files with text replacements
   - Changed all references from:
     - `MillionTrees` → `MillionAnimals`
     - `milliontrees` → `millionanimals`
     - `TreeBoxes` → `AnimalBoxes`
     - `TreePoints` → `AnimalPoints`
     - `TreePolygons` → `AnimalPolygons`
     - Tree-specific terminology → Animal-specific terminology

5. **Documentation Updates**
   - Updated `README.md` to reflect animal detection focus
   - Updated `docs/index.rst` with wildlife monitoring context
   - Rewritten `docs/datasets.md` with placeholder animal datasets
   - Updated domain from `milliontrees.idtrees.org` to `millionanimals.idanimals.org`

6. **Configuration Updates**
   - Updated `pyproject.toml` package name and description
   - Updated all import statements throughout the codebase
   - Updated URLs to point to the new repository

## Key Features Preserved

- Benchmark structure with three dataset types (Boxes, Points, Polygons)
- Data loader functionality
- Evaluation metrics
- Split schemes (official, crossgeometry, zeroshot)
- Documentation structure

## Next Steps

1. **Dataset Collection**: Use the [dataset collection spreadsheet](https://docs.google.com/spreadsheets/d/12D3BnlE1car_CzngrwoPG7uySKoaKweYkneEBkgrRKw/edit?usp=sharing) to track and integrate animal detection datasets

2. **Repository Setup**:
   - Create new GitHub repository at https://github.com/weecology/MillionAnimals
   - Update GitHub Actions workflows
   - Set up ReadTheDocs for millionanimals.readthedocs.io
   - Configure PyPI package publishing

3. **Dataset Integration**:
   - Process and integrate datasets from the collection spreadsheet
   - Update dataset documentation with real animal detection examples
   - Generate sample images with annotations

4. **Testing**:
   - Run all tests to ensure functionality is preserved
   - Update test data to use animal examples
   - Validate data loaders with new datasets

## Acknowledgments

This project is adapted from the MillionTrees benchmark (https://github.com/weecology/MillionTrees), maintaining the same architecture while focusing on animal detection applications.