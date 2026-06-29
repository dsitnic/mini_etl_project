# IMPORTS

import openmeteo_requests
import pandas as pd
import requests_cache
import uuid
import time

from datetime import datetime, timezone
from pathlib import Path
from retry_requests import retry
from typing import Any


# CONSTANTS

PROJECT         = Path.cwd() 
LOCATIONS_FILE  = PROJECT / "data" / "silver" / "airport_locations_raw_europe.csv" # TODO, replace with actualy silver data
OUTPUT_DIR      = PROJECT / "data" / "silver"


URL             = "https://archive-api.open-meteo.com/v1/archive"
START_DATE      = "2021-01-01"
END_DATE        = "2025-12-31"
SOURCE          = "https://open-meteo.com"
VARIABLES       = [
    "temperature_2m_mean",
    "precipitation_sum",
    "wind_speed_10m_max"
]


# HELPER FUNCTIONS

def setup_api_client() -> openmeteo_requests.Client:
    """Create API client."""

    cache_session   = requests_cache.CachedSession(".cache", expire_after=3600)
    retry_session   = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo       = openmeteo_requests.Client(session=retry_session)

    return openmeteo


def request_with_retry(openmeteo: openmeteo_requests.Client, params: dict[str, Any]) -> list[Any]:
    """
    Request data with infinite retries on failure. 
    This is necessary because open-meteo limits the amount of data one can fetch per minute and per hour.
    """

    tries = 0

    while True:
        try:
            tries += 1
            responses = openmeteo.weather_api(URL, params=params)
            print(f"request succeeded on try {tries}")
            return responses
        except Exception as e:
            print(f"request failed on try {tries}, waiting 60 seconds: {e}")
            time.sleep(60)


def response_to_dataframe(response: Any) -> pd.DataFrame:
    """Convert data from response objects to DataFrame."""

    daily = response.Daily()

    dates = pd.date_range(
        start   = pd.to_datetime(daily.Time(), unit="s", utc=True),
        periods = len(daily.Variables(0).ValuesAsNumpy()),
        freq    = "D",
    )

    return pd.DataFrame({
        "longitude":            response.Longitude(),
        "latitude":             response.Latitude(),
        "year":                 dates.year,
        "month":                dates.month,
        "day":                  dates.day,
        "temperature_2m_mean":  daily.Variables(0).ValuesAsNumpy(),
        "precipitation_sum":    daily.Variables(1).ValuesAsNumpy(),
        "wind_speed_10m_max":   daily.Variables(2).ValuesAsNumpy(),
    })



def fetch_weather_data_batches(
    openmeteo: openmeteo_requests.Client,
    locations: pd.DataFrame,
    batch_size: int = 10,
) -> pd.DataFrame:
    """Fetch weather data from open-meteo API in batches."""

    all_frames = []
    total_batches = (len(locations) + batch_size - 1) // batch_size
    started_at = time.time()

    for batch_num, start in enumerate(range(0, len(locations), batch_size)):
        elapsed_seconds = int(time.time() - started_at)

        print(
            f"batch {batch_num} out of {total_batches} "
            f"| elapsed {elapsed_seconds // 60}m {elapsed_seconds % 60}s"
        )

        batch = locations.iloc[start:start + batch_size]

        params = {
            "latitude":     batch["Latitude"],
            "longitude":    batch["Longitude"],
            "start_date":   START_DATE,
            "end_date":     END_DATE,
            "daily":        VARIABLES,
        }
        
        # get responses from openmeteo
        responses = request_with_retry(openmeteo, params)

        for response in responses:
            all_frames.append(response_to_dataframe(response))

    return pd.concat(all_frames, ignore_index=True)


# MAIN SCRIPT

def main():

    # setup api client
    openmeteo = setup_api_client()

    # load file with locations data containing latitudes and longitudes
    locations = pd.read_csv(LOCATIONS_FILE)

    # get wether data from open-meteo api in batches
    weather_df = fetch_weather_data_batches(openmeteo, locations, batch_size=10)

    # add metadata
    weather_df["load_timestamp"]    = datetime.now(timezone.utc).replace(microsecond=0)
    weather_df["source"]            = SOURCE
    weather_df["run_id"]            = str(uuid.uuid4())

    # save data to parquet and partition by year to keep filesizes down
    weather_df.to_parquet(OUTPUT_DIR / "weather_daily", index=False, partition_cols=["year"])


main()