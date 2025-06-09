import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import os

# === CONFIG ===
forecast_path = "../forecast/forecasting/output/forecast_2026_to_2050.csv"
density_path = "../forecast/data_generated/hive_density_staged.csv"
bee_path = "honeybees_2004-2024.csv"
shapefile_path = "../preparingHistoricalData/ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp"
output_folder = "output"
os.makedirs(output_folder, exist_ok=True)

# === LOAD DATA ===
forecast_df = pd.read_csv(forecast_path)
density_df = pd.read_csv(density_path)
bees_df = pd.read_csv(bee_path)
world = gpd.read_file(shapefile_path)

# === STRIP & RENAME 'Czech Republic' TO 'Czechia' (ANY CASE) ===
for df in [forecast_df, density_df, bees_df]:
    # Standardize column name first
    cols = [col.strip().lower() for col in df.columns]
    if "country" in cols:
        country_col = df.columns[[c.strip().lower() == "country" for c in df.columns]][0]
        df.rename(columns={country_col: "Country"}, inplace=True)
        df["Country"] = df["Country"].str.strip().replace("Czech Republic", "Czechia")



# === CLEAN COLUMN NAMES ===
forecast_df.columns = forecast_df.columns.str.strip()
density_df.columns = density_df.columns.str.strip()
bees_df.columns = bees_df.columns.str.strip()

# === RENAME COLUMNS ===
forecast_df.rename(columns={"year": "Year", "country": "Country", "count": "hive_count"}, inplace=True)
density_df.rename(columns={
    "year": "Year",
    "country": "Country",
    "Hornet_Count": "hive_count",
    "hive_density": "hive_density",
    "area_km2": "Area_km2",
    "final_stage": "stage"
}, inplace=True)
bees_df.rename(columns={"Honey_bee_colonies": "Bee_Count"}, inplace=True)

# === PREPARE SHAPEFILE AREA ===
world["Country"] = world["ADMIN"].str.strip()
world = world.to_crs(epsg=3857)  # Web Mercator for area calc
world["shapefile_area_km2"] = world["geometry"].area / 1e6
area_lookup = world[["Country", "shapefile_area_km2"]]

# === PART 1: Combine Hornet Forecast and Density Data ===
density_part = density_df[density_df["Year"] <= 2024][
    ["Country", "Year", "hive_count", "Area_km2", "hive_density", "stage"]
]

forecast_filtered = forecast_df[forecast_df["Year"] > 2024][["Country", "Year", "hive_count"]].copy()

if "hive_density" in forecast_df.columns and "stage" in forecast_df.columns:
    density_info = forecast_df[forecast_df["Year"] > 2024][["Country", "Year", "hive_density", "stage"]]
    forecast_filtered = pd.merge(forecast_filtered, density_info, on=["Country", "Year"], how="left")

latest_density = density_part[density_part["Year"] == 2024][["Country", "Area_km2"]]
forecast_enriched = pd.merge(forecast_filtered, latest_density, on="Country", how="left")

# Fill missing area from shapefile
forecast_enriched = pd.merge(forecast_enriched, area_lookup, on="Country", how="left")
forecast_enriched["Area_km2"] = forecast_enriched["Area_km2"].fillna(forecast_enriched["shapefile_area_km2"])
forecast_enriched.drop(columns=["shapefile_area_km2"], inplace=True)

# Final hornet output
hornet_combined = pd.concat([density_part, forecast_enriched], ignore_index=True).sort_values(["Country", "Year"])
hornet_combined = hornet_combined[["Country", "Year", "hive_count", "Area_km2", "hive_density", "stage"]]
hornet_combined.to_csv(f"{output_folder}/hornet_combined_corrected.csv", index=False)

# === PART 2: Bee Density and Growth ===
bees_df["Country"] = bees_df["Country"].str.strip()
area_lookup = area_lookup.copy()
area_lookup["Country"] = area_lookup["Country"].str.strip()


bees_df = pd.merge(bees_df, area_lookup, on="Country", how="left")
bees_df.rename(columns={"shapefile_area_km2": "Area_km2"}, inplace=True)

bees_df["Bee_Density"] = bees_df["Bee_Count"] / bees_df["Area_km2"]
bees_df.sort_values(["Country", "Year"], inplace=True)

bees_df["Bee_Density_Growth"] = (
    bees_df.groupby("Country")["Bee_Density"]
    .pct_change(fill_method=None)
    .round(4)
)

bees_df.to_csv(f"{output_folder}/bee_density_trends.csv", index=False)
