import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
 
# Load Pernis Apivorus dataset
df = pd.read_csv(r"C:\Users\Adriana Slúková\OneDrive - Vysoké učení technické v Brně\Dokumenty\Pernis_2024-2025.csv")
 
# Rename relevant columns to match expected format
df = df.rename(columns={
    'Event date': 'eventDate',
    'Decimal latitude': 'decimalLatitude',
    'Decimal longitude': 'decimalLongitude'
})
 
# Drop rows with missing coordinates or date
df = df.dropna(subset=['decimalLatitude', 'decimalLongitude', 'eventDate'])
 
# Convert eventDate to datetime and extract year
df['eventDate'] = pd.to_datetime(df['eventDate'], errors='coerce')
df = df.dropna(subset=['eventDate'])
df['year'] = df['eventDate'].dt.year
 
# Create GeoDataFrame from observation points
geometry = [Point(xy) for xy in zip(df['decimalLongitude'], df['decimalLatitude'])]
gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
 
# Load world shapefile (adjust path if needed)
world = gpd.read_file(r"C:\Users\Adriana Slúková\Downloads\copy observation visuals\copy observation visuals\ne_110m_admin_0_countries")
 
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
    gdf[gdf['year'] == year].plot(ax=ax, color='darkorange', markersize=1, alpha=0.6)
 
    ax.set_xlim(europe_bounds['minx'], europe_bounds['maxx'])
    ax.set_ylim(europe_bounds['miny'], europe_bounds['maxy'])
 
    plt.title(f"Pernis Apivorus Observations – {year}")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.grid(True)
    plt.tight_layout()
    plt.show()