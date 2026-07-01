# Data Dictionary and Profiling Notes
Project: Medallion Architecture - European Airport Traffic and Weather Analytics (2021-2025)

## 1. Purpose

This document describes the main datasets used in the Bronze, Silver, and Gold layers. It is intended to hold column-level information so the layer documentation can stay focused on pipeline flow, scripts, validation, and handoff.

## 2. Dataset Inventory

| Layer | Dataset/File | Rows | Purpose |
|---|---|---:|---|
| Bronze | `data/bronze/airport_flights_2021.csv` | 112,727 | Raw EuroControl airport flight data for 2021 |
| Bronze | `data/bronze/airport_flights_2022.csv` | 113,630 | Raw EuroControl airport flight data for 2022 |
| Bronze | `data/bronze/airport_flights_2023.csv` | 114,420 | Raw EuroControl airport flight data for 2023 |
| Bronze | `data/bronze/airport_flights_2024.csv` | 115,022 | Raw EuroControl airport flight data for 2024 |
| Bronze | `data/bronze/airport_flights_2025.csv` | 115,655 | Raw EuroControl airport flight data for 2025 |
| Bronze | `data/bronze/airport_locations_raw.csv` | 7,698 | Raw OpenFlights airport reference data |
| Bronze | `data/bronze/airport_top250_locations_raw.csv` | 250 | Project airport scope file |
| Bronze | `data/bronze/airport_top250_locations_joined.csv` | 250 | Top 250 airport scope file enriched with coordinates |
| Silver | `data/silver/stg_airport_flights.parquet` | 571,454 | Cleaned and concatenated flight staging data |
| Silver | `data/silver/stg_airport_geography.csv` | 7,698 | Cleaned airport geography staging data |
| Silver | `data/silver/stg_weather_daily.csv` | 456,500 | Raw daily weather extract from Open-Meteo |
| Silver | `data/silver/stg_weather_daily_clean.parquet` | 456,500 | Cleaned daily weather staging data with derived date |
| Silver | `data/silver/silver_tables_joined.parquet` | 448,423 | Joined Silver validation dataset |
| Silver | `data/silver/valid_rows.csv` | 159,516 | Rows that passed Silver validation |
| Silver | `data/silver/review_rows.csv` | 288,907 | Rows that failed one or more Silver validation checks |
| Silver | `data/silver/metric_summary.csv` | 8 | Validation row-count summary |
| Silver | `data/silver/review_summary.csv` | 3 | Grouped validation review reasons |
| Gold | `gold.dim_date` | Built from `valid_rows` | Date dimension |
| Gold | `gold.dim_airport` | Built from `valid_rows` | Airport dimension |
| Gold | `gold.fact_flights` | Built from `valid_rows` | Flight and weather fact table |


## 3. Bronze Data Dictionary

### 3.1 Airport Flight Files

Applies to `airport_flights_2021.csv` through `airport_flights_2025.csv`.

| Column | Type | Description | Notes |
|---|---|---|---|
| `YEAR` | integer | Source year | Used during Silver date and year standardization |
| `MONTH_NUM` | integer | Month number | Used as `month_num` in Silver |
| `MONTH_MON` | string | Month label | Standardized to title case as `month_str` |
| `FLT_DATE` | string/date | Flight date | Parsed as `date` in Silver |
| `APT_ICAO` | string | Airport ICAO code | Standardized to uppercase; used as join key |
| `APT_NAME` | string | Airport name | Standardized to title case |
| `STATE_NAME` | string | Country/state name from source | Renamed to `country` in Silver |
| `FLT_DEP_1` | integer | Departure flight count metric | Renamed to `departures` after Silver joins |
| `FLT_DEP_IFR_2` | float | Submitted IFR departure count metric | Renamed to `departures_data_submitted` after Silver joins |
| `DLY_ALL_PRE_2` | float | Pre-departure delay minutes | Renamed to `delay_minutes` in Silver |
| `load_timestamp` | string/timestamp | Ingestion timestamp | Technical metadata |
| `source_system` | string | EuroControl source URL/system | Technical metadata |
| `run_id` | string | Ingestion run identifier | Technical metadata |

Profiling note: `FLT_DEP_IFR_2` and `DLY_ALL_PRE_2` have many missing values in every yearly file. This is expected source completeness behavior and is handled during Silver validation.

### 3.2 Airport Locations Raw

Applies to `data/bronze/airport_locations_raw.csv`.

| Column | Type | Description | Notes |
|---|---|---|---|
| `Name` | string | Airport name | Cleaned to `airport_name_clean` in Silver |
| `City` | string | City name | Some missing values |
| `Country` | string | Country name | Cleaned to `country_clean` in Silver |
| `IATA` | string | IATA airport code | Cleaned to `iata_clean` in Silver |
| `ICAO` | string | ICAO airport code | Cleaned to `icao_clean` in Silver |
| `Latitude` | float | Airport latitude | Cleaned to `latitude_clean` in Silver |
| `Longitude` | float | Airport longitude | Cleaned to `longitude_clean` in Silver |
| `Altitude` | integer | Airport altitude | Cleaned to `altitude_clean` in Silver |
| `Timezone` | string/float | Timezone offset | Cleaned to `timezone_clean` in Silver |
| `DST` | string | Daylight saving time flag | Cleaned to `dst_clean` in Silver |
| `Tz database timezone` | string | Timezone database name | Cleaned to `tz_database_timezone_clean` in Silver |
| `Type` | string | OpenFlights location type | Not kept in final Silver geography output |
| `Source` | string | OpenFlights source label | Not kept as a business field |
| `run_id` | string | Ingestion run identifier | Technical metadata |
| `load_timestamp` | string/timestamp | Ingestion timestamp | Technical metadata |
| `source` | string | Source URL | Technical metadata |

### 3.3 Top 250 Airport Files

Applies to `airport_top250_locations_raw.csv` and `airport_top250_locations_joined.csv`.

| Column | Type | Description | Notes |
|---|---|---|---|
| `date` | string/date | Source date for the top airport list | Used as source context |
| `airport_code` | string | Airport ICAO code | Used to join to Silver geography and fetch weather |
| `flights` | integer | Flight count from the top airport source file | Used to define airport scope |
| `run_id` | string | Ingestion run identifier | Technical metadata |
| `load_timestamp` | string/timestamp | Ingestion timestamp | Technical metadata |
| `source` | string | Source URL or label | Technical metadata |
| `Latitude` | float | Airport latitude | Present in joined file only |
| `Longitude` | float | Airport longitude | Present in joined file only |

## 4. Silver Data Dictionary

### 4.1 Staged Airport Flights

Applies to `data/silver/stg_airport_flights.parquet`.

| Column | Type | Description | Notes |
|---|---|---|---|
| `year` | numeric | Source year | From Bronze `YEAR` |
| `month_num` | numeric | Month number | From Bronze `MONTH_NUM` |
| `month_str` | string | Month label | From Bronze `MONTH_MON` |
| `date` | date | Flight date | From Bronze `FLT_DATE` |
| `apt_icao` | string | Airport ICAO code from flight data | Join key |
| `apt_name` | string | Airport name from flight data | Standardized text |
| `country` | string | Country/state name from flight data | From Bronze `STATE_NAME` |
| `depatures` | numeric | Departure flight count metric | Typo retained in staging; renamed later to `departures` |
| `depatures_data_submitted` | numeric | Submitted departure count metric | Typo retained in staging; renamed later to `departures_data_submitted` |
| `delay_minutes` | numeric | Pre-departure delay minutes | Validated in Silver |
| `load_timestamp` | timestamp | Ingestion timestamp | Metadata from Bronze |
| `source_system` | string | EuroControl source URL/system | Metadata from Bronze |
| `run_id` | string | Ingestion run identifier | Metadata from Bronze |

### 4.2 Staged Airport Geography

Applies to `data/silver/stg_airport_geography.csv`.

| Column | Type | Description | Notes |
|---|---|---|---|
| `airport_name_clean` | string | Cleaned airport name | Title-cased |
| `city_clean` | string | Cleaned city name | Title-cased |
| `country_clean` | string | Cleaned country name | Title-cased |
| `iata_clean` | string | Cleaned IATA code | Uppercased |
| `icao_clean` | string | Cleaned ICAO code | Uppercased; join key |
| `latitude_clean` | float | Cleaned airport latitude | Validated later |
| `longitude_clean` | float | Cleaned airport longitude | Validated later |
| `altitude_clean` | numeric | Cleaned airport altitude | From OpenFlights |
| `timezone_clean` | numeric | Cleaned timezone offset | From OpenFlights |
| `dst_clean` | string | Cleaned daylight saving flag | Uppercased |
| `tz_database_timezone_clean` | string | Cleaned timezone database name | Title-cased |
| `run_id` | string | Ingestion run identifier | Metadata |
| `load_timestamp_clean` | timestamp | Cleaned ingestion timestamp | Metadata |
| `source` | string | Source URL | Metadata |

### 4.3 Weather Daily Staging

Applies to `data/silver/stg_weather_daily.csv` and `data/silver/stg_weather_daily_clean.parquet`.

| Column | Type | Description | Notes |
|---|---|---|---|
| `airport_code` | string | Airport ICAO code used for weather lookup | Uppercased during cleaning |
| `longitude` | float | Longitude returned by Open-Meteo | Used for traceability |
| `latitude` | float | Latitude returned by Open-Meteo | Used for traceability |
| `year` | integer | Weather observation year | Used to create `date` |
| `month` | integer | Weather observation month | Used to create `date` |
| `day` | integer | Weather observation day | Used to create `date` |
| `temperature_2m_mean` | float | Daily mean 2m air temperature | Validated in Silver |
| `precipitation_sum` | float | Daily precipitation total | Validated in Silver |
| `wind_speed_10m_max` | float | Daily maximum 10m wind speed | Validated in Silver |
| `load_timestamp` | timestamp | Weather ingestion timestamp | Metadata |
| `source` | string | Open-Meteo source URL | Metadata |
| `run_id` | string | Weather ingestion run identifier | Metadata |
| `date` | date | Weather observation date | Present in cleaned parquet output |

### 4.4 Joined Silver Validation Dataset

Applies to `silver_tables_joined.parquet`, `valid_rows.csv`, and `review_rows.csv`.

| Column | Type | Description | Notes |
|---|---|---|---|
| `date` | date | Flight/weather date | Must be between 2021-01-01 and 2025-12-31 |
| `airport_name` | string | Cleaned airport name | Required by validation |
| `icao` | string | Cleaned ICAO code from airport geography | Must be 4 characters |
| `apt_icao` | string | ICAO code from flight data | Used for Gold airport joins |
| `iata` | string | Cleaned IATA code | Airport identifier |
| `country` | string | Cleaned country name | Required by validation |
| `city` | string | Cleaned city name | Airport location attribute |
| `year` | numeric | Flight year | From flight staging |
| `month_num` | numeric | Flight month number | From flight staging |
| `month_str` | string | Flight month label | From flight staging |
| `latitude` | float | Airport latitude | Must be between -90 and 90 |
| `longitude` | float | Airport longitude | Must be between -180 and 180 |
| `altitude` | numeric | Airport altitude | From airport geography |
| `departures` | numeric | Departure count | Must be non-negative |
| `departures_data_submitted` | numeric | Submitted departure count metric | Must be non-negative when present |
| `delay_minutes` | numeric | Pre-departure delay minutes | Must be non-negative when present |
| `temperature_2m_mean` | float | Daily mean 2m temperature | Must be between -40 and 60 |
| `precipitation_sum` | float | Daily precipitation total | Must be non-negative |
| `wind_speed_10m_max` | float | Daily maximum 10m wind speed | Must be non-negative |
| `review_reason` | string | Validation failure reason(s) | Empty for valid rows; populated in review rows |

Profiling notes:

- `silver_tables_joined.parquet` has 448,423 rows.
- `valid_rows.csv` has 159,516 rows.
- `review_rows.csv` has 288,907 rows.
- The validation script counted 0 duplicate `date + icao` combinations.
- Most review rows are caused by missing `departures_data_submitted` and `delay_minutes`.

### 4.5 Silver Validation Summary Files

| Dataset | Column | Type | Description |
|---|---|---|---|
| `metric_summary.csv` | `filename` | string | Source or output dataset name |
| `metric_summary.csv` | `row_count` | integer | Row count for the dataset |
| `review_summary.csv` | `review_reason` | string | Grouped validation failure reason |
| `review_summary.csv` | `count` | integer | Number of rows with that reason |

## 5. Gold Data Dictionary

### 5.1 `gold.dim_date`

| Column | Type | Description |
|---|---|---|
| `date_key` | integer | Date key in `YYYYMMDD` format |
| `date` | date | Calendar date |
| `year` | integer | Calendar year |
| `quarter` | integer | Calendar quarter |
| `month_num` | integer | Month number |
| `week_of_year` | integer | ISO week number |
| `day_of_month` | integer | Day number within month |
| `day_of_week` | integer | Day number within week, Monday = 1 |
| `month_name` | string | Full month name |
| `month_short` | string | Three-letter month abbreviation |
| `year_month` | string | Year-month label in `YYYY-MM` format |
| `day_name` | string | Full day name |
| `is_weekend` | boolean | Weekend flag |
| `season` | string | Season derived from month |

### 5.2 `gold.dim_airport`

| Column | Type | Description |
|---|---|---|
| `airport_key` | integer | Surrogate airport key |
| `airport_name` | string | Airport name |
| `icao_code` | string | ICAO airport code |
| `iata_code` | string | IATA airport code |
| `country` | string | Airport country |
| `city` | string | Airport city |
| `latitude` | float | Airport latitude |
| `longitude` | float | Airport longitude |

### 5.3 `gold.fact_flights`

| Column | Type | Description |
|---|---|---|
| `flight_key` | integer | Surrogate flight fact key |
| `date_key` | integer | Foreign key to `gold.dim_date` |
| `departure_apt_key` | integer | Foreign key to `gold.dim_airport` |
| `departures` | integer | Departure count |
| `total_departures_delay_m` | float | Total pre-departure delay minutes |
| `temperature_2m_mean` | float | Daily mean 2m temperature |
| `precipitation_sum` | float | Daily precipitation total |
| `wind_speed_10m_max` | float | Daily maximum 10m wind speed |

## 6. Data Quality Notes

- Bronze keeps source-level values and adds ingestion metadata.
- Silver performs the main cleaning, typing, joining, and validation.
- Rows with failed Silver validation are preserved in `review_rows.csv` rather than being deleted.
- Gold tables are loaded only from `valid_rows.csv`.
- Column names with `depatures` in `stg_airport_flights.parquet` are staging typos retained by the current script and corrected during `validation_joins.py`.
