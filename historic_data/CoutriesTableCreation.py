import pandas as pd
#1.5

# Load files
estimated_df = pd.read_csv("estimated_hives_summary.csv")
weights_df = pd.read_csv("hive_weighting_table.csv")

# Country bounding boxes for coordinate-to-country mapping
country_bounds = {
    'France': {'lat_min': 41.3, 'lat_max': 51.1, 'lon_min': -5.3, 'lon_max': 9.6},
    'Spain': {'lat_min': 36.0, 'lat_max': 43.8, 'lon_min': -9.3, 'lon_max': 3.3},
    'Portugal': {'lat_min': 36.8, 'lat_max': 42.1, 'lon_min': -9.5, 'lon_max': -6.2},
    'Belgium': {'lat_min': 49.5, 'lat_max': 51.5, 'lon_min': 2.5, 'lon_max': 6.4},
    'Netherlands': {'lat_min': 50.7, 'lat_max': 53.7, 'lon_min': 3.3, 'lon_max': 7.2},
    'Italy': {'lat_min': 36.5, 'lat_max': 47.1, 'lon_min': 6.6, 'lon_max': 18.5},
    'Germany': {'lat_min': 47.2, 'lat_max': 55.1, 'lon_min': 5.9, 'lon_max': 15.0},
    'Switzerland': {'lat_min': 45.8, 'lat_max': 47.8, 'lon_min': 5.9, 'lon_max': 10.5},
    'Luxembourg': {'lat_min': 49.4, 'lat_max': 50.2, 'lon_min': 5.4, 'lon_max': 6.5}
}

# Neighboring countries for fallbacks
neighbors = {
    'Germany': ['France', 'Belgium', 'Netherlands', 'Luxembourg'],
    'Italy': ['France', 'Switzerland'],
    'Switzerland': ['France', 'Germany', 'Italy'],
    'Luxembourg': ['France', 'Belgium', 'Germany'],
}


# Assign country to each row by coordinates
def get_country(lat, lon):
    for country, b in country_bounds.items():
        if b['lat_min'] <= lat <= b['lat_max'] and b['lon_min'] <= lon <= b['lon_max']:
            return country
    return None


estimated_df['country'] = estimated_df.apply(lambda row: get_country(row['centroid_lat'], row['centroid_lon']), axis=1)
estimated_df = estimated_df.dropna(subset=['country'])

# Group by year + country to get hive count
estimated_counts = estimated_df.groupby(['year', 'country']).size().reset_index(
    name='estimated_hives_without_weighting')

# Merge with pre-computed weights
merged = pd.merge(estimated_counts, weights_df, on=['year', 'country'], how='left')

# Calculate fallback values
country_avg = weights_df.groupby('country')['final_weight'].mean().to_dict()
year_avg = weights_df.groupby('year')['final_weight'].mean().to_dict()
global_avg = weights_df['final_weight'].mean()
global_min = weights_df['final_weight'].min()
global_max = weights_df['final_weight'].max()


# Clamp helper
def clamp(value, min_val, max_val):
    return max(min_val, min(value, max_val))


# Assign improved weight
def assign_weight(row):
    if pd.notna(row['final_weight']):
        # Clamp to actual observed max per policy
        return clamp(row['final_weight'], global_min, global_max)

    country = row['country']
    year = row['year']

    # Known country → use country average, clamped
    if country in country_avg:
        return clamp(country_avg[country], global_min, global_max)

    # Try nearby neighbors around similar years
    nearby_weights = []
    if country in neighbors:
        for neighbor in neighbors[country]:
            near_rows = weights_df[(weights_df['country'] == neighbor) &
                                   (weights_df['year'].between(year - 1, year + 1))]
            nearby_weights.extend(near_rows['final_weight'].dropna().tolist())
        if nearby_weights:
            avg_near = sum(nearby_weights) / len(nearby_weights)
            return clamp(avg_near, 0.1, 10.0)  # clamp wider for inferred neighbors

    # Try year average
    if year in year_avg:
        return clamp(year_avg[year], 0.1, 10.0)

    # Final fallback
    return clamp(global_avg, 0.1, 10.0)


# Apply logic to assign weight
merged['final_weight'] = merged.apply(assign_weight, axis=1)

# Apply weighted hive estimate
merged['estimated_hives_with_weighting'] = (
        merged['estimated_hives_without_weighting'] * merged['final_weight']
).round().astype(int)

# Prepare final output including the weight
output = merged[
    ['year', 'country', 'estimated_hives_without_weighting', 'final_weight', 'estimated_hives_with_weighting']]
output = output.sort_values(by=['year', 'country'])

# Save result
output.to_csv("estimated_hives_weighted_output_clamped.csv", index=False)
print("✅ Saved: 'estimated_hives_weighted_output_clamped.csv'")
print(output)
