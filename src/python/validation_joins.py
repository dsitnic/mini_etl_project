import pandas as pd
from pathlib import Path

# Base folder path
BASE_FOLDER = Path("C:/mini_etl_project")
SILVER_FOLDER = BASE_FOLDER / "data" / "silver"
BRONZE_FOLDER = BASE_FOLDER / "data" / "bronze"

# Load tables
airport_top250 = pd.read_csv(BRONZE_FOLDER / "airport_top250_locations_raw.csv")
stg_airport_flights = pd.read_parquet(SILVER_FOLDER / "stg_airport_flights.parquet")
stg_airport_geography = pd.read_csv(SILVER_FOLDER / "stg_airport_geography.csv")
stg_weather_daily = pd.read_parquet(SILVER_FOLDER / "stg_weather_daily_clean.parquet")

# First left join: airport_top250 to stg_airport_flights
silver_tables_joined = airport_top250.merge(
    stg_airport_flights,
    left_on="airport_code",
    right_on="apt_icao",
    how="left"
)


# Second left join: stg_airport_flights to airport_geography
silver_tables_joined = silver_tables_joined.merge(
    stg_airport_geography,
    left_on="apt_icao",
    right_on="icao_clean",
    how="left"
)

# Dropping the duplicate meta data columns

stg_weather_daily = stg_weather_daily.drop(
    columns=["run_id", "load_timestamp", "source"],
    errors="ignore"
)

# Third left join: silver_tables_joined to stg_weather_daily
silver_tables_joined = silver_tables_joined.merge(
    stg_weather_daily,
    left_on=["apt_icao", "date_y"],
    right_on=["airport_code", "date"],
    how="left"
)


# cleaning columns
silver_tables_joined = silver_tables_joined[[
    'date',
    'airport_name_clean',
    'icao_clean',
    "apt_icao",
    'iata_clean',
    'country_clean',
    'city_clean',
    'year_x',
    'month_num',
    'month_str',
    'latitude_clean', 
    'longitude_clean',
    'altitude_clean',
    'depatures', 
    'depatures_data_submitted', 
    'delay_minutes',
    'temperature_2m_mean',
    'precipitation_sum',
    'wind_speed_10m_max'
]]

silver_tables_joined.rename(columns={
    "depatures"                 : "departures",
    "depatures_data_submitted"  : "departures_data_submitted",
    'year_x'                    : "year",
    "airport_name_clean"        : "airport_name",
    "icao_clean"                : "icao",
    'iata_clean'                : "iata",
    "country_clean"             : "country",
    "city_clean"                : "city",
    'latitude_clean'            : 'latitude' , 
    'longitude_clean'           : "longitude",
    'altitude_clean'            : "altitude",


}, inplace=True)

silver_tables_joined.to_parquet(SILVER_FOLDER / "silver_tables_joined.parquet", index=False)