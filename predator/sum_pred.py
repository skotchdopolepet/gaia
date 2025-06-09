from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import geopandas as gpd
import zipfile
import os
from shapely.geometry import Point
 
# === FILE PATHS ===
gallus_file = "Gallus_2024-2025 (1).csv"
martes_file = "Martes_2024-2025 (1).csv"
pernis_file = "Pernis_2024-2025 (1).csv"
shapefile_zip = "ne_110m_admin_0_countries.zip"
shapefile_dir = "shapefile_extracted"
shapefile_path = f"{shapefile_dir}/ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp"
 
# === SHAPEFILE ===
if not os.path.exists(shapefile_path):
    with zipfile.ZipFile(shapefile_zip, 'r') as zip_ref:
        zip_ref.extractall(shapefile_dir)
 
gdf_countries = gpd.read_file(shapefile_path)[["ADMIN", "geometry"]].rename(columns={"ADMIN": "country"})
gdf_countries = gdf_countries.to_crs("EPSG:4326")
 
# === LOAD 2024 PREDATORS ===
def load_predator(path, name):
    df = pd.read_csv(path)
    df["eventDate"] = pd.to_datetime(df["eventDate"], errors="coerce")
    df = df[df["eventDate"].dt.year == 2024]
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df["decimalLongitude"], df["decimalLatitude"]), crs="EPSG:4326")
    gdf["predator"] = name
    return gdf
 
gdf_gallus = load_predator(gallus_file, "Gallus")
gdf_martes = load_predator(martes_file, "Martes")
gdf_pernis = load_predator(pernis_file, "Pernis")
 
# === COUNT BY COUNTRY ===
def count_by_country(gdf, countries, name):
    joined = gpd.sjoin(gdf, countries, predicate="within", how="inner")
    return joined.groupby("country").size().reset_index(name=name)
 
df_gallus = count_by_country(gdf_gallus, gdf_countries, "Gallus")
df_martes = count_by_country(gdf_martes, gdf_countries, "Martes")
df_pernis = count_by_country(gdf_pernis, gdf_countries, "Pernis")
 
# === MERGE + CALCULATE TOTAL ===
df = df_gallus.merge(df_martes, on="country", how="outer") \
              .merge(df_pernis, on="country", how="outer")
df.fillna(0, inplace=True)
 
# === SUM ALL PREDATORS ===
df["predator_total"] = df["Gallus"] + df["Martes"] + df["Pernis"]
 
# === SCALE TO 0.0 – 0.5 ===
scaler = MinMaxScaler(feature_range=(0.0, 0.5))  # ⚠️ nastav max dopad na 0.5
df["predation_score"] = scaler.fit_transform(df[["predator_total"]])
 
# === EXPORT ===
os.makedirs("output", exist_ok=True)
df.to_csv("output/predation_score_2024_scaled.csv", index=False)
 
print("✅ Uložené do: output/predation_score_2024_scaled.csv")