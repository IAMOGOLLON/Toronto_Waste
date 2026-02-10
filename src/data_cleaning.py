import geopandas as gpd
from pathlib import Path
import pandas as pd
import numpy as np
from shapely.geometry import box
from src.paths import RAW_DIR

CRS_PROJECTED = "EPSG:26917"

def clean_waste_bins(
    park_bins: gpd.GeoDataFrame,
    street_bins: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:

    park_bins = park_bins.to_crs(CRS_PROJECTED)
    street_bins = street_bins.to_crs(CRS_PROJECTED)

    park_bins["source"] = "park_assets"
    street_bins["source"] = "street_furniture"

    waste_bins = gpd.GeoDataFrame(
        pd.concat([park_bins, street_bins], ignore_index=True),
        crs=CRS_PROJECTED
    )

    waste_bins["bin_uid"] = np.where(
        waste_bins["source"] == "park_assets",
        "park_" + waste_bins["RID"].astype(str),
        "street_" + waste_bins["OBJECTID"].astype(str)
    )

    return waste_bins

CRS_PROJECTED = "EPSG:26917"


def clean_pedestrian_network(ped_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Standardizes pedestrian network to EPSG:26917 and ensures:
    - a stable segment id column exists (segment_uid)
    - a length column in meters exists (ped_length_m)
    """
    ped = ped_gdf.copy()

    ped = ped.to_crs(CRS_PROJECTED)

    if "_id" in ped.columns:
        ped["segment_uid"] = ped["_id"].astype(str)
    else:
        ped["segment_uid"] = ped.index.astype(str)

    if "LENGTH" in ped.columns:
        ped["ped_length_m"] = ped["LENGTH"].astype(float)
    else:
        ped["ped_length_m"] = ped.geometry.length.astype(float)

    keep_cols = ["segment_uid", "ped_length_m", "geometry"]
    ped = ped[keep_cols]

    return ped

CRS_PROJECTED = "EPSG:26917"


def clean_transit_stops(stops_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Reprojects transit stops to EPSG:26917 and standardizes columns.
    """
    stops = stops_gdf.copy().to_crs(CRS_PROJECTED)

    # Stable id
    if "stop_id" in stops.columns:
        stops["stop_uid"] = stops["stop_id"].astype(str)
    else:
        stops["stop_uid"] = stops.index.astype(str)

    keep = ["stop_uid", "geometry"]
    return stops[keep]

def clean_population_context(pop_df: pd.DataFrame) -> pd.DataFrame:
    """
    Minimal cleaning/validation for city-level population context.
    Keeps it non-spatial (no grid allocation).
    """
    df = pop_df.copy()

    # Strip column names
    df.columns = [c.strip() for c in df.columns]

    # If your age-group file has this column, keep only 2024–2025
    if "YEAR (JULY 1)" in df.columns:
        df["YEAR (JULY 1)"] = pd.to_numeric(df["YEAR (JULY 1)"], errors="coerce")
        df = df[df["YEAR (JULY 1)"].isin([2024, 2025])].copy()

    return df
