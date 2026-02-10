import geopandas as gpd
import json
import pandas as pd
import numpy as np

from shapely.geometry import box
from shapely.geometry import shape
from src.paths import RAW_DIR

def load_park_bins() -> gpd.GeoDataFrame:
    path = RAW_DIR / "SWMS_PARK_BIN_WGS84.shp"
    return gpd.read_file(path)


def load_street_bins() -> gpd.GeoDataFrame:
    path = RAW_DIR / "Street furniture-Litter receptacle data - 4326.geojson"
    return gpd.read_file(path)


def load_pedestrian_network_df() -> pd.DataFrame:
    """
    Loads the Pedestrian Network file from data/raw as a DataFrame.
    Supports either CSV or XLSX (whichever exists).
    """
    csv_path = RAW_DIR / "Pedestrian Network Data - 4326.csv"
    xlsx_path = RAW_DIR / "Pedestrian Network Data - 4326.xlsx"

    if csv_path.exists():
        return pd.read_csv(csv_path)

    if xlsx_path.exists():
        # Explicit engine to avoid pandas guessing error
        return pd.read_excel(xlsx_path, engine="openpyxl")

    raise FileNotFoundError(
        "Pedestrian Network file not found. Expected one of:\n"
        f"- {csv_path}\n"
        f"- {xlsx_path}"
    )

def load_pedestrian_network_gdf() -> gpd.GeoDataFrame:
    """
    Converts the Pedestrian Network DataFrame into a GeoDataFrame (EPSG:4326).
    Expects a 'geometry' column containing GeoJSON strings.
    """
    df = load_pedestrian_network_df()

    if "geometry" not in df.columns:
        raise KeyError("Column 'geometry' not found in pedestrian dataset.")

    # geometry column is expected to be GeoJSON text -> shapely geometry
    df["geometry"] = df["geometry"].apply(lambda x: shape(json.loads(x)))

    gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")
    return gdf

def load_transit_stops_df() -> pd.DataFrame:
    """
    Loads GTFS stops from data/raw/stops.txt
    """
    stops_path = RAW_DIR / "stops.txt"
    if not stops_path.exists():
        raise FileNotFoundError(f"stops.txt not found at: {stops_path}")

    return pd.read_csv(stops_path)


def load_transit_stops_gdf() -> gpd.GeoDataFrame:
    """
    Converts stops DataFrame into a GeoDataFrame in EPSG:4326.
    Requires stop_lat and stop_lon columns.
    """
    df = load_transit_stops_df()

    required = {"stop_id", "stop_lat", "stop_lon"}
    missing = required - set(df.columns)
    if missing:
        raise KeyError(f"Missing required columns in stops.txt: {missing}")

    df = df.dropna(subset=["stop_lat", "stop_lon"]).copy()

    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df["stop_lon"], df["stop_lat"]),
        crs="EPSG:4326"
    )
    return gdf

def load_population_context_df() -> pd.DataFrame:
    """
    Loads city-level population context (no geometry).
    """
    # Option 1: if you already created a CSV with age groups
    csv1 = RAW_DIR / "population_toronto_2024_2025_age_groups.csv"

    # Option 2: if you only have the original Excel in raw (your file listing shows .xlsx)
    xlsx = RAW_DIR / "49_census_divisions_mof_population_projections_2024-2051.xlsx"

    if csv1.exists():
        return pd.read_csv(csv1)

    if xlsx.exists():
        # keep it simple: you can later select the correct sheet/columns
        return pd.read_excel(xlsx, engine="openpyxl")

    raise FileNotFoundError(
        "Population context file not found. Expected one of:\n"
        f"- {csv1}\n"
        f"- {xlsx}"
    )

def load_population_context_df() -> pd.DataFrame:
    """
    Loads city-level population context (non-spatial).
    Priority:
    1) If a prepared CSV exists in data/raw, use it.
    2) Otherwise, load the original Excel file in data/raw.
    """
    csv_path = RAW_DIR / "population_toronto_2024_2025_age_groups.csv"
    xlsx_path = RAW_DIR / "49_census_divisions_mof_population_projections_2024-2051.xlsx"

    if csv_path.exists():
        return pd.read_csv(csv_path)

    if xlsx_path.exists():
        return pd.read_excel(xlsx_path, engine="openpyxl")

    raise FileNotFoundError(
        "Population context file not found. Expected one of:\n"
        f"- {csv_path}\n"
        f"- {xlsx_path}"
    )