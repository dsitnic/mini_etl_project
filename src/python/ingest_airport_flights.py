import os
import requests
import pandas as pd
import io
import uuid
from datetime import datetime, timezone

# Setup the Bronze directory
BRONZE_DIR = "data/bronze"
os.makedirs(BRONZE_DIR, exist_ok=True)

# Define the years to download
years_to_download = [2021, 2022, 2023, 2024, 2025]

run_id = uuid.uuid4().hex
load_timestamp = datetime.now(timezone.utc).replace(microsecond=0)

# Standard headers (look like a browser, even without a firewall)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://ansperformance.eu/"
}

print(f"Starting Ingestion Pipeline | Run ID: {run_id}")

for year in years_to_download:
    # UPDATE: The new unblocked URL pattern
    url = f"https://www.eurocontrol.int/performance/data/download/csv/all_pre_departure_delays_{year}.csv"
    
    # UPDATE: Saving directly to CSV
    final_csv_path = os.path.join(BRONZE_DIR, f"airport_flights_{year}.csv")
    
    print(f"Downloading data for {year}...")
    
    try:
        # 3. Stream the download
        response = requests.get(url, headers=HEADERS, stream=True)
        
        if response.status_code == 200:
            # Read the raw web bytes directly into Pandas from memory
            df = pd.read_csv(io.BytesIO(response.content))
            
            # Add the metadata columns using Pandas before saving
            df['load_timestamp'] = load_timestamp
            df['source'] = url
            df['run_id'] = run_id

            # Save the enriched data straight into the Bronze folder
            # index=False prevents Pandas from creating an unneeded row-index column
            df.to_csv(final_csv_path, index=False)
            print(f"Success! Enriched file saved to {final_csv_path}")

        else:
            print(f"Failed to download {year}. Status: {response.status_code}")
            
    except Exception as e:
        print(f"Error downloading {year}: {e}")

print("\nBronze ingestion task complete!")