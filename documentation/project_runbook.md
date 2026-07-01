# Project Runbook

## 1. Requirements

From the project root, install the required Python packages:

```powershell
pip install -r requirements.txt
```

Other requirements:

- `data/source/top_250_airports_europe_2025.csv`
- internet access for EuroControl, OpenFlights, and Open-Meteo
- ODBC Driver 18 for SQL Server when running Azure SQL steps
- database connection values in `.env` for Gold table creation and loading

## 2. Execution Order

### 2.1 Ingest Bronze Data

```powershell
python src\python\ingest_airport_flights.py
python src\python\ingest_airports_source.py
python src\python\ingest_top250_airports.py
```

Creates:

| Output | Description |
|---|---|
| `data/bronze/airport_flights_2021.csv` to `data/bronze/airport_flights_2025.csv` | Raw EuroControl yearly flight files with ingestion metadata |
| `data/bronze/airport_locations_raw.csv` | Raw OpenFlights airport location file with ingestion metadata |
| `data/bronze/airport_top250_locations_raw.csv` | Top 250 airport scope file with ingestion metadata |

### 2.2 Prepare Silver Staging Data

```powershell
python src\python\clean_airport_locations.py
python src\python\join_top250_locations.py
python src\python\ingest_weather_data.py
python src\python\clean_weather_data.py
python src\python\clean_airport_flights.py
```

Creates:

| Output | Description |
|---|---|
| `data/silver/stg_airport_geography.csv` | Cleaned airport geography staging data |
| `data/bronze/airport_top250_locations_joined.csv` | Top 250 airport scope file enriched with coordinates |
| `data/silver/stg_weather_daily.csv` | Open-Meteo daily weather extract |
| `data/silver/stg_weather_daily_clean.parquet` | Cleaned daily weather staging data |
| `data/silver/stg_airport_flights.parquet` | Cleaned and concatenated airport flight staging data |

### 2.3 Join Silver Data

```powershell
python src\python\validation_joins.py
```

Creates:

| Output | Description |
|---|---|
| `data/silver/silver_tables_joined.parquet` | Joined Silver dataset used for validation |

### 2.4 Validate Silver Data

```powershell
python src\python\validate_silver.py
```

Creates:

| Output | Description |
|---|---|
| `data/silver/valid_rows.csv` | Rows that passed Silver validation and are loaded to Gold |
| `data/silver/review_rows.csv` | Rows that failed one or more Silver validation checks |
| `data/silver/metric_summary.csv` | Validation row-count summary |
| `data/silver/review_summary.csv` | Grouped validation review reasons |

### 2.5 Create Gold Tables

```powershell
python src\python\gold_tables_creation.py
```

Creates:

| Gold Table | Description |
|---|---|
| `gold.dim_date` | Date dimension |
| `gold.dim_airport` | Airport dimension |
| `gold.fact_flights` | Flight and weather fact table |

### 2.6 Load Gold Tables

```powershell
python src\python\data_loading_to_gold.py
```

Loads `data/silver/valid_rows.csv` into:

| Gold Table | Source |
|---|---|
| `gold.dim_date` | Distinct dates from `valid_rows.csv` |
| `gold.dim_airport` | Distinct airports from `valid_rows.csv` |
| `gold.fact_flights` | Valid flight/weather rows from `valid_rows.csv` |

Gold fact notes:

- `gold.fact_flights.departures` is populated from Silver `departures_data_submitted`.
- `gold.fact_flights.departures_delay_m` is populated from Silver `delay_minutes`.

## 3. Validation Checks

After running the pipeline, check:

```powershell
Get-Content data\silver\metric_summary.csv
```

Expected current validation summary:

| Metric | Current Value |
|---|---:|
| `silver_tables_joined` rows | 448,423 |
| `valid_rows` rows | 159,516 |
| `review_rows` rows | 288,907 |

## 4. Notes

- Run commands from the project root.
- Weather extraction can take time because `ingest_weather_data.py` calls the Open-Meteo archive API in batches.
- Gold scripts require a working SQL Server connection through environment variables.
- Layer documentation is in `documentation/bronze_layer_documentation.md` and `documentation/silver_layer_documentation.md`.
- Column-level details are in `documentation/data_dictionary.md`.
