#!/usr/bin/env python3
"""
File: outputs/combined.py
Description: Visualizes invasion stage progression and yearly hive density maps (2004–2050).
"""

import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# === PATHS ===
forecast_path = "forecast/forecasting/output/forecast_2026_to_2050.csv"
historical_path_density = "forecast/data_generated/hive_density_staged.csv"
shapefile_path = "preparingHistoricalData/ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp"
output_folder = "outputs/combined_visuals"
os.makedirs(output_folder, exist_ok=True)

# === LOAD & PREPARE DATA ===
forecast = pd.read_csv(forecast_path)
historical = pd.read_csv(historical_path_density)

# Harmonize
forecast.rename(columns={"stage": "final_stage"}, inplace=True)
forecast = forecast[["year", "country", "final_stage", "hive_density", "hive_count"]]
historical = historical[["year", "country", "final_stage", "hive_density", "hive_count"]]

# Combine
df = pd.concat([historical, forecast], ignore_index=True)
df = df.dropna(subset=["final_stage"])
df["year"] = df["year"].astype(int)
df["final_stage"] = df["final_stage"].astype(int)

# === PLOT: Invasion Stage Timeline ===
stage_colors = {1: "#99d98c", 2: "#f9c74f", 3: "#f94144"}
countries = sorted(df["country"].unique())
fig, ax = plt.subplots(figsize=(14, 0.4 * len(countries) + 2))

for i, country in enumerate(countries):
    sub = df[df["country"] == country].sort_values("year")
    offset_y = i * 4
    y_vals = sub["final_stage"] + offset_y
    ax.plot(sub["year"], y_vals, color="#333333", linewidth=1.5, zorder=2)
    ax.scatter(sub["year"], y_vals, c=[stage_colors[s] for s in sub["final_stage"]],
               edgecolors="black", s=60, zorder=3)
    ax.text(sub["year"].min() - 1, offset_y + 2, country, va='center', ha='right', fontsize=9)

ax.set_yticks([])
ax.set_xlabel("Year", fontsize=12)
ax.set_title("Combined Invasion Stage Progression (2004–2050)", fontsize=14)
ax.grid(axis='x', linestyle="--", alpha=0.4)
plt.tight_layout()
plt.savefig(os.path.join(output_folder, "invasion_stage_over_time_spaced.png"), dpi=300)
plt.close()

# === PLOT: Yearly Hive Density Maps ===
world = gpd.read_file(shapefile_path)
europe = world[world['NAME'].isin(df["country"].unique())]
europe = europe.explode(index_parts=True).reset_index(drop=True)
europe['area'] = europe.geometry.area
europe = europe.sort_values(by=['NAME', 'area'], ascending=[True, False])
europe = europe.drop_duplicates(subset='NAME', keep='first')

vmin = 0
vmax = 0.015

for year in sorted(df['year'].unique()):
    df_year = df[df['year'] == year]
    merged = europe.merge(df_year, left_on='NAME', right_on='country', how='left')

    fig, ax = plt.subplots(figsize=(11, 9))
    merged.boundary.plot(ax=ax, color="grey", linewidth=0.5)
    merged.plot(
        ax=ax,
        column='hive_density',
        cmap='OrRd',
        legend=True,
        edgecolor='0.8',
        vmin=vmin,
        vmax=vmax,
        missing_kwds={"color": "lightgrey", "label": "No data"}
    )

    for _, row in merged.iterrows():
        if pd.notna(row['hive_count']) and row['hive_count'] > 0:
            centroid = row['geometry'].centroid
            ax.text(centroid.x, centroid.y, f"{int(row['hive_count'])}", fontsize=6,
                    ha='center', va='center', color='black')

    ax.set_title(f"Vespa velutina Hive Density – {year}", fontsize=14)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, f"hive_map_{year}.png"), dpi=200)
    plt.close()

print(f"✅ All plots saved to: {output_folder}")
