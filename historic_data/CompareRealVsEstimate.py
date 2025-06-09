import pandas as pd
#1.4

# Step 1: Load estimated hives
hives = pd.read_csv("estimated_hives_summary.csv")

# Step 2: Assign countries using lat/lon bounding boxes
country_bounds = {
    'France':      {'lat_min': 41.3, 'lat_max': 51.1, 'lon_min': -5.3, 'lon_max': 9.6},
    'Spain':       {'lat_min': 36.0, 'lat_max': 43.8, 'lon_min': -9.3, 'lon_max': 3.3},
    'Portugal':    {'lat_min': 36.8, 'lat_max': 42.1, 'lon_min': -9.5, 'lon_max': -6.2},
    'Belgium':     {'lat_min': 49.5, 'lat_max': 51.5, 'lon_min': 2.5, 'lon_max': 6.4},
    'Netherlands': {'lat_min': 50.7, 'lat_max': 53.7, 'lon_min': 3.3, 'lon_max': 7.2}
}

def get_country(lat, lon):
    for country, bounds in country_bounds.items():
        if bounds['lat_min'] <= lat <= bounds['lat_max'] and bounds['lon_min'] <= lon <= bounds['lon_max']:
            return country
    return None

hives['country'] = hives.apply(lambda row: get_country(row['centroid_lat'], row['centroid_lon']), axis=1)
hives = hives.dropna(subset=['country'])

# Step 3: Count estimated hives by year and country
estimated_summary = hives.groupby(['year', 'country']).size().reset_index(name='estimated_hives')

# Step 4: Known nest data (manually input)
known_data = [
    (2004, 'France', 2), (2005, 'France', 4), (2006, 'France', 257),
    (2007, 'France', 1670), (2008, 'France', 1233), (2009, 'France', 1636),
    (2010, 'Spain', 2), (2011, 'Portugal', 1), (2011, 'Belgium', 1),
    (2012, 'Spain', 2), (2013, 'Spain', 17), (2014, 'Spain', 769),
    (2015, 'Spain', 5022), (2016, 'Spain', 10642), (2016, 'Belgium', 1),
    (2017, 'Belgium', 4), (2017, 'Netherlands', 1), (2018, 'France', 2353),
    (2018, 'Spain', 30000), (2018, 'Belgium', 13), (2018, 'Netherlands', 3),
    (2019, 'Netherlands', 0), (2021, 'France', 1983), (2021, 'Netherlands', 3),
    (2022, 'France', 3833), (2023, 'Belgium', 2000), (2023, 'Netherlands', 500),
]
known_df = pd.DataFrame(known_data, columns=['year', 'country', 'known_nests'])

# Step 5: Merge known + estimated counts
merged = pd.merge(known_df, estimated_summary, on=['year', 'country'], how='left')
merged['estimated_hives'] = merged['estimated_hives'].fillna(0).astype(int)

# Step 6: Calculate raw weight
merged['weight'] = merged['known_nests']/merged['estimated_hives']
merged.replace([float('inf'), -float('inf')], pd.NA, inplace=True)

# Step 7: Fill missing weights with fallback logic
country_avg = merged.groupby('country')['weight'].mean().to_dict()
year_avg = merged.groupby('year')['weight'].mean().to_dict()
global_avg = merged['weight'].mean()

def fill_weight(row):
    if pd.notna(row['weight']):
        return row['weight']
    if pd.notna(country_avg.get(row['country'])):
        return country_avg[row['country']]
    if pd.notna(year_avg.get(row['year'])):
        return year_avg[row['year']]
    return global_avg

merged['final_weight'] = merged.apply(fill_weight, axis=1)

# Step 8: Save both outputs
merged.to_csv("comparison_known_vs_estimated_hives.csv", index=False)
merged[['year', 'country', 'final_weight']].to_csv("hive_weighting_table.csv", index=False)

# Step 9: Print summary
print("✅ Comparison table saved as 'comparison_known_vs_estimated_hives.csv'")
print("✅ Weight table saved as 'hive_weighting_table.csv'")
print("\n📊 Final weighting table:\n")
print(merged[['year', 'country', 'final_weight']].sort_values(by=['year', 'country']))
