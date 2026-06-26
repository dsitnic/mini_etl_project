# ✈️ European Flight Delays & Weather Analytics
**Data Engineering Program - Week 8 Mini-Project**

## 📖 Project Overview
This project is an end-to-end Data Engineering ETL/ELT pipeline that investigates the correlation between historical weather conditions and flight arrival delays across European airports. 

**The Business Question:** > *"How do historical weather conditions (rain, snow, wind speed) correlate with reported weather-related delays at major airports, and how does this affect overall arrival performance?"*

This repository contains the Python scripts, Jupyter Notebooks, data validation logic, and documentation used to extract, load, and transform the data into a Star Schema ready for Power BI reporting.

---

## 🏗️ Architecture & Pipeline (Medallion)
We implemented a strict **Medallion Architecture** to process the data from raw inputs to reporting-ready formats:

* 🥉 **Bronze Layer (Raw):** Raw data ingestion. Data is stored exactly as it arrives from the external sources (CSVs and JSON API responses) with an added `load_timestamp`.
* 🥈 **Silver Layer (Cleaned & Validated):** Data is cleaned using Python/Pandas. Dates are standardized, API JSON is parsed and aggregated to a daily grain, missing values are handled, and invalid rows (e.g., negative delay minutes) are routed to a "Rejected" table.
* 🥇 **Gold Layer (Modeled):** Business-level transformations into a Star Schema. 
    * **Fact Table:** `Fact_Airport_Delays` (Daily delays by airport and reason).
    * **Dimension Tables:** `Dim_Airport` (Location metadata) & `Dim_Weather` (Daily weather metrics).

---

## 🗄️ Data Sources
1.  **ANS Performance (Flight Delays):** [ansperformance.eu](https://ansperformance.eu/data/)
    * Format: CSV 
    * Content: Daily aggregate flight arrivals and specific delay causes by ICAO airport code.
2.  **Open-Meteo API (Historical Weather):** [open-meteo.com](https://open-meteo.com/en/docs/historical-weather)
    * Format: REST API (JSON)
    * Content: Historical hourly weather data (aggregated to daily in our pipeline) based on airport coordinates.
3.  **Global Airport Database (Mapping):** *(Used for Enrichment)*
    * Format: CSV
    * Content: Maps `ICAO` codes from the flight data to `Latitude` and `Longitude` required to query the Weather API.

---

## 🛠️ Tech Stack & Tools
* **Language:** Python (Pandas, Requests, JSON)
* **Storage/Architecture:** Local File System structured via Medallion (Bronze, Silver, Gold folders)
* **Reporting:** Power BI (Connected strictly to the Gold layer)
* **Version Control:** Git & GitHub
* **Project Management:** Trello (Scrum Kanban Board)

---

## 👥 Team & Agile Methodology
We use Scrum methodology to track progress. Our backlog and sprint tasks are managed via a **Trello Kanban Board**. 

To satisfy project requirements, **every team member contributed to Python data ingestion, cleaning, or validation.**

* **[Team Member 1 Name]:** Data Engineer (Flight Data Ingestion & Bronze-to-Silver cleaning).
* **[Team Member 2 Name]:** Data Engineer (Airport Dictionary parsing & mapping standardizations).
* **[Team Member 3 Name]:** Data Engineer (Open-Meteo API integration & JSON parsing).
* **[Team Member 4 Name]:** Analytics Engineer (Silver-to-Gold joins, Validation logic, Power BI Modeling).

---

## 🚀 Runbook: How to Execute the Pipeline
Follow these steps to run the ETL pipeline from end to end:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME.git)
    cd YOUR_REPO_NAME
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Ingestion Script (Bronze):**
    ```bash
    python src/1_ingest_bronze.py
    ```
    *Extracts CSVs and pulls API data into the `/data/bronze/` directory.*

4.  **Run the Cleaning & Validation Script (Silver):**
    ```bash
    python src/2_clean_silver.py
    ```
    *Cleans data, drops duplicates, unpivots columns, and generates validation logs in `/data/silver/`.*

5.  **Run the Modeling Script (Gold):**
    ```bash
    python src/3_model_gold.py
    ```
    *Joins tables and outputs the final Fact and Dimension tables to `/data/gold/`.*

6.  **View the Report:**
    * Open `reports/Flight_Weather_Dashboard.pbix` in Power BI Desktop to view the dashboard connected to the Gold data.

---

## 🛡️ Data Quality & Validation
Our Silver layer pipeline includes explicit data quality checks:
* Validation that `FLT_DATE` falls within the expected bounds.
* Check for orphaned ICAO codes (airports in the flight data missing from the coordinate mapping).
* Rejection of rows with negative delay minutes.
* Validation summaries and rejected rows are outputted to `data/silver/rejected_rows.csv` for auditing.
