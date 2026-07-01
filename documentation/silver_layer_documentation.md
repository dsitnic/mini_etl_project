# Silver Layer Documentation
Project: Medallion Architecture - European Airport Traffic and Weather Analytics (2021-2025)

## 1. Purpose & Scope of the Silver Layer

The Silver layer is the cleaned and standardized layer of the pipeline. Its purpose is to transform raw Bronze data into structured, validated, and reusable datasets that are ready for downstream modeling in Gold.

## 2. Silver Input Sources

| Source | Description | Comes From | Used For |
|---|---|---|---|
| Airport flight raw yearly files | Raw airport traffic data for 2021-2025 | Bronze `airport_flights_2021.csv` to `airport_flights_2025.csv` | Build `stg_airport_flights` |
| Airport locations raw file | Raw airport reference data with names, airport codes, timezone, and coordinates | Bronze `airport_locations_raw.csv` | Build `stg_airport_geography` |
| Top 250 airport list | Airport list used as the Silver join base | Bronze `airport_top250_locations_raw.csv` | Build `silver_tables_joined` |
| Top 250 airport list enriched with coordinates | Airport list with latitude and longitude added from Silver geography | Bronze `airport_top250_locations_joined.csv` | Fetch weather data from Open-Meteo |
| Open-Meteo API | Daily weather data for each airport coordinate from `2021-01-01` to `2025-12-31` | External weather API | Build `stg_weather_daily` |

## 3. Silver Output Files
| File | Purpose |
|---|---|
| `data/silver/stg_airport_flights.parquet` | Cleaned and standardized airport flight data |
| `data/silver/stg_airport_geography.csv` | Cleaned airport reference data with validated geography and airport codes |
| `data/silver/stg_weather_daily.csv` | Daily weather observations linked to airports and dates, before cleaning |
| `data/silver/stg_weather_daily_clean.parquet` | Cleaned daily weather observations linked to airports and dates |
| `data/silver/silver_tables_joined.parquet` | Combined Silver dataset created by joining the top 250 airport list with flight, geography, and cleaned weather data before validation |
| `data/silver/valid_rows.csv` | Rows that pass Silver validation checks and are used to build Gold tables |
| `data/silver/review_rows.csv` | Rows that fail Silver validation checks and are kept for review |
| `data/silver/metric_summary.csv` | Validation row-count summary created by `validate_silver.py` |
| `data/silver/review_summary.csv` | Grouped `review_reason` summary created by `validate_silver.py` |

## 4. Silver Standardizations

The Silver layer applies these standardizations across the staging scripts:

1. Flight data columns are lowercased, yearly files are concatenated, dates are parsed, and core measures are converted to numeric types.
2. Flight text fields are trimmed and normalized:
   `apt_icao` is uppercased, while `month_mon`, `apt_name`, and `state_name` are title-cased.
3. Flight columns are renamed for downstream use, including `flt_date -> date`, `state_name -> country`, `dly_all_pre_2 -> delay_minutes`, and the departure metrics used later in validation.
4. Airport location columns are renamed and standardized into cleaned fields such as `airport_name_clean`, `city_clean`, `country_clean`, `iata_clean`, `icao_clean`, `latitude_clean`, and `longitude_clean`.
5. Airport location coordinates, altitude, timezone, and load timestamp are cast to numeric or datetime types.
6. Weather data columns are lowercased, key numeric weather fields are coerced to numeric, `load_timestamp` is parsed as UTC datetime, and `airport_code` is uppercased.
7. Weather data gets a derived `date` column from `year`, `month`, and `day`.

## 5. Silver Cleaning/Standardization Scripts and Flow

The current Silver workflow is implemented by these scripts:

1. `src/python/clean_airport_flights.py`
   Reads the five Bronze flight files, standardizes them, and writes `data/silver/stg_airport_flights.parquet`.
2. `src/python/clean_airport_locations.py`
   Cleans the Bronze airport reference file and writes `data/silver/stg_airport_geography.csv`.
3. `src/python/join_top250_locations.py`
   Matches the top 250 airport list to Silver geography on airport code so latitude and longitude can be added for weather extraction.
4. `src/python/ingest_weather_data.py`
   Reads `data/bronze/airport_top250_locations_joined.csv`, fetches Open-Meteo daily weather history, adds metadata, and writes `data/silver/stg_weather_daily.csv`.
5. `src/python/clean_weather_data.py`
   Cleans the raw Silver weather extract, creates a `date` column, and writes `data/silver/stg_weather_daily_clean.parquet`.
6. `src/python/validation_joins.py`
   Joins the Bronze top 250 airport list to Silver flights, Silver geography, and cleaned Silver weather, then writes `data/silver/silver_tables_joined.parquet`.
7. `src/python/validate_silver.py`
   Validates the joined Silver dataset and writes the final review, valid, and summary files.

## 6. Silver Validation

The Silver validation step is implemented in `src/python/validate_silver.py`.

The script loads `data/silver/silver_tables_joined.parquet` and checks:

- all expected columns exist in the joined Silver dataset
- important fields are not null:
  `date`, `airport_name`, `icao`, `country`, `latitude`, `longitude`,
  `departures`, `departures_data_submitted`, `delay_minutes`,
  `temperature_2m_mean`, `precipitation_sum`, `wind_speed_10m_max`
- numeric ranges are valid:
  `longitude` between `-180` and `180`, `latitude` between `-90` and `90`,
  `temperature_2m_mean` between `-40` and `60`,
  `precipitation_sum >= 0`, `wind_speed_10m_max >= 0`,
  `departures >= 0`, `departures_data_submitted >= 0`, `delay_minutes >= 0`
- `date` is within `2021-01-01` to `2025-12-31`
- `icao` codes are exactly 4 characters long
- duplicate records are counted for the key combination `date + icao`

Rows with one or more failed checks are written to `data/silver/review_rows.csv`.
Rows with no failed checks are written to `data/silver/valid_rows.csv`.

The script also creates:

- `data/silver/metric_summary.csv` with row counts for the top 250 airport locations input, cleaned and raw staging inputs, and validation outputs
- `data/silver/review_summary.csv` with grouped `review_reason` counts

## 7. Handoff from Silver to Gold

The Silver layer feeds the Gold layer as follows:

| Silver Input | Gold Output | Gold Action |
|---|---|---|
| `valid_rows` | `dim_date` | Build the date dimension from distinct validated dates |
| `valid_rows` | `fact_flights` | Build flight facts by airport and date |
| `valid_rows` | `dim_airport` | Build airport dimension from distinct airport attributes |

The Gold load step is implemented in `src/python/data_loading_to_gold.py`, which reads `data/silver/valid_rows.csv` and constructs `dim_date`, `dim_airport`, and `fact_flights`.