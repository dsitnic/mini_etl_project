
# %%
import pandas as pd
import os
import requests
import uuid
import io
from pathlib import Path
from datetime import datetime, timezone

if Path.cwd().name == 'python':
    os.chdir('..')

if Path.cwd().name == 'src':
    os.chdir('..')

BASE_DIR = Path.cwd()
BRONZE_DIR = BASE_DIR / "data" / "bronze"
AIRPORTS_SOURCE_PATH = BASE_DIR / "data" / "source" / "airports.csv"
OUTPUT_FILE = BASE_DIR / "data" / "bronze" / "airport_locations_raw.csv"

source_url = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat"


# %%

run_id = str(uuid.uuid4())
loaded_at = datetime.now(timezone.utc).replace(microsecond=0)
loaded_file_name = AIRPORTS_SOURCE_PATH.name

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print("run_id:", run_id)
print("loaded_at:", loaded_at)
print("loaded_file_name:", loaded_file_name)

# %%
AIRPORT_COLUMNS = [
    "Name",
    "City",
    "Country",
    "IATA",
    "ICAO",
    "Latitude",
    "Longitude",
    "Altitude",
    "Timezone",
    "DST",
    "Tz database timezone",
    "Type",
    "Source",
]

print(f"Starting airport locations ingestion | Run ID: {run_id}")
print(f"Downloading airport data from {source_url}")

try:
    response = requests.get(source_url, headers=HEADERS, stream=True, timeout=30)

    if response.status_code == 200:
        airports_df = pd.read_csv(
            io.BytesIO(response.content),
            header=None,
            names=AIRPORT_COLUMNS,
        )

        airports_df["run_id"] = run_id
        airports_df["load_timestamp"] = loaded_at
        airports_df["source"] = source_url

        airports_df.to_csv(OUTPUT_FILE, index=False)

        print(f"Success! Enriched file saved to {OUTPUT_FILE}")

    else:
        print(f"Failed to download airport data. Status: {response.status_code}")

except Exception as e:
    print(f"Error downloading airport data: {e}")

print("Airport locations bronze ingestion task complete!")

# %%
