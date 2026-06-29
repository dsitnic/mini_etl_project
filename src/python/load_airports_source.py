
# %%
import pandas as pd
import os
from datetime import datetime
import uuid

from pathlib import Path

if Path.cwd().name == 'python':
    os.chdir('..')

if Path.cwd().name == 'src':
    os.chdir('..')

BASE_DIR = Path.cwd()
AIRPORTS_SOURCE_PATH = BASE_DIR / "data" / "source" / "airports.csv"
OUTPUT_FILE = BASE_DIR / "data" / "bronze" / "airport_locations_raw.csv"

# %%

run_id = str(uuid.uuid4())
loaded_at = datetime.now().replace(microsecond=0)
loaded_file_name = AIRPORTS_SOURCE_PATH.name
source_url = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat"

print("run_id:", run_id)
print("loaded_at:", loaded_at)
print("loaded_file_name:", loaded_file_name)

# %%
AIRPORT_COLUMNS = [
    "Airport ID",
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

airports_df = pd.read_csv(
    AIRPORTS_SOURCE_PATH,
    header=None,
    names=AIRPORT_COLUMNS,
)

airports_df.head()

# %%
airports_df["run_id"] = run_id
airports_df["load_timestamp"] = loaded_at
airports_df["source"] = source_url

airports_df.head()
# %%
airports_df.to_csv(OUTPUT_FILE)
# %%
