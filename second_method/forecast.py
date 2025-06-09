#!/usr/bin/env python3
"""
File: forecast_bees_impact.py
Description: Forecasts bee colony decline until 2050 based on hornet spread
             using correlation from each country.
"""

import pandas as pd
import geopandas as gpd
import os

# === PATHS ===
hornet_path = "output/hornet_combined_corrected.csv"
bee_trend_path = "output/bee_density_trends.csv"
correlation_path = "output/correlationByCountry.csv"
shapefile_path = "../preparingHistoricalData/ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp"
output_path = "output/bee_forecast_2026_to_2050.csv"
os.makedirs("output", exist_ok=True)

# === LOAD DATA ===
hornets = pd.read_csv(hornet_path)
bees = pd.read_csv(bee_trend_path)
correlations = pd.read_csv(correlation_path)

# === PREPARE CORRELATION MAPPING ===
correlations = correlations.dropna(subset=["Density_vs_BeeGrowth_r"])
cor_map = correlations.set_index("Country")["Density_vs_BeeGrowth_r"].to_dict()

# === COUNTRY NEIGHBORS ===
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

# === AREA LOOKUP ===
gdf = gpd.read_file(shapefile_path).to_crs(epsg=6933)
gdf["Area_km2"] = gdf["geometry"].area / 1e6
area_map = gdf.set_index("ADMIN")["Area_km2"].to_dict()

# === INITIALIZE STATE ===
latest_bees = bees[bees["Year"] == 2024][["Country", "Bee_Density", "Bee_Count", "Area_km2"]].dropna()
state_map = latest_bees.set_index("Country").to_dict("index")

forecast_rows = []
for year in range(2025, 2051):
    hornets_year = hornets[hornets["Year"] == year].set_index("Country")
    new_state_map = {}

    for country, bee_data in state_map.items():
        area = bee_data.get("Area_km2", area_map.get(country, 0))
        density = bee_data["Bee_Density"]
        hornet_density = hornets_year.at[country, "hive_density"] if country in hornets_year.index else 0

        # === Lag Effect: Combine with previous year ===
        prev_year = year - 1
        if prev_year in hornets["Year"].values:
            prev_density = hornets[hornets["Year"] == prev_year].set_index("Country").get("hive_density",
                                                                                          pd.Series()).get(country, 0)
            hornet_density_avg = (hornet_density + prev_density) / 2
        else:
            hornet_density_avg = hornet_density

        corr = cor_map.get(country, -0.3)

        # === Apply non-linear biological decline ===
        base_decline = (hornet_density_avg * 10) ** 1.1 * abs(corr) * 2.0

        # Cap decline to 50% of density
        decline = min(base_decline, 0.5 * density)

        new_density = max(density - decline, 0)
        new_count = new_density * area

        new_state_map[country] = {
            "Bee_Density": new_density,
            "Bee_Count": round(new_count),
            "Area_km2": area
        }

        forecast_rows.append({
            "Year": year,
            "Country": country,
            "Hornet_Density": hornet_density,
            "Bee_Density": round(new_density, 6),
            "Bee_Count": round(new_count)
        })

    state_map = new_state_map

# === SAVE TO CSV ===
# Create DataFrame
df = pd.DataFrame(forecast_rows)
df = df.sort_values(by=["Country", "Year"])

# Calculate Bee_Density_Growth per country
df["Bee_Density_Growth"] = df.groupby("Country")["Bee_Density"].pct_change().round(4).fillna(0)

# Save final table
df.to_csv(output_path, index=False)
print(f"✅ Bee forecast with growth rates saved to: {output_path}")

