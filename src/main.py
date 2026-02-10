import geopandas as gpd
from src.paths import CLEAN_DIR

from src.data_loader import (
    load_park_bins,
    load_street_bins,
    load_pedestrian_network_gdf,
    load_transit_stops_gdf,
)

from src.data_cleaning import (
    clean_waste_bins,
    clean_pedestrian_network,
    clean_transit_stops,
)

from src.feature_engineering import (
    create_grid,
    aggregate_bins_to_grid,
    aggregate_pedestrian_to_grid,
    aggregate_transit_to_grid,
)


def main():
    # =========================
    # 1) WASTE BINS
    # =========================
    print("Running waste bins pipeline...")

    park_bins = load_park_bins()
    street_bins = load_street_bins()
    waste_bins = clean_waste_bins(park_bins, street_bins)

    # Save clean points (drop problematic fields)
    points_out = CLEAN_DIR / "waste_bins_points_clean.gpkg"
    waste_bins_points = waste_bins.copy()
    drop_cols = [c for c in ["FID", "fid"] if c in waste_bins_points.columns]
    if drop_cols:
        waste_bins_points = waste_bins_points.drop(columns=drop_cols)
    waste_bins_points = waste_bins_points.loc[:, ~waste_bins_points.columns.duplicated()]
    waste_bins_points.to_file(points_out, layer="waste_bins_points", driver="GPKG")
    print("Saved:", points_out)

    # Create grid + aggregate bins
    grid = create_grid(waste_bins, cell_size=250, buffer=2000)
    grid_bins = aggregate_bins_to_grid(waste_bins, grid)
    grid_bins["has_bins"] = grid_bins["bins_total"] > 0

    grid_bins_out = CLEAN_DIR / "grid_250m_waste_bins.gpkg"
    grid_bins.to_file(grid_bins_out, layer="grid_bins", driver="GPKG")
    print("Saved:", grid_bins_out)

    print("Total bins original:", len(waste_bins))
    print("Total bins counted:", int(grid_bins["bins_total"].sum()))

    # =========================
    # 2) PEDESTRIAN PROXY
    # =========================
    print("\nRunning pedestrian proxy pipeline...")

    ped_raw = load_pedestrian_network_gdf()
    ped_clean = clean_pedestrian_network(ped_raw)

    grid_base = gpd.read_file(grid_bins_out, layer="grid_bins")
    grid_with_ped = aggregate_pedestrian_to_grid(ped_clean, grid_base)

    ped_out = CLEAN_DIR / "grid_250m_with_pedestrian_proxy.gpkg"
    grid_with_ped.to_file(ped_out, layer="grid_pedestrian", driver="GPKG")
    print("Saved:", ped_out)
    print("Cells with pedestrian_length_m > 0:", int((grid_with_ped["pedestrian_length_m"] > 0).sum()))

    # =========================
    # 3) TRANSIT STOPS
    # =========================
    print("\nRunning transit stops pipeline...")

    stops_raw = load_transit_stops_gdf()
    stops_clean = clean_transit_stops(stops_raw)

    # IMPORTANT: use the grid that already includes pedestrian (so final layer has bins+ped+transit)
    grid_ped = gpd.read_file(ped_out, layer="grid_pedestrian")
    grid_with_transit = aggregate_transit_to_grid(stops_clean, grid_ped)

    transit_out = CLEAN_DIR / "grid_250m_with_pedestrian_and_transit.gpkg"
    grid_with_transit.to_file(transit_out, layer="grid_ped_transit", driver="GPKG")
    print("Saved:", transit_out)

    print("Cells with transit_stops_count > 0:", int((grid_with_transit["transit_stops_count"] > 0).sum()))
    print("Total stops counted in grid:", int(grid_with_transit["transit_stops_count"].sum()))


  # =========================
    # 4) POPULATION CONTEXT (CITY-LEVEL)
    # =========================
    print("\nRunning population context pipeline...")

    from src.data_loader import load_population_context_df
    from src.data_cleaning import clean_population_context

    pop_raw = load_population_context_df()
    pop_clean = clean_population_context(pop_raw)

    pop_out = CLEAN_DIR / "population_context_city_level.csv"
    pop_clean.to_csv(pop_out, index=False)
    print("Saved:", pop_out)

    # =========================
    # 5) FINAL MASTER INTEGRATION
    # =========================
    print("\nRunning final master integration...")

    from src.integrate import build_master_grid, save_master_grid

    master = build_master_grid()
    save_master_grid(master)

    print("Master cells:", len(master))
    print("Master bins total:", int(master["bins_total"].sum()))
    print("Master stops total:", int(master["transit_stops_count"].sum()))

if __name__ == "__main__":
    main()