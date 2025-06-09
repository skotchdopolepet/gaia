#!/usr/bin/env python3
"""
File: outputs/bee_density_combined.py
Description: Visualizes yearly honeybee density maps (2004–2024) across Europe.
"""

import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# === PATHS ===
bee_path = "honeybees_2004-2024.csv"
shapefile_path = "../preparingHistoricalData/ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp"
output_folder = "output/bee_visuals"
os.makedirs(output_folder, exist_ok=True)

# === LOAD & CLEAN DATA ===
bees = pd.read_csv(bee_path)
bees.columns = bees.columns.str.strip()
bees.rename(columns={"Honey_bee_colonies": "Bee_Count"}, inplace=True)
bees["Country"] = bees["Country"].str.strip().replace("Czech Republic", "Czechia")

# === LOAD SHAPEFILE AND COMPUTE AREA ===
world = gpd.read_file(shapefile_path)
world["Country"] = world["ADMIN"].str.strip().replace("Czech Republic", "Czechia")

# Keep only relevant countries (from bee data)
europe = world[world["Country"].isin(bees["Country"].unique())].copy()

# Handle multi-polygons: keep largest geometry per country
europe = europe.explode(index_parts=True).reset_index(drop=True)
europe["area"] = europe.geometry.area
europe = europe.sort_values(by=["Country", "area"], ascending=[True, False])
europe = europe.drop_duplicates(subset="Country", keep="first")

# Merge area back into bees and compute density
area_lookup = europe[["Country", "area"]].copy()
area_lookup["Area_km2"] = area_lookup["area"] / 1e6
bees = pd.merge(bees, area_lookup[["Country", "Area_km2"]], on="Country", how="left")
bees["Bee_Density"] = bees["Bee_Count"] / bees["Area_km2"]

# === PLOT: Yearly Bee Density Maps ===
vmin = 0.2
vmax = 4.5

for year in sorted(bees["Year"].unique()):
    df_year = bees[bees["Year"] == year].copy()
    merged = europe.merge(df_year, on="Country", how="left")

    fig, ax = plt.subplots(figsize=(11, 9))
    merged.boundary.plot(ax=ax, color="grey", linewidth=0.5)
    merged.plot(
        ax=ax,
        column='Bee_Density',
        cmap='YlGnBu',
        legend=True,
        edgecolor='0.8',
        vmin=vmin,
        vmax=vmax,
        missing_kwds={"color": "lightgrey", "label": "No data"}
    )

    for _, row in merged.iterrows():
        if pd.notna(row['Bee_Count']) and row['Bee_Count'] > 0:
            centroid = row['geometry'].centroid
            ax.text(centroid.x, centroid.y, f"{int(row['Bee_Count'])}", fontsize=6,
                    ha='center', va='center', color='black')

    ax.set_title(f"Honeybee Density – {year}", fontsize=14)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, f"bee_density_{year}.png"), dpi=200)
    plt.close()

print(f"✅ Bee density maps saved to: {output_folder}")
