import requests
import pandas as pd
import json
import os
from datetime import datetime
import time

# Movebank API base URL
MOVEBANK_API_BASE = "https://www.movebank.org/movebank/service/direct-read"

def test_api_connection():
    """Test if we can connect to the Movebank API."""
    print("Testing connection to Movebank API...")
    
    # Try accessing the studies endpoint
    try:
        response = requests.get(f"{MOVEBANK_API_BASE}/json/study")
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            print("Successfully connected to the API!")
            return True
        else:
            print(f"Connection failed. Response: {response.text[:500]}...")
            return False
    except Exception as e:
        print(f"Error connecting to API: {e}")
        return False

def get_all_studies():
    """Get a list of all studies from Movebank."""
    print("Retrieving all studies...")
    
    try:
        # According to the documentation, this endpoint should list all studies
        response = requests.get(f"{MOVEBANK_API_BASE}/json/study")
        
        if response.status_code == 200:
            studies = response.json()
            print(f"Successfully retrieved {len(studies)} studies")
            return studies
        else:
            print(f"Failed to retrieve studies. Status code: {response.status_code}")
            print(f"Response: {response.text[:500]}...")
            return []
    except Exception as e:
        print(f"Error retrieving studies: {e}")
        return []

def search_asian_hornet_studies(studies):
    """Filter studies related to Asian hornets."""
    search_terms = ["asian hornet", "vespa velutina", "vespa mandarinia", "hornet", "vespa"]
    
    hornet_studies = []
    for study in studies:
        study_str = json.dumps(study).lower()
        if any(term in study_str for term in search_terms):
            hornet_studies.append(study)
    
    print(f"Found {len(hornet_studies)} potentially relevant studies")
    return hornet_studies

def get_study_details(study_id):
    """Get detailed information about a specific study."""
    print(f"Getting details for study {study_id}...")
    
    try:
        response = requests.get(f"{MOVEBANK_API_BASE}/json/study?study_id={study_id}")
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get study details. Status code: {response.status_code}")
            print(f"Response: {response.text[:500]}...")
            return None
    except Exception as e:
        print(f"Error getting study details: {e}")
        return None

def download_study_data(study_id):
    """Download movement data for a specific study."""
    print(f"Downloading data for study {study_id}...")
    
    # First try without license acceptance
    try:
        url = f"{MOVEBANK_API_BASE}/csv/event?study_id={study_id}"
        response = requests.get(url)
        
        if response.status_code == 200:
            # Convert to DataFrame
            data = pd.read_csv(pd.io.common.StringIO(response.text))
            print(f"Downloaded {len(data)} data points")
            return data
        elif response.status_code == 403:
            print("License acceptance required. Trying with license terms...")
            
            # Try with license acceptance
            url_with_license = f"{MOVEBANK_API_BASE}/csv/event?study_id={study_id}&license-md5=null&i_agree_to_terms_of_use=true"
            license_response = requests.get(url_with_license)
            
            if license_response.status_code == 200:
                data = pd.read_csv(pd.io.common.StringIO(license_response.text))
                print(f"Downloaded {len(data)} data points")
                return data
            else:
                print(f"Failed to download with license acceptance. Status code: {license_response.status_code}")
                print(f"Response: {license_response.text[:500]}...")
                return None
        else:
            print(f"Failed to download data. Status code: {response.status_code}")
            print(f"Response: {response.text[:500]}...")
            return None
    except Exception as e:
        print(f"Error downloading data: {e}")
        return None

def main():
    """Main function to execute the workflow."""
    # Step 1: Test API connection
    if not test_api_connection():
        print("\nCannot connect to Movebank API. There might be several reasons:")
        print("1. The API structure might have changed")
        print("2. The API might be temporarily unavailable")
        print("3. Your network might be blocking the connection")
        print("\nLet's try accessing data through the web interface instead:")
        print("1. Visit: https://www.movebank.org/cms/webapp")
        print("2. Search for 'Asian hornet', 'vespa velutina', or 'vespa mandarinia'")
        print("3. Download the data manually")
        return
    
    # Step 2: Get all studies
    all_studies = get_all_studies()
    
    if not all_studies:
        print("Could not retrieve studies list.")
        return
    
    # Step 3: Filter for Asian hornet studies
    hornet_studies = search_asian_hornet_studies(all_studies)
    
    if not hornet_studies:
        print("No Asian hornet studies found.")
        return
    
    # Step 4: Display available studies
    print("\nAvailable studies that might contain Asian hornet data:")
    for i, study in enumerate(hornet_studies):
        print(f"{i+1}. {study.get('name', 'Unnamed study')} (ID: {study.get('id')})")
    
    # Step 5: Let user select a study
    try:
        selected_idx = int(input("\nEnter the number of the study you want to explore (or 0 to exit): ")) - 1
        
        if selected_idx == -1:
            print("Exiting program.")
            return
            
        if 0 <= selected_idx < len(hornet_studies):
            selected_study = hornet_studies[selected_idx]
            study_id = selected_study.get('id')
            print(f"\nSelected study: {selected_study.get('name')} (ID: {study_id})")
            
            # Step 6: Get study details
            study_details = get_study_details(study_id)
            
            if study_details:
                print("\nStudy details:")
                details = study_details[0] if isinstance(study_details, list) else study_details
                print(f"Name: {details.get('name', 'N/A')}")
                if 'principal_investigator_name' in details:
                    print(f"Principal investigator: {details.get('principal_investigator_name')}")
                if 'study_objective' in details:
                    print(f"Study objective: {details.get('study_objective')}")
            
            # Step 7: Download data
            data = download_study_data(study_id)
            
            if data is not None and not data.empty:
                # Save to CSV
                filename = f"asian_hornet_data_{study_id}_{datetime.now().strftime('%Y%m%d')}.csv"
                data.to_csv(filename, index=False)
                print(f"\nData saved to {filename}")
                
                # Display data summary
                print("\nData summary:")
                print(f"Number of records: {len(data)}")
                print(f"Columns available: {', '.join(data.columns)}")
                
                # Show preview
                print("\nData preview:")
                print(data.head())
            else:
                print("\nNo data retrieved. This study might be private or require authentication.")
                print("Consider using the web interface to access this data.")
        else:
            print("Invalid selection.")
    except ValueError:
        print("Please enter a valid number.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()