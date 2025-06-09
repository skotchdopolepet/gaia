import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from geopy.distance import great_circle
from datetime import datetime
#1.2.1

# Load your data
file_main = 'GAIA_combined/combined_main.csv'
file_old = 'GAIA_combined/combined_old format_to_2009.csv'

df_main = pd.read_csv(file_main)
df_old = pd.read_csv(file_old)

# Combine datasets
df = pd.concat([df_main, df_old], ignore_index=True)

# Parse dates
df['eventDate'] = pd.to_datetime(df['eventDate'], errors='coerce')

# Drop rows missing critical info
df = df.dropna(subset=['eventDate', 'decimalLatitude', 'decimalLongitude'])

# Extract year and month
df['year'] = df['eventDate'].dt.year
df['month'] = df['eventDate'].dt.month

# Only include active Vespa velutina season (March–November)
df = df[df['month'].between(3, 11)]

# Clustering function
def cluster_hives(df, eps_km=2, min_samples=1):
    hive_records = []
    kms_per_radian = 6371.0088  # Earth radius

    for year in sorted(df['year'].unique()):
        df_year = df[df['year'] == year].copy()

        # Coordinates in radians for haversine
        coords = df_year[['decimalLatitude', 'decimalLongitude']].to_numpy()
        coords_rad = np.radians(coords)

        # DBSCAN spatial clustering
        db = DBSCAN(eps=eps_km / kms_per_radian, min_samples=min_samples, algorithm='ball_tree', metric='haversine')
        labels = db.fit_predict(coords_rad)

        df_year['cluster'] = labels

        for cluster_id in sorted(df_year['cluster'].unique()):
            if cluster_id == -1:
                continue  # Ignore noise points

            cluster_df = df_year[df_year['cluster'] == cluster_id]

            centroid_lat = cluster_df['decimalLatitude'].mean()
            centroid_lon = cluster_df['decimalLongitude'].mean()
            min_date = cluster_df['eventDate'].min().date()
            max_date = cluster_df['eventDate'].max().date()
            n_obs = len(cluster_df)

            # Max distance from centroid
            radius = max(
                great_circle((centroid_lat, centroid_lon), (row['decimalLatitude'], row['decimalLongitude'])).km
                for _, row in cluster_df.iterrows()
            )

            hive_records.append({
                'hive_id': f'HIVE_{year}_{cluster_id}',
                'year': year,
                'season_range': f'{year}-03 to {year}-11',
                'n_observations': n_obs,
                'centroid_lat': round(centroid_lat, 5),
                'centroid_lon': round(centroid_lon, 5),
                'min_date': min_date,
                'max_date': max_date,
                'radius_km': round(radius, 2),
                'notes': 'only one observation' if n_obs == 1 else ''
            })

    return pd.DataFrame(hive_records)

# Run clustering and export results
hives_df = cluster_hives(df)
hives_df.to_csv('estimated_hives_summary.csv', index=False)

print("✅ Hive estimation complete. Output saved as 'estimated_hives_summary.csv'")
