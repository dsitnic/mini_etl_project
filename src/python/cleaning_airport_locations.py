# %%
import pandas as pd
import os
from datetime import datetime
from pathlib import Path

if Path.cwd().name == 'python':
    os.chdir('..')

if Path.cwd().name == 'src':
    os.chdir('..')

BASE_DIR = Path.cwd()
AIRPORTS_LOCATION_RAW_FILE = BASE_DIR / "data" / "bronze" / "airport_locations_raw.csv"
OUTPUT_FILE = BASE_DIR / "data" / "silver" / "stg_airport_geography.csv"
# %%
airport_locations = pd.read_csv(AIRPORTS_LOCATION_RAW_FILE)

airport_locations.head()
# %%
airport_locations.info()
airport_locations.columns
# %% Change columns name to snake case and remove the source column from the original source dataset
# Type column is also removed since we only have airport as type in our dataset
airport_locations_std = airport_locations.copy()

airport_locations_std = airport_locations_std.rename(columns={
    "Tz database timezone" : "tz_database_timezone",
    "Source" : "source_delete",
    "Name" : "airport_name"
})

airport_locations_std.columns = (
    airport_locations_std.columns
    .str.strip()
    .str.lower()
)

airport_locations_std.columns

airport_locations_std = airport_locations_std[
    [
        'airport_name', 'city', 'country', 'iata', 'icao', 'latitude', 'longitude',
        'altitude', 'timezone', 'dst', 'tz_database_timezone',
        'run_id', 'load_timestamp', 'source'
    ]
]

airport_locations_std.head()


# %% Basic cleaning of the different columns and update type
airport_locations_std["airport_name_clean"] = (
    airport_locations_std["airport_name"]
    .astype("string")
    .str.strip()
    .str.title()
    .replace("", pd.NA)
)

airport_locations_std["city_clean"] = (
    airport_locations_std["city"]
    .astype("string")
    .str.strip()
    .str.title()
    .replace("", pd.NA)
)

airport_locations_std["country_clean"] = (
    airport_locations_std["country"]
    .astype("string")
    .str.strip()
    .str.title()
    .replace("", pd.NA)
)

airport_locations_std["iata_clean"] = (
    airport_locations_std["iata"]
    .astype("string")
    .str.strip()
    .str.upper()
    .replace("", pd.NA)
)

airport_locations_std["icao_clean"] = (
    airport_locations_std["icao"]
    .astype("string")
    .str.strip()
    .str.upper()
    .replace("", pd.NA)
)

airport_locations_std["dst_clean"] = (
    airport_locations_std["dst"]
    .astype("string")
    .str.strip()
    .str.upper()
    .replace("", pd.NA)
)

airport_locations_std["tz_database_timezone_clean"] = (
    airport_locations_std["tz_database_timezone"]
    .astype("string")
    .str.strip()
    .str.title()
    .replace("", pd.NA)
)

airport_locations_std["latitude_clean"] = pd.to_numeric(airport_locations_std["latitude"], errors="coerce")

airport_locations_std["longitude_clean"] = pd.to_numeric(airport_locations_std["longitude"], errors="coerce")

airport_locations_std["altitude_clean"] = pd.to_numeric(airport_locations_std["altitude"], errors="coerce")

airport_locations_std["timezone_clean"] = pd.to_numeric(airport_locations_std["timezone"], errors="coerce")

airport_locations_std["latitude_clean"] = pd.to_numeric(airport_locations_std["latitude"], errors="coerce")

airport_locations_std["load_timestamp_clean"] = pd.to_datetime(airport_locations_std["load_timestamp"], errors="coerce")

#airport_locations_std.head()
# %%
#airport_locations_std.info()


# %%
checks = {
    "missing_iata" : airport_locations_std["iata_clean"].isna().sum(),
    "missing_latitude" : airport_locations_std["latitude_clean"].isna().sum(),
    "missing_longitide" : airport_locations_std["longitude_clean"].isna().sum(),
     "invalid_latitude": (~airport_locations_std["latitude_clean"].between(-90, 90)).sum(),
    "invalid_longitude": (~airport_locations_std["longitude_clean"].between(-180, 180)).sum(),
}

checks
# %%
airport_locations_clean = airport_locations_std.copy()

airport_locations_clean = airport_locations_clean[
    [
        'airport_name_clean',
        'city_clean',
        'country_clean',
        'iata_clean', 
        'icao_clean',
        'latitude_clean', 
        'longitude_clean',
        'altitude_clean',
        'timezone_clean',
        'dst_clean', 
        'tz_database_timezone_clean',
        'run_id',
        'load_timestamp_clean',
        'source'
    ]
]

airport_locations_clean.head()

# %%
airport_locations_clean.to_csv(OUTPUT_FILE, index=False)
# %%
