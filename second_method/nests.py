import pandas as pd
from sklearn.cluster import DBSCAN
import numpy as np
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import time

# --- Configuration ---
INPUT_CSV = "merged_data.csv"
OUTPUT_CSV = "potential_nests_with_counts.csv" # Updated output file name
ACTIVE_MONTH_START = 3  # March
ACTIVE_MONTH_END = 11 # November
NEST_PROXIMITY_KM = 2.0 # If sightings are within 2km, they might be from the same nest.
MIN_SIGHTINGS_FOR_NEST_CLUSTER = 1 # Minimum sightings to form a potential nest cluster
EARTH_RADIUS_KM = 6371.0 # For converting km to radians for DBSCAN with haversine

# --- Helper Functions ---
def get_country_from_coords(lat, lon, geolocator, retries=3, delay=1):
    """
    Gets the country from latitude and longitude using geopy.
    """
    for attempt in range(retries):
        try:
            location = geolocator.reverse((lat, lon), exactly_one=True, language='en', timeout=10)
            if location and location.raw and 'address' in location.raw and 'country' in location.raw['address']:
                return location.raw['address']['country']
            else:
                return "Unknown" # Or None, if preferred
        except GeocoderTimedOut:
            print(f"Geocoder timed out for ({lat}, {lon}). Retrying ({attempt+1}/{retries})...")
            time.sleep(delay * (attempt + 1))
        except GeocoderUnavailable:
            print(f"Geocoder service unavailable for ({lat}, {lon}). Retrying ({attempt+1}/{retries})...")
            time.sleep(delay * (attempt + 1))
        except Exception as e:
            print(f"An error occurred during geocoding for ({lat}, {lon}): {e}")
            return "Error" # Or None
    return "Failed after retries"

# --- Main Logic ---
def find_potential_nests():
    print(f"Loading data from {INPUT_CSV}...")
    try:
        # Load only necessary columns to save memory
        df = pd.read_csv(INPUT_CSV, usecols=['eventDate', 'decimalLatitude', 'decimalLongitude'])
    except FileNotFoundError:
        print(f"Error: Input file '{INPUT_CSV}' not found.")
        return
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return

    print(f"Initial records: {len(df)}")

    # Drop rows with missing essential data
    df.dropna(subset=['eventDate', 'decimalLatitude', 'decimalLongitude'], inplace=True)
    print(f"Records after dropping NA in essential columns: {len(df)}")

    # Convert eventDate to datetime and extract year/month
    try:
        df['eventDate'] = pd.to_datetime(df['eventDate'], errors='coerce')
        df.dropna(subset=['eventDate'], inplace=True) # Drop rows where date conversion failed
    except Exception as e:
        print(f"Error converting 'eventDate' to datetime: {e}")
        return

    df['year'] = df['eventDate'].dt.year
    df['month'] = df['eventDate'].dt.month

    # Filter for active season (March-November)
    print(f"Filtering for active season (Months: {ACTIVE_MONTH_START}-{ACTIVE_MONTH_END})...")
    df_seasonal = df[df['month'].between(ACTIVE_MONTH_START, ACTIVE_MONTH_END)]
    print(f"Records within active season: {len(df_seasonal)}")

    if df_seasonal.empty:
        print("No data found within the active season. Exiting.")
        return

    # Initialize geolocator
    geolocator = Nominatim(user_agent="hornet_nest_locator_v1.1") # Use a descriptive user agent

    potential_nests_list = []
    
    eps_rad = NEST_PROXIMITY_KM / EARTH_RADIUS_KM

    print(f"\nProcessing data year by year using DBSCAN (eps={NEST_PROXIMITY_KM}km)...")
    for year, year_data in df_seasonal.groupby('year'):
        print(f"\n--- Processing Year: {year} ---")
        if len(year_data) < MIN_SIGHTINGS_FOR_NEST_CLUSTER:
            print(f"Skipping year {year}, not enough sightings ({len(year_data)} < {MIN_SIGHTINGS_FOR_NEST_CLUSTER}).")
            continue
        
        coords = year_data[['decimalLatitude', 'decimalLongitude']].values
        coords_rad = np.radians(coords)
        
        db = DBSCAN(eps=eps_rad, min_samples=MIN_SIGHTINGS_FOR_NEST_CLUSTER, 
                    algorithm='ball_tree', metric='haversine').fit(coords_rad)
        
        labels = db.labels_
        year_data['cluster_label'] = labels
        
        num_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        print(f"Found {num_clusters} potential nest clusters in {year} from {len(year_data)} sightings.")

        for cluster_id in set(labels):
            if cluster_id == -1:
                continue

            cluster_points = year_data[year_data['cluster_label'] == cluster_id]
            
            nest_latitude = cluster_points['decimalLatitude'].mean()
            nest_longitude = cluster_points['decimalLongitude'].mean()
            
            # Get the number of sightings for this cluster
            sightings_count = len(cluster_points) # <--- Get the count here

            print(f"  Cluster {cluster_id}: {sightings_count} sightings. Centroid: ({nest_latitude:.4f}, {nest_longitude:.4f})")

            country = get_country_from_coords(nest_latitude, nest_longitude, geolocator)
            print(f"    Country: {country}")
            
            # --- MODIFICATION HERE ---
            potential_nests_list.append({
                'year': year,
                'nest_latitude': nest_latitude, # Changed 'nest_latitude' to 'decimalLatitude' for consistency
                'nest_longitude': nest_longitude, # Changed 'nest_longitude' to 'decimalLongitude' for consistency
                'country': country,
                'sightings_count': sightings_count # <--- Added the sightings count
            })
            time.sleep(0.35)

    if not potential_nests_list:
        print("\nNo potential nests identified after processing all years.")
        return

    # Create a DataFrame from the list of nests
    nests_df = pd.DataFrame(potential_nests_list)
    
    # Ensure the column order if desired (optional, pandas might pick a different order)
    if not nests_df.empty:
        nests_df = nests_df[['year', 'nest_latitude', 'nest_longitude', 'country', 'sightings_count']]

    print(f"\nTotal potential nests identified: {len(nests_df)}")
    print(f"Saving potential nests to {OUTPUT_CSV}...")
    try:
        nests_df.to_csv(OUTPUT_CSV, index=False)
        print("Done.")
    except Exception as e:
        print(f"Error saving output CSV: {e}")

if __name__ == "__main__":
    find_potential_nests()