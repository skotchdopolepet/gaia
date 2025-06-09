#!/usr/bin/env python3
"""
File: visualize_bee_forecast_full.py
Description: Visualizes bee density and count maps from 2004 to 2050.
"""

import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# === CONFIG ===
forecast_path = "output/bee_forecast_2026_to_2050.csv"
historical_path = "output/bee_density_trends.csv"
shapefile_path = "../preparingHistoricalData/ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp"
output_folder = "output/bee_forecast_visuals_full"
os.makedirs(output_folder, exist_ok=True)

# === LOAD & PREPARE DATA ===
forecast_df = pd.read_csv(forecast_path)
historical_df = pd.read_csv(historical_path)

# Ensure columns match
historical_df = historical_df.rename(columns={
    "Bee_Density": "Bee_Density",
    "Bee_Count": "Bee_Count"
})

# Use only necessary columns
forecast_df = forecast_df[["Country", "Year", "Bee_Density", "Bee_Count"]]
historical_df = historical_df[["Country", "Year", "Bee_Density", "Bee_Count"]]

# Combine historical + forecast
full_df = pd.concat([historical_df, forecast_df], ignore_index=True)

# === LOAD SHAPEFILE ===
world = gpd.read_file(shapefile_path)
europe = world[world['NAME'].isin(full_df["Country"].unique())]
europe = europe.explode(index_parts=True).reset_index(drop=True)
europe['area'] = europe.geometry.area
europe = europe.sort_values(by=['NAME', 'area'], ascending=[True, False])
europe = europe.drop_duplicates(subset='NAME', keep='first')

# === COLOR RANGE ===
vmax = full_df["Bee_Density"].max()
vmin = 0

# === PLOT EACH YEAR ===
for year in sorted(full_df["Year"].unique()):
    df_year = full_df[full_df["Year"] == year]
    merged = europe.merge(df_year, left_on='NAME', right_on='Country', how='left')

    fig, ax = plt.subplots(figsize=(11, 9))
    merged.boundary.plot(ax=ax, color="grey", linewidth=0.5)
    merged.plot(
        ax=ax,
        column='Bee_Density',
        cmap='RdYlGn',  # Green = high, Red = low (default)
        edgecolor='0.8',
        legend=True,
        alpha=0.8,  # pastel effect
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
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(f"{output_folder}/bee_density_{year}.png", dpi=200)
    plt.close()

print(f"✅ Maps saved for 2004–2050 in: {output_folder}")

# === NEW: PLOT GROWTH TRENDS OVER TIME ===
growth_output_folder = os.path.join(output_folder, "bee_growth_trends")
os.makedirs(growth_output_folder, exist_ok=True)

# Reload forecast with Bee_Density_Growth
forecast_df_growth = pd.read_csv(forecast_path)
forecast_df_growth = forecast_df_growth[["Country", "Year", "Bee_Density_Growth"]]

# Compute historical growth too
historical_df = historical_df.sort_values(by=["Country", "Year"])
historical_df["Bee_Density_Growth"] = historical_df.groupby("Country")["Bee_Density"].pct_change().round(4).fillna(0)

# Combine again
growth_df = pd.concat([historical_df[["Country", "Year", "Bee_Density_Growth"]], forecast_df_growth], ignore_index=True)

# Plot for each country
for country in sorted(growth_df["Country"].unique()):
    country_df = growth_df[growth_df["Country"] == country].sort_values(by="Year")

    plt.figure(figsize=(8, 4))
    plt.plot(country_df["Year"], country_df["Bee_Density_Growth"] * 100, marker='o', linestyle='-')
    plt.title(f"{country} – Bee Density Growth Rate (%)")
    plt.xlabel("Year")
    plt.ylabel("Growth (%)")
    plt.axhline(y=0, color='grey', linestyle='--')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{growth_output_folder}/growth_trend_{country}.png", dpi=150)
    plt.close()

print(f"✅ Growth trend charts saved per country in: {growth_output_folder}")

# Plot for each country
for country in sorted(growth_df["Country"].unique()):
    growth_country = growth_df[growth_df["Country"] == country].sort_values(by="Year")
    count_country = full_df[full_df["Country"] == country].sort_values(by="Year")

    fig, ax1 = plt.subplots(figsize=(9, 4))

    # === Left axis: Growth (%)
    ax1.plot(growth_country["Year"], growth_country["Bee_Density_Growth"] * 100,
             color='tab:red', marker='o', label='Bee Density Growth (%)')
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Growth Rate (%)", color='tab:red')
    ax1.tick_params(axis='y', labelcolor='tab:red')
    ax1.axhline(y=0, color='gray', linestyle='--', linewidth=0.8)
    ax1.grid(True, which='major', axis='both', linestyle='--', alpha=0.4)

    # === Right axis: Bee Count
    ax2 = ax1.twinx()
    ax2.plot(count_country["Year"], count_country["Bee_Count"],
             color='tab:blue', marker='x', linestyle='--', label='Bee Count')
    ax2.set_ylabel("Bee Count", color='tab:blue')
    ax2.tick_params(axis='y', labelcolor='tab:blue')

    # === Title and save
    plt.title(f"{country} – Bee Density Growth and Count Over Time")
    fig.tight_layout()
    plt.savefig(f"{growth_output_folder}/growth_trend_{country}.png", dpi=150)
    plt.close()
