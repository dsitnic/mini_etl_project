# Project Runbook
(TODO) ADD AIRFLOW OPTIONS AND LOAD GOLD SCRIPTS

## Requirements

From the project root run the following to install required packages:

```powershell
pip install -r requirements.txt
```

Other requirements:

- `data/source/top_250_airports_europe_2025.csv`
- internet access for Eurocontrol, OpenFlights, and Open-Meteo
- ODBC Driver 18 for SQL Server if running Azure SQL steps
- Python version 3.14

## Execution Order

### 1. Ingest Bronze data

```powershell
python src\python\ingest_airport_flights.py
python src\python\ingest_airports_source.py
python src\python\ingest_top250_airports.py
```

Creates:

- `data/bronze/airport_flights_2021.csv` through `data/bronze/airport_flights_2025.csv`
- `data/bronze/airport_locations_raw.csv`
- `data/bronze/airport_top250_locations_raw.csv`

### 2. Prepare Silver data

```powershell
python src\python\cleaning_airport_locations.py
python src\python\join_top250_locations.py
python src\python\ingest_weather_data.py
python src\python\clean_weather_data.py
python src\python\clean_airport_flights.py
```

Creates:

- `data/silver/stg_airport_geography.csv`
- `data/bronze/airport_top250_locations_joined.csv`
- `data/silver/stg_weather_daily.csv`
- `data/silver/stg_weather_daily_clean.parquet`
- `data/silver/stg_airport_flights.parquet`

### 3. Join Silver data

```powershell
python src\python\validation_joins.py
```

Creates:

- `data/silver/silver_tables_joined.parquet`

### 4. Create Gold tables

Run this SQL script against Azure SQL:

```text
src/sql/create_tables_script.sql
```

Creates:

- `gold.dim_date`
- `gold.dim_airport`
- `gold.fact_flights`

There is currently no script that loads `silver_tables_joined.parquet` into the Gold tables.
