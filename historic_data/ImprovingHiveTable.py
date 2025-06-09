import pandas as pd
#1.2.2 - to be continued improving, output not actually changed anything

# Load hive summary table
hive_table = 'estimated_hives_summary.csv'
hives_df = pd.read_csv(hive_table)

# 1. Filter and print hives with radius > 1.9 km
wide_hives = hives_df[hives_df['radius_km'] > 1.9]

print("\n🔎 Hives with spread radius > 1.9 km:\n")
print(wide_hives[['hive_id', 'year', 'n_observations', 'centroid_lat', 'centroid_lon', 'radius_km', 'min_date', 'max_date']])

# 2. Calculate average number of observations for hives with radius < 2 km
avg_obs_small_radius = hives_df[hives_df['radius_km'] < 2]['n_observations'].mean()
print(f"\n📊 Average observations for hives with radius < 2 km: {avg_obs_small_radius:.2f}")

# 3. Identify large-radius hives that have unusually high number of observations
suspect_hives = hives_df[
    (hives_df['radius_km'] >= 2) &
    (hives_df['n_observations'] > avg_obs_small_radius)
]

print("\n🚩 Suspected overclustered hives (radius >= 2 km AND above-average observations):\n")
print(suspect_hives[['hive_id', 'year', 'n_observations', 'centroid_lat', 'centroid_lon', 'radius_km']])
