# Bronze Layer Documentation
Project: Medallion Architecture - European Airport Traffic and Weather Analytics (2021-2025)

## 1. Purpose & Scope of the Bronze Layer

The Bronze layer is the raw ingestion layer of the pipeline. Its purpose is to store source extracts with minimal changes, while adding technical metadata for lineage and reproducibility.

Bronze data is used for traceability and reprocessing. Cleaning, standardization, joining, typing, and business validation happen later in the Silver layer.

## 2. Bronze Input Sources

| Source | Description | Comes From | Used For |
|---|---|---|---|
| EuroControl airport flight data | Airport traffic and pre-departure delay data for 2021-2025 | EuroControl CSV downloads | Build `stg_airport_flights` |
| OpenFlights airport locations | Airport reference data with names, codes, countries, cities, and coordinates | OpenFlights `airports.dat` | Build `stg_airport_geography` |
| Top 250 European airport list | Selected airport list used as the project airport scope | Local source file `data/source/top_250_airports_europe_2025.csv` | Build `airport_top250_locations_raw.csv` |
| Top 250 airport list enriched with coordinates | Top 250 list joined with airport coordinates | `airport_top250_locations_raw.csv` and `stg_airport_geography.csv` | Fetch weather data in Silver |

## 3. Bronze Output Files

| File | Purpose |
|---|---|
| `data/bronze/airport_flights_2021.csv` | Raw EuroControl flight data for 2021 with ingestion metadata |
| `data/bronze/airport_flights_2022.csv` | Raw EuroControl flight data for 2022 with ingestion metadata |
| `data/bronze/airport_flights_2023.csv` | Raw EuroControl flight data for 2023 with ingestion metadata |
| `data/bronze/airport_flights_2024.csv` | Raw EuroControl flight data for 2024 with ingestion metadata |
| `data/bronze/airport_flights_2025.csv` | Raw EuroControl flight data for 2025 with ingestion metadata |
| `data/bronze/airport_locations_raw.csv` | Raw OpenFlights airport reference data with ingestion metadata |
| `data/bronze/airport_top250_locations_raw.csv` | Top 250 airport scope file with ingestion metadata |
| `data/bronze/airport_top250_locations_joined.csv` | Top 250 airport scope file enriched with latitude and longitude for weather extraction |

The Bronze folder also contains older `airport_top100_*` files. These are not used by the current Silver workflow.

## 4. Bronze Ingestion Rules

The Bronze layer follows these rules:

1. Keep source data as close as practical to the original structure.
2. Add technical metadata such as `run_id`, `load_timestamp`, and source information.
3. Do not perform business cleaning, standardization, or validation in Bronze.
4. Do not reject records in Bronze because of missing or invalid business values.
5. Send cleaning, typing, joining, and validation work to the Silver layer.

## 5. Bronze Ingestion Scripts and Flow

The current Bronze workflow is implemented by these scripts:

1. `src/python/ingest_airport_flights.py`
   Downloads EuroControl yearly airport flight CSV files for 2021-2025, adds ingestion metadata, and writes `data/bronze/airport_flights_<year>.csv`.
2. `src/python/ingest_airports_source.py`
   Downloads OpenFlights airport location data, assigns source column names, adds ingestion metadata, and writes `data/bronze/airport_locations_raw.csv`.
3. `src/python/ingest_top250_airports.py`
   Reads `data/source/top_250_airports_europe_2025.csv`, adds ingestion metadata, and writes `data/bronze/airport_top250_locations_raw.csv`.
4. `src/python/join_top250_locations.py`
   Joins the top 250 airport list to Silver airport geography and writes `data/bronze/airport_top250_locations_joined.csv` so latitude and longitude can be used for weather extraction.

## 6. Bronze Metadata

Bronze files keep the original source columns and add technical metadata where available:

| Metadata Column | Purpose |
|---|---|
| `run_id` | Identifies one ingestion run |
| `load_timestamp` | Timestamp when the data was loaded |
| `source` or `source_system` | Source URL or source system name |

## 7. Handoff from Bronze to Silver

The Bronze layer feeds the Silver layer as follows:

| Bronze Input | Silver Output | Silver Action |
|---|---|---|
| `airport_flights_2021.csv` to `airport_flights_2025.csv` | `stg_airport_flights` | Concatenate yearly files, standardize text, parse dates, and type numeric fields |
| `airport_locations_raw.csv` | `stg_airport_geography` | Standardize airport codes, clean location fields, and type coordinates |
| `airport_top250_locations_raw.csv` | `silver_tables_joined` | Define the airport scope used in the joined Silver validation dataset |
| `airport_top250_locations_joined.csv` | `stg_weather_daily` | Provide airport coordinates for Open-Meteo weather extraction |

## 8. Notes

- Weather history from Open-Meteo is created in the Silver layer as `stg_weather_daily.csv`, not stored as a raw Bronze file.
