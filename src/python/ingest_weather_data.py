# IMPORTS

import openmeteo_requests
import pandas as pd
import requests_cache
import uuid
import time

from datetime import datetime, timezone
from pathlib import Path
from retry_requests import retry


# CONSTANTS

PROJECT         = Path.cwd() 
LOCATIONS_FILE  = PROJECT / "data" / "bronze" / "airport_locations_raw.csv" # TODO, replace path with silver data where we only have european airport locations
OUTPUT_DIR      = PROJECT / "data" / "silver"

URL             = "https://archive-api.open-meteo.com/v1/archive"

VARIABLES       = [
    "temperature_2m_mean",
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "wind_speed_10m_max"
]

# HELPER FUNCTIONS

def setup_api_client():
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session   = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session   = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo       = openmeteo_requests.Client(session = retry_session)
    
    return openmeteo


def fetch_weather_batches(openmeteo, locations, batch_size=10):
    all_frames = []
    total_batches = (len(locations) + batch_size - 1) // batch_size

    for batch_num, start in enumerate(range(0, len(locations), batch_size)):
        print(f"batch {batch_num} out of {total_batches}")
        batch = locations.iloc[start:start + batch_size]

        params = {
            "latitude": batch["Latitude"].tolist(),
            "longitude": batch["Longitude"].tolist(),
            "start_date": "2021-01-01",
            "end_date": "2025-12-31",
            "daily": VARIABLES,
        }
        
        # get responses from openmeteo
        # since open-meteo limits the amount of data you can get per minute this try and except block is needed
        tries = 0
        while True:
            try:
                tries += 1
                responses = openmeteo.weather_api(URL, params=params)
                print(f"request succeeded on try {tries}")
                break
            except Exception as e:
                print(f"request failed on try {tries}, waiting 60 seconds: {e}")
                time.sleep(60)


        for response in responses:
            daily = response.Daily()

            dates = pd.date_range(
                start=pd.to_datetime(daily.Time(), unit="s", utc=True),
                periods=len(daily.Variables(0).ValuesAsNumpy()),
                freq="D",
            )

            df = pd.DataFrame({
                "longitude": response.Longitude(),
                "latitude": response.Latitude(),
                "year": dates.year,
                "month": dates.month,
                "day": dates.day,
                "temperature_2m_mean": daily.Variables(0).ValuesAsNumpy(),
                "temperature_2m_max": daily.Variables(1).ValuesAsNumpy(),
                "temperature_2m_min": daily.Variables(2).ValuesAsNumpy(),
                "precipitation_sum": daily.Variables(3).ValuesAsNumpy(),
                "wind_speed_10m_max": daily.Variables(4).ValuesAsNumpy(),
            })

            all_frames.append(df)


    return pd.concat(all_frames, ignore_index=True)


# MAIN

def main():

    # setup api client
    openmeteo = setup_api_client()

    # load file with locations
    locations = pd.read_csv(LOCATIONS_FILE).head(100) # TODO remove .head(100) when production

    # get data from api for each location
    weather_df = fetch_weather_batches(openmeteo, locations, batch_size=10)

    # add metadata
    weather_df["load_timestamp"] = datetime.now(timezone.utc).replace(microsecond=0)
    weather_df["source"] = "https://open-meteo.com"
    weather_df["run_id"] = str(uuid.uuid4())

    #weather_df.to_parquet(OUTPUT_DIR / "weather_daily", index=False, partition_cols=["year"])
    weather_df.to_csv(OUTPUT_DIR / "weather_daily.csv", index=False) # TODO replace with parquet when finished
    print("wrote files to .csv")


main()