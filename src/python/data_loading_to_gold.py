import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from pathlib import Path

# -----------------------------
# Setup
# -----------------------------
BASE_DIR = Path.cwd()
VALID_ROWS_PATH = BASE_DIR / "data" / "silver" / "valid_rows.csv"

load_dotenv()

server = os.getenv("DB_SERVER")
database = os.getenv("DB_DATABASE")
username = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")
driver = os.getenv("DB_DRIVER")

params = quote_plus(
    f"DRIVER={driver};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"UID={username};"
    f"PWD={password};"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=30;"
)

engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

# -----------------------------
# Read source
# -----------------------------
valid_rows = pd.read_csv(VALID_ROWS_PATH)

valid_rows["date"] = pd.to_datetime(valid_rows["date"])

# -----------------------------
# Create dim_date
# -----------------------------
dim_date = valid_rows[["date"]].drop_duplicates().copy()

dim_date["date_key"] = dim_date["date"].dt.strftime("%Y%m%d").astype(int)
dim_date["year"] = dim_date["date"].dt.year
dim_date["quarter"] = dim_date["date"].dt.quarter
dim_date["month_num"] = dim_date["date"].dt.month
dim_date["week_of_year"] = dim_date["date"].dt.isocalendar().week.astype(int)
dim_date["day_of_month"] = dim_date["date"].dt.day
dim_date["day_of_week"] = dim_date["date"].dt.weekday + 1
dim_date["month_name"] = dim_date["date"].dt.month_name()
dim_date["month_short"] = dim_date["date"].dt.strftime("%b")
dim_date["year_month"] = dim_date["date"].dt.strftime("%Y-%m")
dim_date["day_name"] = dim_date["date"].dt.day_name()
dim_date["is_weekend"] = dim_date["day_of_week"].isin([6, 7])

def get_season(month):
    if month in [12, 1, 2]:
        return "Winter"
    if month in [3, 4, 5]:
        return "Spring"
    if month in [6, 7, 8]:
        return "Summer"
    return "Autumn"

dim_date["season"] = dim_date["month_num"].apply(get_season)

dim_date = dim_date[
    [
        "date_key", "date", "year", "quarter", "month_num",
        "week_of_year", "day_of_month", "day_of_week",
        "month_name", "month_short", "year_month",
        "day_name", "is_weekend", "season"
    ]
]

# -----------------------------
# Create dim_airport
# -----------------------------
dim_airport = valid_rows[
    [
        "airport_name",
        "apt_icao",
        "iata",
        "country",
        "city",
        "latitude",
        "longitude"
    ]
].drop_duplicates(subset=["apt_icao"]).copy()

dim_airport = dim_airport.rename(columns={
    "apt_icao": "icao_code",
    "iata": "iata_code"
})

dim_airport = dim_airport.reset_index(drop=True)
dim_airport["airport_key"] = dim_airport.index + 1

dim_airport["region"] = None

dim_airport = dim_airport[
    [
        "airport_key",
        "airport_name",
        "icao_code",
        "iata_code",
        "country",
        "city",
        "latitude",
        "longitude"
    ]
]

# -----------------------------
# Create fact_flights
# -----------------------------
fact_source = valid_rows.copy()

fact_source["date_key"] = fact_source["date"].dt.strftime("%Y%m%d").astype(int)

fact_source = fact_source.merge(
    dim_airport[["airport_key", "icao_code"]],
    left_on="apt_icao",
    right_on="icao_code",
    how="left"
)

fact_flights = fact_source[
    [
        "date_key",
        "airport_key",
        "departures",
        "delay_minutes",
        "temperature_2m_mean",
        "precipitation_sum",
        "wind_speed_10m_max"
    ]
].copy()

fact_flights = fact_flights.rename(columns={
    "airport_key": "departure_apt_key",
    "delay_minutes": "total_departures_delay_m"
})

fact_flights = fact_flights.reset_index(drop=True)
fact_flights["flight_key"] = fact_flights.index + 1

fact_flights = fact_flights[
    [
        "flight_key",
        "date_key",
        "departure_apt_key",
        "departures",
        "total_departures_delay_m",
        "temperature_2m_mean",
        "precipitation_sum",
        "wind_speed_10m_max"
    ]
]

# -----------------------------
# Load to SQL Server
# -----------------------------
with engine.begin() as conn:
    dim_date.to_sql(
        "dim_date",
        con=conn,
        schema="gold",
        if_exists="append",
        index=False
    )

    dim_airport.to_sql(
        "dim_airport",
        con=conn,
        schema="gold",
        if_exists="append",
        index=False
    )

    fact_flights.to_sql(
        "fact_flights",
        con=conn,
        schema="gold",
        if_exists="append",
        index=False
    )

print("Gold tables loaded successfully.")
print(f"dim_date rows: {len(dim_date)}")
print(f"dim_airport rows: {len(dim_airport)}")
print(f"fact_flights rows: {len(fact_flights)}")