import duckdb
from pathlib import Path
import pandas as pd

# create folder paths
silver_folder = Path(".") / "data" / "silver"
bronze_folder = Path(".") / "data" / "bronze"
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)

# all expected columns
all_columns = [
    'date',
    'airport_name',
    'icao',
    'iata',
    'country',
    'city',
    'year',
    'month_num',
    'month_str',
    'latitude', 
    'longitude',
    'altitude',
    'departures', 
    'departures_data_submitted', 
    'delay_minutes',
    'temperature_2m_mean',
    'precipitation_sum',
    'wind_speed_10m_max'
]

# read joined silver table
silver_tables_joined = pd.read_parquet(silver_folder / "silver_tables_joined.parquet")

# define important columns
important_columns = [
    'date',
    'airport_name',
    'icao',
    'country', 
    'latitude', 
    'longitude',  
    'departures', 
    'departures_data_submitted', 
    'delay_minutes', 
    'temperature_2m_mean', 
    'precipitation_sum', 
    'wind_speed_10m_max' 
]

# check all columns
print("check all columns ...")
missing_columns = sorted(set(all_columns) - set(silver_tables_joined.columns))
if missing_columns:
     raise ValueError(f"Missing columns: {missing_columns}")

# check for nulls
print("check for nulls ...")
silver_tables_joined["review_reason"] = ""

for column in important_columns:
     silver_tables_joined.loc[silver_tables_joined[column].isnull(), "review_reason"] += "MISSING_" + column.upper() + "; "

# value ranges check:
print("check value ranges ...")
silver_tables_joined.loc[~silver_tables_joined["longitude"].between(-180, 180), "review_reason"] += "INVALID_LONGITUDE; " 
silver_tables_joined.loc[~silver_tables_joined["latitude"].between(-90, 90), "review_reason"] += "INVALID_LATITUDE; " 
silver_tables_joined.loc[~silver_tables_joined["temperature_2m_mean"].between(-40, 60), "review_reason"] += "INVALID_TEMPERATURE; " 
silver_tables_joined.loc[~(silver_tables_joined["precipitation_sum"] >= 0), "review_reason"] += "INVALID_PRECIPITATION; " 
silver_tables_joined.loc[~(silver_tables_joined["wind_speed_10m_max"] >= 0), "review_reason"] += "INVALID_WINDSPEED; " 
silver_tables_joined.loc[~(silver_tables_joined["departures"] >= 0), "review_reason"] += "INVALID_DEPARTURES; " # null values could cause error
silver_tables_joined.loc[~(silver_tables_joined["departures_data_submitted"] >= 0), "review_reason"] += "INVALID_DATA_SUBMITTED; " # null values could cause error
silver_tables_joined.loc[~(silver_tables_joined["delay_minutes"] >= 0), "review_reason"] += "INVALID_DELAY; " # null values could cause error
silver_tables_joined.loc[~(silver_tables_joined["date"].between(pd.to_datetime("2021-01-01"), pd.to_datetime("2025-12-31"))), "review_reason"] += "INVALID_DATE; " # null values could cause error

# valid values check:
print("check valid values ...")
silver_tables_joined.loc[~(silver_tables_joined["icao"].str.len().eq(4)), "review_reason"] += "INVALID_ICAO_LENGTH; "

# duplicates check: date + icao
print("check duplicates ...")
duplic = silver_tables_joined.groupby(["date", "icao"]).agg(
     count = ("icao" , "count")
).reset_index()

duplic = duplic.loc[duplic["count"] > 1]
# duplic.head()
print("Number of duplicates:", len(duplic))

# display(silver_tables_joined.head(5))
# silver_tables_joined.loc[(silver_tables_joined["review_reason"] != "") & ~(silver_tables_joined["review_reason"].isin(["MISSING_DEPARTURES_DATA_SUBMITTED; MISSING_DELAY_MINUTES; "]))].tail()

review_rows = silver_tables_joined.loc[(silver_tables_joined["review_reason"] != "")]
valid_rows = silver_tables_joined.loc[(silver_tables_joined["review_reason"] == "")]


# dataframes to output
print("reading files ...")
top_250 = pd.read_csv(bronze_folder / "airport_top250_locations_raw.csv")
stg_airport_flights = pd.read_parquet(silver_folder / "stg_airport_flights.parquet")
stg_weather_daily = pd.read_csv(silver_folder / "stg_weather_daily.csv")
airport_locations = pd.read_csv(bronze_folder / "airport_locations_raw.csv")

print("create metric summary ...")
metric_summary = pd.DataFrame([
 {"filename": "airport_top250_locations_raw", "row_count": len(top_250)},
 {"filename": "stg_airport_flights", "row_count": len(stg_airport_flights)},
 {"filename": "stg_weather_daily", "row_count": len(stg_weather_daily)},
 {"filename": "airport_locations", "row_count": len(airport_locations)},
 {"filename": "silver_tables_joined", "row_count": len(silver_tables_joined)},
 {"filename": "review_rows", "row_count": len(review_rows)},
 {"filename": "duplicated_rows", "row_count": len(duplic)},
 {"filename": "valid_rows", "row_count": len(valid_rows)},
#  {"metric_name": "unknown_category_rows", "metric_value": len(product_review_rows[product_review_rows["review_reason"] == "UNKNOWN_CATEGORY"])}
])
print(metric_summary)

# display(metric_summary)
print("create review reason summary ...")
review_summary = review_rows.value_counts("review_reason").reset_index()
review_summary = review_summary[["count", "review_reason"]]
# display(review_summary)
# print(review_summary)



# write files
print("saving files ...")
valid_rows.to_csv(silver_folder / "valid_rows.csv", index=False)
review_rows.to_csv(silver_folder / "review_rows.csv", index=False)

metric_summary.to_csv(silver_folder / "metric_summary.csv", index=False)
review_summary.to_csv(silver_folder / "review_summary.csv", index=False)
print("validation done")