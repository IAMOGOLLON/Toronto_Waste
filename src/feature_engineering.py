import geopandas as gpd
from pathlib import Path
import pandas as pd
import numpy as np
from shapely.geometry import box
from src.paths import RAW_DIR

CRS_PROJECTED = "EPSG:26917"

def create_grid(
    gdf: gpd.GeoDataFrame,
    cell_size: int = 250,
    buffer: int = 2000
) -> gpd.GeoDataFrame:

    minx, miny, maxx, maxy = gdf.total_bounds
    minx -= buffer
    miny -= buffer
    maxx += buffer
    maxy += buffer

    xs = np.arange(minx, maxx, cell_size)
    ys = np.arange(miny, maxy, cell_size)

    grid_polys = []
    grid_ids = []
    gid = 0

    for x in xs:
        for y in ys:
            grid_polys.append(box(x, y, x + cell_size, y + cell_size))
            grid_ids.append(gid)
            gid += 1

    return gpd.GeoDataFrame(
        {"cell_id": grid_ids},
        geometry=grid_polys,
        crs=CRS_PROJECTED
    )

def aggregate_bins_to_grid(
    waste_bins: gpd.GeoDataFrame,
    grid: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:

    joined = gpd.sjoin(
        waste_bins[["bin_uid", "source", "geometry"]],
        grid[["cell_id", "geometry"]],
        how="left",
        predicate="intersects"
    )

    # Avoid double-counting bins on grid boundaries
    joined = (
        joined
        .sort_values(["bin_uid", "cell_id"])
        .drop_duplicates(subset=["bin_uid"], keep="first")
    )

    counts_total = joined.groupby("cell_id").size().rename("bins_total")

    counts_by_source = (
        joined.groupby(["cell_id", "source"])
        .size()
        .unstack(fill_value=0)
        .rename(columns={
            "park_assets": "bins_park_assets",
            "street_furniture": "bins_street_furniture"
        })
    )

    grid_out = grid.merge(counts_total, on="cell_id", how="left")
    grid_out = grid_out.merge(counts_by_source, on="cell_id", how="left")

    for c in ["bins_total", "bins_park_assets", "bins_street_furniture"]:
        if c not in grid_out.columns:
            grid_out[c] = 0
        grid_out[c] = grid_out[c].fillna(0).astype(int)

    return grid_out[[
        "cell_id", "geometry",
        "bins_total", "bins_park_assets", "bins_street_furniture"
    ]]

def aggregate_pedestrian_to_grid(
    ped_clean: gpd.GeoDataFrame,
    grid: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    """
    Intersects pedestrian segments with the grid and aggregates total segment length per cell.
    Avoids double counting for segments on boundaries by keeping the first matched cell per segment.
    Returns a grid with pedestrian_length_m.
    """
    joined = gpd.sjoin(
        ped_clean[["segment_uid", "ped_length_m", "geometry"]],
        grid[["cell_id", "geometry"]],
        how="left",
        predicate="intersects"
    )

    joined = (
        joined
        .sort_values(["segment_uid", "cell_id"])
        .drop_duplicates(subset=["segment_uid"], keep="first")
    )

    ped_length = (
        joined.groupby("cell_id")["ped_length_m"]
        .sum()
        .rename("pedestrian_length_m")
        .reset_index()
    )

    grid_out = grid.merge(ped_length, on="cell_id", how="left")
    grid_out["pedestrian_length_m"] = grid_out["pedestrian_length_m"].fillna(0).astype(float)

    return grid_out

def aggregate_transit_to_grid(
    stops_clean: gpd.GeoDataFrame,
    grid: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    """
    Assigns stops to grid cells (within) and counts stops per cell.
    Returns a grid with transit_stops_count.
    """
    joined = gpd.sjoin(
        stops_clean[["stop_uid", "geometry"]],
        grid[["cell_id", "geometry"]],
        how="left",
        predicate="within"
    )

    counts = (
        joined.groupby("cell_id")
        .size()
        .rename("transit_stops_count")
        .reset_index()
    )

    grid_out = grid.merge(counts, on="cell_id", how="left")
    grid_out["transit_stops_count"] = grid_out["transit_stops_count"].fillna(0).astype(int)

    return grid_out
