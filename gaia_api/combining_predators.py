import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
 
# === Načítanie CSV súborov + pridanie druhu ako stĺpca ===
df_pernis = pd.read_csv(r"C:\Users\Adriana Slúková\OneDrive - Vysoké učení technické v Brně\Dokumenty\Pernis_2024-2025.csv")
df_pernis['species'] = 'Pernis apivorus'
 
df_gallus = pd.read_csv(r"C:\Users\Adriana Slúková\OneDrive - Vysoké učení technické v Brně\Dokumenty\Gallus_2024-2025.csv")
df_gallus['species'] = 'Gallus gallus'
 
df_martes = pd.read_csv(r"C:\Users\Adriana Slúková\OneDrive - Vysoké učení technické v Brně\Dokumenty\Martes_2024-2025.csv")
df_martes['species'] = 'Martes martes'
 
# Spojenie všetkých dát
df_all = pd.concat([df_pernis, df_gallus, df_martes], ignore_index=True)
 
# Oprava názvov stĺpcov (ak treba)
df_all = df_all.rename(columns={
    'Event date': 'eventDate',
    'Decimal latitude': 'decimalLatitude',
    'Decimal longitude': 'decimalLongitude'
})
 
# Vyčistenie dát
df_all = df_all.dropna(subset=['decimalLatitude', 'decimalLongitude', 'eventDate'])
df_all['eventDate'] = pd.to_datetime(df_all['eventDate'], errors='coerce')
df_all = df_all.dropna(subset=['eventDate'])
df_all['year'] = df_all['eventDate'].dt.year
 
# Vytvorenie GeoDataFrame
geometry = [Point(xy) for xy in zip(df_all['decimalLongitude'], df_all['decimalLatitude'])]
gdf = gpd.GeoDataFrame(df_all, geometry=geometry, crs="EPSG:4326")
 
# Načítanie mapy sveta
world = gpd.read_file(r"C:\Users\Adriana Slúková\Downloads\copy observation visuals\copy observation visuals\ne_110m_admin_0_countries")
 
# Vymedzenie Európy
europe_bounds = {
    'minx': -25,
    'maxx': 45,
    'miny': 34,
    'maxy': 72
}
 
# Farby podľa druhu
colors = {
    'Pernis apivorus': 'green',
    'Gallus gallus': 'red',
    'Martes martes': 'orange'
}
 
# Vykreslenie pre každý rok
for year in sorted(gdf['year'].unique()):
    fig, ax = plt.subplots(figsize=(10, 7))
    world.plot(ax=ax, color='lightgrey', edgecolor='white')
 
    for species, color in colors.items():
        gdf[(gdf['year'] == year) & (gdf['species'] == species)].plot(
            ax=ax,
            color=color,
            markersize=5,
            alpha=0.7,
            label=species
        )
 
    ax.set_xlim(europe_bounds['minx'], europe_bounds['maxx'])
    ax.set_ylim(europe_bounds['miny'], europe_bounds['maxy'])
 
    plt.title(f"Pozorovania zvierat – {year}")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()