# IMPORTS

import pandas as pd

from pathlib import Path

# CONSTANTS

PROJECT             = Path(__file__).resolve().parents[2]
WEATHER_DATA_RAW    = PROJECT / "data" / "silver" / "stg_weather_daily.csv"
OUTPUT_DIR          = PROJECT / "data" / "silver"


# HELPER FUNCTIONS

def inspect_weather_data(df: pd.DataFrame) -> None:
    """Print basic dataset diagnostics."""

    print("Shape:", df.shape)
    print("\nColumns:")
    print(df.columns.tolist())
    print("\nDtypes:")
    print(df.dtypes)
    print("\nMissing values:")
    print(df.isna().sum())
    print("\nDuplicate rows:", df.duplicated().sum())
    print("\nHead:")
    print(df.head())


def standardize_weather_data(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize column names and dtypes."""
    df = df.copy()

    df.columns = df.columns.str.strip().str.lower()

    numeric_columns = [
        "longitude",
        "latitude",
        "year",
        "month",
        "day",
        "temperature_2m_mean",
        "precipitation_sum",
        "wind_speed_10m_max",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    if "load_timestamp" in df.columns:
        df["load_timestamp"] = pd.to_datetime(df["load_timestamp"], errors="coerce", utc=True)

    if "source" in df.columns:
        df["source"] = df["source"].astype("string").str.strip().replace("", pd.NA)

    if "run_id" in df.columns:
        df["run_id"] = df["run_id"].astype("string").str.strip().replace("", pd.NA)

    return df


def create_date_column(df: pd.DataFrame) -> pd.DataFrame:
    """Create a date column from year, month, and day."""
    df = df.copy()

    df["date"] = pd.to_datetime(
        df[["year", "month", "day"]],
        errors="coerce",
    )

    return df


# MAIN FUNCTION

def main():

    # load raw weather data
    weather_df = pd.read_csv(WEATHER_DATA_RAW)

    # inspect and standardize weather data
    inspect_weather_data(weather_df)
    standardize_weather_data(weather_df)
    create_date_column(weather_df)

    # save standardized/cleaned weather data
    weather_df.to_parquet(OUTPUT_DIR / "stg_weather_daily_clean.parquet", index=False)


if __name__ == "__main__":
    main()