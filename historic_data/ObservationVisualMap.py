import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
#1.1

# Load original files
df_main = pd.read_csv('GAIA_combined/combined_main.csv')
df_old = pd.read_csv('GAIA_combined/combined_old format_to_2009.csv')

# Combine both datasets
df = pd.concat([df_main, df_old], ignore_index=True)

# Drop rows with missing coordinates or date
df = df.dropna(subset=['decimalLatitude', 'decimalLongitude', 'eventDate'])

# Convert eventDate to datetime and extract year
df['eventDate'] = pd.to_datetime(df['eventDate'], errors='coerce')
df = df.dropna(subset=['eventDate'])
df['year'] = df['eventDate'].dt.year

# Create GeoDataFrame from observation points
geometry = [Point(xy) for xy in zip(df['decimalLongitude'], df['decimalLatitude'])]
gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

# Load world shapefile
world = gpd.read_file('ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp')

# Define Europe bounding box
europe_bounds = {
    'minx': -25,
    'maxx': 45,
    'miny': 34,
    'maxy': 72
}

# Plot observations per year
for year in sorted(gdf['year'].unique()):
    fig, ax = plt.subplots(figsize=(9, 6))

    world.plot(ax=ax, color='lightgrey', edgecolor='white')
    gdf[gdf['year'] == year].plot(ax=ax, color='red', markersize=5, alpha=0.6)

    ax.set_xlim(europe_bounds['minx'], europe_bounds['maxx'])
    ax.set_ylim(europe_bounds['miny'], europe_bounds['maxy'])

    plt.title(f"Vespa velutina Observations – {year} (Europe Only)")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
