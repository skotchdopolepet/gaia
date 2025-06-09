import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import os

# === CONFIG ===
forecast_csv = "forecasting/output/forecast_2026_to_2050.csv"
shapefile_path = "../preparingHistoricalData/ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp"

# === 1. Load forecast output ===
df = pd.read_csv(forecast_csv)

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
    'Switzerland': 'Switzerland',
    'Czechia': 'Czechia',
    'Austria': 'Austria',
    'Slovakia': 'Slovakia',
    'Poland': 'Poland',
    'Hungary': 'Hungary',
    'Slovenia': 'Slovenia',
    'Croatia': 'Croatia',
    'Bosnia and Herzegovina': 'Bosnia and Herzegovina',
    'Serbia': 'Serbia',
    'Romania': 'Romania',
    'Bulgaria': 'Bulgaria',
    'Greece': 'Greece',
    'Denmark': 'Denmark',
    'Norway': 'Norway',
    'Sweden': 'Sweden',
    'Finland': 'Finland',
    'Estonia': 'Estonia',
    'Latvia': 'Latvia',
    'Lithuania': 'Lithuania',
    'Ukraine': 'Ukraine'
}
df['country_gis'] = df['country'].map(name_mapping)

# === 2. Load Natural Earth shapefile ===
if not os.path.exists(shapefile_path):
    raise FileNotFoundError("🌍 Shapefile not found. Please place it under ../preparingHistoricalData/ne_110m_admin_0_countries/")

world = gpd.read_file(shapefile_path)

# === 3. Filter and clean country geometries ===
europe = world[world['NAME'].isin(name_mapping.values())]
europe = europe.explode(index_parts=True).reset_index(drop=True)
europe['area'] = europe.geometry.area
europe = europe.sort_values(by=['NAME', 'area'], ascending=[True, False])
europe = europe.drop_duplicates(subset='NAME', keep='first')

# === 4. Set color scale for hive density ===
vmin = 0
vmax = 0.02  # adjust upper limit for color scaling

# === 5. Plot maps year-by-year ===
for year in sorted(df['year'].unique()):
    df_year = df[df['year'] == year]
    merged = europe.merge(df_year, left_on='NAME', right_on='country_gis', how='left')

    fig, ax = plt.subplots(figsize=(11, 9))

    # Borders
    merged.boundary.plot(ax=ax, color="grey", linewidth=0.5)

    # Color fill by density
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

    # Add text with hive counts
    for _, row in merged.iterrows():
        if pd.notna(row['hive_count']) and row['hive_count'] > 0:
            centroid = row['geometry'].centroid
            ax.text(
                centroid.x,
                centroid.y,
                f"{int(row['hive_count'])}",
                fontsize=6,
                ha='center',
                va='center',
                color='black'
            )

    ax.set_title(f"Forecasted Vespa velutina Hive Density – {year}", fontsize=14)
    ax.axis('off')
    plt.tight_layout()
    plt.show()
