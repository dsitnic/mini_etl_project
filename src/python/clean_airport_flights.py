# %%
import pandas as pd
from pathlib import Path
import os

# Setup directories
BRONZE_DIR = Path("data/bronze")
SILVER_DIR = Path("data/silver")
os.makedirs(BRONZE_DIR, exist_ok=True)


# %%
# read data

print("cleaning flight data ...")
print("read data ...")
flights_2021 = pd.read_csv(BRONZE_DIR / "airport_flights_2021.csv")
flights_2022 = pd.read_csv(BRONZE_DIR / "airport_flights_2022.csv")
flights_2023 = pd.read_csv(BRONZE_DIR / "airport_flights_2023.csv")
flights_2024 = pd.read_csv(BRONZE_DIR / "airport_flights_2024.csv")
flights_2025 = pd.read_csv(BRONZE_DIR / "airport_flights_2025.csv")

df_list = [flights_2021, flights_2022, flights_2023, flights_2024, flights_2025]
# %%
# columns to snake case
for df in df_list:
    df.rename(columns=str.lower, inplace=True)

# %%
# concatenate all years
flights_all = pd.concat(df_list)

# %%
# clean date columns
flights_all["flt_date"] = pd.to_datetime(flights_all["flt_date"] , errors="coerce")
flights_all["load_timestamp"] = pd.to_datetime(flights_all["load_timestamp"] , errors="coerce")

# %%
# clean string columns
def clean_strings_title(series):
    return series.astype("string").str.strip().str.title().replace("", pd.NA)
def clean_strings_upper(series):
    return series.astype("string").str.strip().str.upper().replace("", pd.NA)

flights_all["apt_icao"] = clean_strings_upper(flights_all["apt_icao"])
flights_all["month_mon"] = clean_strings_title(flights_all["month_mon"])
flights_all["apt_name"] = clean_strings_title(flights_all["apt_name"])
flights_all["state_name"] = clean_strings_title(flights_all["state_name"])

# %%
# clean numeric columns
def clean_numeric(series):
    numeric = series.astype("string").str.strip()
    return pd.to_numeric(numeric, errors="coerce")

print("convert column names to snake case ...")
flights_all["year"] = clean_numeric(flights_all["year"])
flights_all["month_num"] = clean_numeric(flights_all["month_num"])
flights_all["flt_dep_1"] = clean_numeric(flights_all["flt_dep_1"])
flights_all["flt_dep_ifr_2"] = clean_numeric(flights_all["flt_dep_ifr_2"])
flights_all["dly_all_pre_2"] = clean_numeric(flights_all["dly_all_pre_2"])


# %%

# %%
print("rename columns ...")
flights_all.columns
mapping = {
    'month_mon' : 'month_str', 
    'flt_date' : "date", 
    'state_name' : "country", 
    'flt_dep_1' : "depatures", 
    'flt_dep_ifr_2' : "depatures_data_submitted", 
    'dly_all_pre_2' : "delay_minutes",
}

flights_all.rename(columns=mapping,inplace=True)


# %%
# write output file
print("save as parquet ...")
flights_all.to_parquet(SILVER_DIR / "stg_airport_flights.parquet", index=False)

print("flight data cleaned")
# %%

# how much delay data is available?
print("No delay information available:", flights_all["delay_minutes"].isna().sum())
print("delay information available", flights_all["delay_minutes"].notna().sum())