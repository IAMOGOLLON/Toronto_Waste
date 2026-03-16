# Analyzing the Spatial Alignment Between Public Waste Bins and Pedestrian Mobility in Urban Toronto

## Project Overview
This group project examines the spatial alignment between public waste bin distribution and indicators of urban mobility within the City of Toronto. The analysis focuses on evaluating whether waste bins are located in areas with higher pedestrian activity and urban demand.

The project integrates spatial and contextual datasets related to:
- public waste bin distribution
- pedestrian mobility patterns
- transit accessibility
- population context

The main objective is to assess whether waste bin placement is spatially aligned with areas of greater pedestrian movement using geospatial analysis techniques in Python.

## Project Scope
The analysis combines multiple spatial and contextual layers, including:
- waste bin locations
- pedestrian network data
- public transit access points
- population and demographic context

All spatial processing, cleaning, validation, integration, and analysis are conducted in Python using GeoPandas, Pandas, NumPy, and Shapely in VS Code and Jupyter Notebooks.

## Repository Structure
```text
TORONTO_WASTE/
├── data/
│   ├── raw/                         # Original source datasets (stored locally, not uploaded to GitHub)
│   │   ├── 49_census_divisions_mof_population_...
│   │   ├── Pedestrian Network Data - 4326.csv
│   │   ├── population_toronto_2024_2025_...
│   │   ├── stops.txt
│   │   ├── street furniture-Litter receptacle data ...
│   │   ├── SWMS_PARK_BIN_WGS84.shp
│   │   ├── SWMS_PARK_BIN_WGS84.dbf
│   │   ├── SWMS_PARK_BIN_WGS84.prj
│   │   ├── SWMS_PARK_BIN_WGS84.shx
│   │   └── related spatial support files
│   │
│   └── clean/                       # Cleaned and integrated spatial outputs (stored locally)
│       ├── grid_250m_master.gpkg
│       ├── grid_250m_waste_bins.gpkg
│       ├── grid_250m_with_pedestrian_and_transit.gpkg
│       ├── grid_250m_with_pedestrian_proxy.gpkg
│       ├── population_context_city_level.csv
│       └── waste_bins_points_clean.gpkg
│
├── notebooks/                       # Jupyter notebooks for QA, cleaning checks, and integration
│   ├── 01_waste_bins_cleaning_checks.ipynb
│   ├── 02_pedestrian_proxy_cleaning_checks.ipynb
│   ├── 03_transit_points_cleaning_checks.ipynb
│   ├── 04_population_context_checks.ipynb
│   ├── 05_analysis_integration.ipynb
│   └── 06_integrate.ipynb
│
├── outputs/                         # Analysis outputs and report-ready working files
│   └── Analysis.ipynb
│
├── src/                             # Core Python scripts for the data pipeline
│   ├── data_cleaning.py
│   ├── data_loader.py
│   ├── feature_engineering.py
│   ├── integrate.py
│   ├── main.py
│   └── paths.py
│
├── .gitignore
├── README.md
└── requirements.txt
```
## Data Management Policy

#GitHub

This repository contains:

project structure

- Python scripts

- Jupyter notebooks

- selected analysis outputs

- documentation

- Local Storage

## Large raw and cleaned datasets are not stored in GitHub due to file size and versioning constraints. These files must be stored locally in the corresponding data/raw/ and data/clean/ folders.

# This includes files such as:

- CSV

- TXT

- GPKG

- SHP, DBF, SHX, PRJ

## other large intermediate spatial outputs

# All team members are expected to:

- place the shared raw datasets into the data/raw/ folder

- generate cleaned and integrated files locally in data/clean/

- run notebooks and scripts locally

- This helps maintain:

- a lightweight repository

- fewer file size issues

- a consistent structure across all team members

## Main Workflow

# The project workflow is organized into the following stages:

- load raw datasets

- clean and standardize each data source

- integrate layers into a common 250 m grid structure

- generate spatial outputs for analysis

- conduct final analytical work in notebooks

# Tools and Technologies

- Python 3.x

- GeoPandas

- Pandas

- NumPy

- Shapely

- Jupyter Notebook

- VS Code

- GitHub

- Power BI

## Notes

This repository is intended for collaborative academic work.
