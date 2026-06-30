# IMPORTS

import openmeteo_requests
import pandas as pd
import requests_cache
import uuid
import time

from datetime import datetime, timezone, timedelta
from pathlib import Path
from retry_requests import retry
from typing import Any


# CONSTANTS

PROJECT         = Path(__file__).resolve().parents[2]
LOCATIONS_FILE  = PROJECT / "data" / "bronze" / "airport_top250_locations_joined.csv"
OUTPUT_DIR      = PROJECT / "data" / "silver" 

SOURCE          = "https://open-meteo.com"
URL             = "https://archive-api.open-meteo.com/v1/archive"
START_DATE      = "2021-01-01"
END_DATE        = "2025-12-31"
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


def get_wait_seconds(message: str) -> int:
    '''
    If you exceed the open-api minute/hourly or daily limit,
    it will be reset at the start of the next minute/hour/day. 
    This function calculates the seconds to wait untill the rate is reset.
    '''

    now = datetime.now(timezone.utc)
    extra_delay = 5 # extra delay to avoid retrying too early due to time differences

    if "tomorrow" in message:
        next_day = (now + timedelta(days=1)).replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        return int((next_day - now).total_seconds() + extra_delay * 100)

    if "next hour" in message:
        next_hour = (now + timedelta(hours=1)).replace(
            minute=0,
            second=0,
            microsecond=0,
        )
        return int((next_hour - now).total_seconds() + extra_delay * 10)

    if "one minute" in message:
        next_minute = (now + timedelta(minutes=1)).replace(
            second=0,
            microsecond=0,
        )
        return int((next_minute - now).total_seconds() + extra_delay)

    return 60


def request_with_retry(openmeteo: openmeteo_requests.Client, params: dict[str, Any]) -> list[Any]:
    """
    Request data with infinite retries on rate limit exceptions.
    Waiting time between retries is calculated based on which rate limit is exceeded. 
    This is necessary because open-meteo limits the amount of data one can fetch per minute, hour and day.
    """


    while True:
        try:
            responses = openmeteo.weather_api(URL, params=params)
            return responses
        except Exception as e:
            message = str(e).lower()

            if "request limit exceeded" in message:
                wait_seconds = get_wait_seconds(message)
                current_time = datetime.now(timezone.utc).replace(microsecond=0)

                print(f"[{current_time}] request failed, waiting {wait_seconds} seconds: {e}")
                time.sleep(wait_seconds)
            else:
                raise


def response_to_dataframe(response: Any, airport_code: str) -> pd.DataFrame:
    """Convert data from the response objects returned by open-meteo API to a DataFrame."""

    daily = response.Daily()

    dates = pd.date_range(
        start   = pd.to_datetime(daily.Time(), unit="s", utc=True),
        periods = len(daily.Variables(0).ValuesAsNumpy()),
        freq    = "D",
    )

    return pd.DataFrame({
        "airport_code":         airport_code,
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

    for batch_num, start in enumerate(range(0, len(locations), batch_size), start=1):
        elapsed_seconds = int(time.time() - started_at)

        print(
            f"batch {batch_num} out of {total_batches} "
            f"| elapsed {elapsed_seconds // 60}m {elapsed_seconds % 60}s"
        )

        batch = locations.iloc[start:start + batch_size]

        # parameters to pass to the open-meteo api for which data to get
        params = {
            "latitude":     batch["Latitude"],
            "longitude":    batch["Longitude"],
            "start_date":   START_DATE,
            "end_date":     END_DATE,
            "daily":        VARIABLES,
        }
        
        # get responses from openmeteo
        responses = request_with_retry(openmeteo, params)

        for response, (_, airport_row) in zip(responses, batch.iterrows()):
            all_frames.append(response_to_dataframe(response, airport_row["airport_code"]))

    return pd.concat(all_frames, ignore_index=True)


# MAIN FUNCTION

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
    weather_df.to_csv(OUTPUT_DIR / "stg_weather_daily.csv", index=False)


if __name__ == "__main__":
    main()