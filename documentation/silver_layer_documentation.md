# Silver Layer Documentation
WORK IN PROGRESS (UPDATE WHEN SILVER LAYER IS FINISHED)
Project: Medallion Architecture - European Airport Traffic and Weather Analytics (2021-2025)

## 1. Purpose & Scope of the Silver Layer

The Silver layer is the cleaned and standardized layer of the pipeline. Its purpose is to transform raw Bronze data into structured, validated, and reusable datasets that are ready for downstream modeling in Gold.

## 2. Silver Input Sources

| Source | Description | Comes From | Used For |
|---|---|---|---|
| Airport flight raw yearly files | Raw airport traffic data for the selected years | Bronze `airport_flights` | Build `stg_airport_flights` |
| Airport locations raw file | Raw airport mapping data with airport codes and coordinates | Bronze `airport_locations` | Build `stg_airport_geography` |
| Joined top airport locations | Top airport list enriched with latitude and longitude | Bronze `airport_top250_locations_joined.csv` | Fetch weather data from Open-Meteo |
| Open-Meteo API | Daily weather data retrieved using airport coordinates | External weather API | Build `stg_weather_daily` |

## 3. Silver Output Files
Folder structure:

```text
data/
  silver/
    stg_airport_flights.parquet
    stg_airport_geography.csv
    stg_weather_daily.csv
    stg_weather_daily_clean.parquet
    validated_rows.csv
    rejected_rows.csv
    quality/
      silver_quality_summary.csv
```

### 3.1 Staged Airport Flights

| Field | Value |
|---|---|
| Path | `data/silver/stg_airport_flights.csv` |
| Purpose | Cleaned and standardized airport flight data for downstream joins and modeling |

### 3.2 Airport Geography

| Field | Value |
|---|---|
| Path | `data/silver/airport_geography.csv` |
| Purpose | Cleaned airport reference data with validated geography and airport codes |

### 3.3 Weather Daily Staging

| Field | Value |
|---|---|
| Path | `data/silver/stg_weather_daily.csv` |
| Purpose | Daily weather observations linked to airports and dates, uncleaned |

### 3.4 Weather Daily Staging

| Field | Value |
|---|---|
| Path | `data/silver/stg_weather_daily.parquet` |
| Purpose | Cleaned daily weather observations linked to airports and dates |

### 3.5 Staging Validation Dataset

| Field | Value |
|---|---|
| Path | `data/silver/silver_tables_joined.csv` |
| Purpose | Combined staging dataset created by joining flight data and weather data before validation |

### 3.6 Validated Rows

| Field | Value |
|---|---|
| Path | `data/silver/validated_rows.csv` |
| Purpose | Rows that pass Silver validation checks and are used to build Gold tables |

### 3.7 Rejected Rows

| Field | Value |
|---|---|
| Path | `data/silver/rejected_rows.csv` |
| Purpose | Rows that fail Silver validation checks and are kept for review |

## 4. Silver Standardizations

The Silver layer applies these standardizations:

1. Standardize column names to snake_case.
2. Cast text fields to string, strip leading/trailing spaces, and replace empty strings with nulls.
3. Normalize casing for text fields:
   - airport codes are uppercased
   - names, cities, countries, and month names are title-cased
4. Parse date and timestamp fields into datetime types.
5. Convert numeric fields such as flight metrics, coordinates, altitude, timezone, and weather measures to numeric types.
6. Rename selected source columns to clearer Silver names.
7. Save cleaned outputs to the Silver layer.

## 5. Silver Quality Checks (WIP, update with the actual quality checks used)

Silver checks should confirm:

- required columns exist
- dates and numeric fields are valid
- airport codes are present where needed
- joined flight/weather rows are complete enough for Gold
- failed rows are written to `rejected_rows.csv`
- summary stats written to `data/silver/quality/silver_quality_summary.csv`

## 6. Handoff from Silver to Gold

The Silver layer feeds the Gold layer as follows:

| Silver Input | Gold Output | Gold Action |
|---|---|---|
| `validated_rows` | `fact_flight` | Build flight facts by airport and date |
| `airport_geography` | `dim_airport` | Build airport dimension |

## 7. Definition of Done for Silver

The Silver layer is complete when:

- Bronze input files are transformed into standardized Silver datasets.
- Column names follow the project naming standard.
- Dates, coordinates, and numeric fields are typed correctly.
- Airport codes are standardized and usable for joins.
- Invalid dates and invalid coordinates are handled.
- Required keys are validated.
- Weather data is retrieved and stored at the intended grain.
- Silver quality checks are recorded.
- Silver outputs are ready to be used by Gold transformations.