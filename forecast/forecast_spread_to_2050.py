"""
File: forecast/forecast_spread_to_2050.py
Description: forcasting until 2050
Output: forecasting/output/forecast_2026_to_2050.csv
"""


import pandas as pd
import geopandas as gpd
import logging

# === Logging Setup ===
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# === CONFIG ===
initial_density_path = "data_generated/hive_density_staged.csv"
shapefile_path = "../preparingHistoricalData/ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp"
output_forecast_path = "forecasting/output/forecast_2026_to_2050.csv"

# === COUNTRY NEIGHBOR MAP ===
neighbors = {
    "France": ["Belgium", "Spain", "Germany", "Italy", "Switzerland", "Luxembourg"],
    "Spain": ["Portugal", "France"],
    "Portugal": ["Spain"],
    "Belgium": ["France", "Netherlands", "Germany", "Luxembourg"],
    "Netherlands": ["Belgium", "Germany"],
    "Germany": ["Denmark", "Netherlands", "Belgium", "France", "Switzerland", "Austria", "Poland", "Czechia", "Luxembourg"],
    "Italy": ["France", "Switzerland", "Austria", "Slovenia"],
    "Switzerland": ["France", "Germany", "Italy", "Austria"],
    "Austria": ["Germany", "Czechia", "Slovakia", "Hungary", "Slovenia", "Switzerland", "Italy"],
    "Luxembourg": ["France", "Belgium", "Germany"],
    "Czechia": ["Germany", "Poland", "Slovakia", "Austria"],
    "Slovakia": ["Czechia", "Austria", "Hungary", "Poland", "Ukraine"],
    "Hungary": ["Slovakia", "Austria", "Slovenia", "Croatia", "Romania", "Ukraine"],
    "Poland": ["Germany", "Czechia", "Slovakia", "Ukraine", "Lithuania"],
    "Slovenia": ["Italy", "Austria", "Hungary", "Croatia"],
    "Croatia": ["Slovenia", "Hungary", "Bosnia and Herzegovina", "Serbia"],
    "Bosnia and Herzegovina": ["Croatia", "Serbia"],
    "Serbia": ["Bosnia and Herzegovina", "Croatia", "Hungary", "Romania", "Bulgaria"],
    "Romania": ["Hungary", "Serbia", "Ukraine", "Bulgaria"],
    "Bulgaria": ["Serbia", "Romania", "Greece"],
    "Greece": ["Bulgaria"],
    "Denmark": ["Germany"],
    "Norway": ["Sweden"],
    "Sweden": ["Norway", "Finland"],
    "Finland": ["Sweden", "Estonia"],
    "Estonia": ["Latvia", "Finland"],
    "Latvia": ["Estonia", "Lithuania"],
    "Lithuania": ["Latvia", "Poland"],
    "Ukraine": ["Poland", "Slovakia", "Hungary", "Romania"]
}
all_countries = list(neighbors.keys())

# # === GROWTH FUNCTIONS ===
# def growth_stage_1(density, year_in_stage):
#     return density * (1 + 0.7)  # exponential
#
# def growth_stage_2(density, year_in_stage):
#     return density + (0.0008 / (1 + year_in_stage))  # flattening
#
# def growth_stage_3(density, year_in_stage):
#     return density + (0.0002 / (1 + year_in_stage ** 1.5))  # very slow

# === REVISED GROWTH FUNCTIONS ===

def growth_stage_1(density, year_in_stage):
    return density * (1 + 0.35)
    # Conservative exponential growth

def growth_stage_2(density, year_in_stage):
    return density + 0.0005 * (1 + 1 / (year_in_stage + 1)**0.5)
    # Accelerated but saturating linear-log growth

def growth_stage_3(density, year_in_stage):
    return density + 0.0003 / ((year_in_stage + 1) ** 1.2)
    # Conservative slow-down


# === LOAD DATA ===
initial_df = pd.read_csv(initial_density_path)
start_year = initial_df["year"].max() - 1
initial_df = initial_df[initial_df["year"] == start_year][["country", "final_stage", "hive_density"]]

# Load area
gdf = gpd.read_file(shapefile_path)
gdf = gdf.to_crs(epsg=6933)
gdf["area_km2"] = gdf["geometry"].area / 1e6
area_df = gdf[["ADMIN", "area_km2"]].rename(columns={"ADMIN": "country"})

# Merge state
state_df = pd.merge(initial_df, area_df, on="country", how="left")
state_df["stage_year"] = 1
state_map = state_df.set_index("country").to_dict("index")

# === FORECAST LOOP ===
forecast_years = list(range(start_year + 1, 2051))
forecast_rows = []

for year in forecast_years:
    logging.info(f"Forecasting year {year}...")
    new_state_map = {}

    for country in all_countries:
        prev = state_map.get(country)

        if prev:
            stage = prev["final_stage"]
            stage_year = prev["stage_year"]
            area_km2 = prev["area_km2"]
            prev_density = prev["hive_density"]

            if stage == 1:
                new_density = growth_stage_1(prev_density, stage_year)
            elif stage == 2:
                new_density = growth_stage_2(prev_density, stage_year)
            else:
                new_density = growth_stage_3(prev_density, stage_year)

            if stage == 1 and new_density >= 0.0002:
                next_stage = 2
                stage_year = 1
            elif stage == 2 and new_density >= 0.005:
                next_stage = 3
                stage_year = 1
            else:
                next_stage = stage
                stage_year += 1

            new_state_map[country] = {
                "final_stage": next_stage,
                "stage_year": stage_year,
                "hive_density": new_density,
                "area_km2": area_km2
            }

        else:
            for neighbor in neighbors.get(country, []):
                n_data = state_map.get(neighbor)
                if n_data and n_data["final_stage"] >= 2:
                    area = area_df[area_df["country"] == country]["area_km2"]
                    if area.empty:
                        continue
                    new_density = 2 / area.values[0]
                    new_state_map[country] = {
                        "final_stage": 1,
                        "stage_year": 1,
                        "hive_density": new_density,
                        "area_km2": area.values[0]
                    }
                    logging.info(f"{year}: {neighbor} → {country} invaded (stage 2+)")
                    break

    for c, v in new_state_map.items():
        dens = v["hive_density"]
        area = v["area_km2"]
        dens = 0 if pd.isna(dens) else dens
        area = 0 if pd.isna(area) else area
        hives = dens * area
        forecast_rows.append({
            "year": year,
            "country": c,
            "stage": v["final_stage"],
            "stage_year": v["stage_year"],
            "hive_density": round(dens, 7),
            "hive_count": round(hives)
        })

    state_map = new_state_map.copy()

# === SAVE TO CSV ===
forecast_df = pd.DataFrame(forecast_rows)
forecast_df = forecast_df.sort_values(by=["year", "country"])
forecast_df.to_csv(output_forecast_path, index=False)
logging.info(f"✅ Forecast saved to {output_forecast_path}")
