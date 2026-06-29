# Bronze Layer Documentation

Project: Medallion Architecture - European Airport Traffic and Weather Analytics (2021-2025)

## 1. Purpose of the Bronze Layer

The Bronze layer is the raw ingestion layer of the pipeline. Its purpose is to store source data as close as possible to the original structure, while adding minimal technical metadata for lineage and reproducibility.

Bronze data should be used for traceability, reprocessing, and source-level quality checks. It is not the reporting layer and should not be connected directly to Power BI.

In this project, Bronze stores the raw source extracts for:

1. Airport Flight Data from EuroControl
2. Airport Locations from OpenFlights

Weather data from Open-Meteo is used later in the Silver layer to create `stg_weather_daily`, using airport location information from the airport locations source.

## 2. Bronze Layer Scope

The project scope is European airport traffic analysis for 2021-2025. The Bronze layer stores the raw input files needed to support this scope.

Important rule: Bronze should preserve the original source data. Filtering, joining, standardizing, typing, and business cleaning should happen in the Silver layer, not in Bronze.

## 3. Bronze Input Sources

| Source | Description | Source Type | Used For |
|---|---|---|---|
| EuroControl Airport Flight Data | Airport flight traffic files for the selected years | Downloaded CSV files | Main traffic dataset |
| OpenFlights Airport Locations | Airport mapping data with airport codes, country/city, and coordinates | Downloaded mapping dataset | Airport location enrichment and weather API coordinates |

## 4. Bronze Output Files

Recommended folder structure:

```text
data/
  bronze/
    airport_flights/
      airport_flights_2021_raw.csv
      airport_flights_2022_raw.csv
      airport_flights_2023_raw.csv
      airport_flights_2024_raw.csv
      airport_flights_2025_raw.csv
    airport_locations/
      airport_locations_raw.csv
    quality/
      bronze_quality_summary.csv
      bronze_ingestion_log.csv
```

### 4.1 Airport Flight Data

Raw file group:

```text
data/bronze/airport_flights/airport_flights_<year>_raw.csv
```

Expected yearly files:

```text
airport_flights_2021_raw.csv
airport_flights_2022_raw.csv
airport_flights_2023_raw.csv
airport_flights_2024_raw.csv
airport_flights_2025_raw.csv
```

Example columns seen in the provided 2025 file:

| Column | Description |
|---|---|
| `YEAR` | Source year |
| `MONTH_NUM` | Month number from source |
| `MONTH_MON` | Month abbreviation from source |
| `FLT_DATE` | Flight date |
| `APT_ICAO` | Airport ICAO code |
| `APT_NAME` | Airport name |
| `STATE_NAME` | Country/state name from source |
| `FLT_DEP_1` | Departure flight metric from source |
| `FLT_DEP_IFR_2` | IFR departure metric from source, where available |
| `DLY_ALL_PRE_2` | Delay metric from source, where available |
| `load_timestamp` | Ingestion timestamp |
| `source_system` | Source URL or source system name |
| `run_id` | Pipeline run identifier |

### 4.2 Airport Locations

Raw file:

```text
data/bronze/airport_locations/airport_locations_raw.csv
```

Example columns seen in the provided airport locations file:

| Column | Description |
|---|---|
| `Name` | Airport name |
| `City` | City name |
| `Country` | Country name |
| `IATA` | IATA airport code |
| `ICAO` | ICAO airport code |
| `Latitude` | Airport latitude |
| `Longitude` | Airport longitude |
| `Altitude` | Airport altitude |
| `Timezone` | Timezone offset from source |
| `DST` | Daylight saving time flag from source |
| `Tz database timezone` | Timezone database name |
| `Type` | Location type, for example airport |
| `Source` | Original source label from dataset |
| `run_id` | Pipeline run identifier |
| `load_timestamp` | Ingestion timestamp |
| `source` | Source URL |

## 5. Metadata Requirements

Each Bronze file should include or be stored with the following metadata:

| Metadata Column | Description |
|---|---|
| `source_name` or `source_system` | Name of the source system, for example EuroControl or OpenFlights |
| `source_file_api_name` or `source` | File name, API name, or source URL |
| `load_timestamp` | Timestamp when the file was loaded into Bronze |
| `run_id` | Unique identifier for the pipeline run |

If the source already includes metadata columns, keep them. If metadata is missing, add it during ingestion.

Recommended additional metadata for the ingestion log:

| Column | Description |
|---|---|
| `run_id` | Unique pipeline run id |
| `source_name` | Source name |
| `bronze_file_path` | File path written to Bronze |
| `load_timestamp` | Load timestamp |
| `rows_read` | Number of rows read from source |
| `columns_read` | Number of columns read from source |
| `status` | Success or failure |
| `error_message` | Error details if ingestion fails |

## 6. Bronze Processing Rules

The Bronze layer should follow these rules:

1. Keep original source column names.
2. Keep original source values and nulls.
3. Do not join datasets in Bronze.
4. Do not rename columns in Bronze.
5. Do not remove duplicates in Bronze.
6. Do not replace or impute missing values in Bronze.
7. Do not convert business data types unless needed only to store the file safely.
8. Add only technical metadata such as `run_id`, `load_timestamp`, and source information.
9. Perform basic source quality checks, but do not reject records here.
10. Send cleaning, standardization, typing, and validation outputs to the Silver layer.

## 7. Bronze Quality Checks

Bronze quality checks are source-level checks. They should identify problems early, but the rows should normally still be preserved in Bronze.

Recommended checks:

| Check | Airport Flight Data | Airport Locations |
|---|---|---|
| File exists and is readable | Yes | Yes |
| File is not empty | Yes | Yes |
| Row count captured | Yes | Yes |
| Column count captured | Yes | Yes |
| Required columns present | `YEAR`, `FLT_DATE`, `APT_ICAO` | `Name`, `Country`, `ICAO`, `Latitude`, `Longitude` |
| Duplicate full rows counted | Yes | Yes |
| Missing values counted per column | Yes | Yes |
| Metadata columns present | `load_timestamp`, `source_system`, `run_id` | `load_timestamp`, `source`, `run_id` |
| Date parse check | `FLT_DATE` can be parsed | Not applicable |
| Coordinate range check | Not applicable | Latitude between -90 and 90, longitude between -180 and 180 |

Recommended output:

```text
data/bronze/quality/bronze_quality_summary.csv
```

Suggested columns:

```text
run_id
source_name
file_name
rows_read
columns_read
duplicate_rows
missing_required_key_count
invalid_date_count
invalid_coordinate_count
load_timestamp
status
notes
```

## 8. Current Sample Profile

The current uploaded sample files show the following Bronze-level profile. These numbers should be regenerated when all yearly files are loaded.

### Airport Flight Data - 2025 sample

| Metric | Result |
|---|---:|
| Rows | 115,655 |
| Columns | 13 |
| Duplicate rows | 0 |
| Flight date range | 2025-01-01 to 2025-12-31 |
| Required metadata present | Yes |
| Missing `FLT_DEP_IFR_2` | 81,503 |
| Missing `DLY_ALL_PRE_2` | 81,503 |

Bronze interpretation: the file is readable, has metadata, and contains no full-row duplicates. Missing IFR/delay fields should be documented as source completeness issues and handled later in Silver/Gold according to business rules.

### Airport Locations sample

| Metric | Result |
|---|---:|
| Rows | 7,698 |
| Columns | 16 |
| Duplicate rows | 0 |
| Missing `City` values | 49 |
| Latitude range | -90.0 to 89.5 |
| Longitude range | -179.877 to 179.951 |
| Required metadata present | Yes |

Bronze interpretation: the file is readable and has valid coordinate ranges. Missing city values should be handled or reviewed in the Silver layer.

## 9. Handoff from Bronze to Silver

The Bronze layer feeds the Silver layer as follows:

| Bronze Input | Silver Output | Silver Action |
|---|---|---|
| Airport flight raw yearly files | `stg_airport_flights` | Concatenate yearly files, standardize column names, parse dates, type numeric fields, validate keys |
| Airport locations raw file | `airport_geography` | Standardize airport codes, clean location fields, validate coordinates, prepare airport geography |
| Open-Meteo API data using airport locations | `stg_weather_daily` | Retrieve daily weather data using airport coordinates and dates |

## 10. Definition of Done for Bronze

The Bronze layer is complete when:

- All expected raw source files are stored in the Bronze folder.
- Source structure is preserved as much as practical.
- Metadata columns or metadata log records exist for each file.
- Each ingestion run has a unique `run_id`.
- Row counts and schema checks are recorded.
- Missing value summaries are generated.
- No cleaning or business transformations are applied in Bronze.
- Bronze outputs can be reprocessed into Silver.
- The Bronze ingestion script or notebook is committed to Git.

## 11. Limitations and Notes

- Bronze data may contain missing values, inconsistent names, invalid values, or duplicated business keys. This is expected.
- Bronze is not intended for Power BI reporting.
- If a source changes its schema, the Bronze quality summary should detect the change before Silver processing.
- Weather data is not stored as a Bronze raw file in the current architecture diagram; it is created in Silver as `stg_weather_daily` from Open-Meteo using airport location information.
