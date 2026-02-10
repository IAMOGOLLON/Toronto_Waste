from __future__ import annotations

import geopandas as gpd
import pandas as pd

from src.paths import CLEAN_DIR


def build_master_grid() -> gpd.GeoDataFrame:
    """
    Final integration:
    Uses the already-integrated grid (bins + pedestrian + transit),
    performs QA, optional derived metrics, and returns a master grid.
    """
    in_path = CLEAN_DIR / "grid_250m_with_pedestrian_and_transit.gpkg"
    layer = "grid_ped_transit"

    g = gpd.read_file(in_path, layer=layer)

    # --- Required columns check ---
    required = ["cell_id", "geometry", "bins_total", "pedestrian_length_m", "transit_stops_count"]
    missing = [c for c in required if c not in g.columns]
    if missing:
        raise ValueError(f"Missing required columns in integrated grid: {missing}")

    # --- Basic cleaning / types ---
    g = g.copy()
    g["cell_id"] = pd.to_numeric(g["cell_id"], errors="coerce").astype("Int64")

    for c in ["bins_total", "bins_park_assets", "bins_street_furniture", "transit_stops_count"]:
        if c in g.columns:
            g[c] = pd.to_numeric(g[c], errors="coerce").fillna(0).astype(int)

    g["pedestrian_length_m"] = pd.to_numeric(g["pedestrian_length_m"], errors="coerce").fillna(0.0)

    # --- Derived metrics (optional but useful) ---
    # 250m x 250m = 62,500 m² = 0.0625 km²
    CELL_AREA_KM2 = 0.0625
    g["bins_per_km2"] = g["bins_total"] / CELL_AREA_KM2
    g["stops_per_km2"] = g["transit_stops_count"] / CELL_AREA_KM2

    # Ped density: meters of pedestrian network per km²
    g["ped_m_per_km2"] = g["pedestrian_length_m"] / CELL_AREA_KM2

    # Ratio examples (avoid divide-by-zero)
    g["bins_per_ped_km"] = g["bins_total"] / (g["pedestrian_length_m"] / 1000).replace({0: pd.NA})
    g["bins_per_stop"] = g["bins_total"] / g["transit_stops_count"].replace({0: pd.NA})

    # --- Final columns: keep what matters ---
    cols_keep = [
        "cell_id",
        "geometry",
        "bins_total",
        "bins_park_assets",
        "bins_street_furniture",
        "pedestrian_length_m",
        "transit_stops_count",
        "bins_per_km2",
        "stops_per_km2",
        "ped_m_per_km2",
        "bins_per_ped_km",
        "bins_per_stop",
    ]
    cols_keep = [c for c in cols_keep if c in g.columns]
    g = g[cols_keep].copy()

    return g


def save_master_grid(g: gpd.GeoDataFrame) -> None:
    out_path = CLEAN_DIR / "grid_250m_master.gpkg"
    g.to_file(out_path, layer="grid_master", driver="GPKG")
    print("Saved:", out_path)
