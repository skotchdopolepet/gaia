import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
#1.3

# Load hive summary
hives_df = pd.read_csv('estimated_hives_summary.csv')

# Create GeoDataFrame from centroids
geometry = [Point(xy) for xy in zip(hives_df['centroid_lon'], hives_df['centroid_lat'])]
gdf = gpd.GeoDataFrame(hives_df, geometry=geometry, crs="EPSG:4326")

# Load world shapefile
world = gpd.read_file('ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp')

# Define Europe bounding box
europe_bounds = {
    'minx': -25,   # westernmost
    'maxx':  45,   # easternmost
    'miny':  34,   # southernmost
    'maxy':  72    # northernmost
}

# Plot hive points per year, zoomed to Europe
for year in sorted(gdf['year'].unique()):
    fig, ax = plt.subplots(figsize=(9, 6))

    world.plot(ax=ax, color='lightgrey', edgecolor='white')
    gdf[gdf['year'] == year].plot(ax=ax, color='red', markersize=5)

    ax.set_xlim(europe_bounds['minx'], europe_bounds['maxx'])
    ax.set_ylim(europe_bounds['miny'], europe_bounds['maxy'])

    plt.title(f"Vespa velutina Hive Centroids – {year} (Europe Only)")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
