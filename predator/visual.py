import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib as mpl
 
# === KONFIGURÁCIA ===
forecast_path = "output/forecast_with_predation_adjustment.csv"
shapefile_path = "shapefile_extracted/ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp"
output_folder = "output/hornet_forecast_visuals5"
os.makedirs(output_folder, exist_ok=True)
 
# === NAČÍTANIE DÁT ===
df = pd.read_csv(forecast_path)
gdf_countries = gpd.read_file(shapefile_path)[["ADMIN", "geometry"]].rename(columns={"ADMIN": "country"})
 
# === PRÍPRAVA GEOMETRIE ===
df["country"] = df["country"].str.strip()
gdf_countries["country"] = gdf_countries["country"].str.strip()
 
europe = gdf_countries[gdf_countries["country"].isin(df["country"].unique())]
europe = europe.explode(index_parts=True).reset_index(drop=True)
 
# Vyber len najväčšiu časť pre viacdielne krajiny
europe["area"] = europe.geometry.area
europe = europe.sort_values(by=["country", "area"], ascending=[True, False])
europe = europe.drop_duplicates(subset="country", keep="first")
 
# === DEFINUJ FIXNÚ FAREBNÚ ŠKÁLU (ZJEDNOTENÁ S TVOJOU PÔVODNOU MAPOU) ===
vmin, vmax = 0.0, 0.015  # 👈 rovnaké ako na tvojej pôvodnej mape
cmap = plt.cm.OrRd
norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
 
# === GENERUJ MAPU PRE KAŽDÝ ROK ===
for year in sorted(df["year"].unique()):
    df_year = df[df["year"] == year]
    merged = europe.merge(df_year, on="country", how="left")
 
    fig, ax = plt.subplots(figsize=(11, 9))
 
    # Základné hranice
    merged.boundary.plot(ax=ax, color="black", linewidth=0.4)
 
    # Výplň farby podľa adjusted_hive_density
    merged.plot(
        ax=ax,
        column="adjusted_hive_density",
        cmap=cmap,
        norm=norm,
        linewidth=0.5,
        edgecolor="0.7",
        missing_kwds={"color": "lightgrey", "label": "No data"}
    )
 
    # FIXNÝ COLORBAR
    sm = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
    sm._A = []
    cbar = fig.colorbar(sm, ax=ax, shrink=0.7)
    cbar.set_label("Adjusted Hive Density (0.00 – 0.015)", fontsize=10)
 
    # TITULOK + SAVE
    ax.set_title(f"Vespa velutina Hive Density (with Predators) – {year}", fontsize=14)
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(f"{output_folder}/hornet_density_{year}.png", dpi=200)
    plt.close()
 
print(f"✅ Hotovo – všetky mapy so zjednotenou farebnou mierkou uložené v: {output_folder}")