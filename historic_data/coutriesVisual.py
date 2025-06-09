import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import os
#1.6

# === 1. Load data ===
df = pd.read_csv("estimated_hives_weighted_output_clamped.csv")

# Mapping internal country names to those in shapefile
name_mapping = {
    'Netherlands': 'Netherlands',
    'Belgium': 'Belgium',
    'France': 'France',
    'Spain': 'Spain',
    'Portugal': 'Portugal',
    'Germany': 'Germany',
    'Italy': 'Italy',
    'Luxembourg': 'Luxembourg',
    'Switzerland': 'Switzerland'
}
df['country_gis'] = df['country'].map(name_mapping)

# === 2. Load Natural Earth shapefile (must be downloaded locally) ===
shapefile_path = "ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp"
if not os.path.exists(shapefile_path):
    raise FileNotFoundError(
        "🌍 Shapefile not found. Please download from naturalearthdata.com and unzip to 'ne_110m_admin_0_countries/'.")

world = gpd.read_file(shapefile_path)

# Filter to only countries we have data for
europe = world[world['NAME'].isin(name_mapping.values())]

# === 3. Remove islands: keep only largest mainland polygon per country ===
europe = europe.explode(index_parts=True).reset_index(drop=True)
europe['area'] = europe.geometry.area
europe = europe.sort_values(by=['NAME', 'area'], ascending=[True, False])
europe = europe.drop_duplicates(subset='NAME', keep='first')

# === 4. Determine fixed color scale across all years ===
vmin = 0
vmax = 10000

# === 5. Plot one map per year ===
for year in sorted(df['year'].unique()):
    df_year = df[df['year'] == year]
    merged = europe.merge(df_year, left_on='NAME', right_on='country_gis', how='left')

    fig, ax = plt.subplots(figsize=(10, 8))

    # Draw country borders
    merged.boundary.plot(ax=ax, color="grey", linewidth=0.6)

    # Fill countries by hive count with fixed scale
    merged.plot(
        ax=ax,
        column='estimated_hives_with_weighting',
        cmap='Reds',
        legend=True,
        edgecolor='0.8',
        vmin=vmin,
        vmax=vmax,
        missing_kwds={"color": "lightgrey", "label": "No data"}
    )

    ax.set_title(f"Estimated Vespa velutina Hives – {year}", fontsize=14)
    ax.axis('off')
    plt.tight_layout()
    plt.show()
