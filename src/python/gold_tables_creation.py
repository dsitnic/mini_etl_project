from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus


# 1. connection parameters
load_dotenv()

server = os.getenv("DB_SERVER")
database = os.getenv("DB_DATABASE")
username = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")
driver = os.getenv("DB_DRIVER")

# 2. connection url
params = quote_plus(
    f"DRIVER={driver};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"UID={username};"
    f"PWD={password};"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=30;"
)

# 3. create sqlalchemy engine
# 'mssql+pyodbc:///?odbc_connect='
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

print("connection configured")

sql_script = """
IF NOT EXISTS (
    SELECT 1
    FROM sys.schemas
    WHERE name = 'gold'
)
BEGIN
    EXEC('CREATE SCHEMA gold');
END;

DROP TABLE IF EXISTS gold.fact_flights;
DROP TABLE IF EXISTS gold.dim_airport;
DROP TABLE IF EXISTS gold.dim_date;

CREATE TABLE gold.dim_date (
    date_key INT PRIMARY KEY,
    [date] DATE NOT NULL,
    [year] INT NOT NULL,
    [quarter] TINYINT,
    [month_num] TINYINT NOT NULL,
    [week_of_year] TINYINT,
    [day_of_month] TINYINT,
    [day_of_week] TINYINT,
    [month_name] VARCHAR(20),
    [month_short] CHAR(3),
    [year_month] CHAR(7),
    [day_name] VARCHAR(10),
    [is_weekend] BIT,
    [season] VARCHAR(10)
);

CREATE TABLE gold.dim_airport (
    airport_key INT PRIMARY KEY,
    airport_name NVARCHAR(250),
    icao_code CHAR(4) NOT NULL UNIQUE,
    iata_code CHAR(3) UNIQUE,
    country NVARCHAR(250),
    city NVARCHAR(250),
    latitude FLOAT,
    longitude FLOAT
);

CREATE TABLE gold.fact_flights (
    flight_key INT PRIMARY KEY,
    date_key INT NOT NULL,
    departure_apt_key INT NOT NULL,
    departures INT,
    departures_delay_m FLOAT,
    temperature_2m_mean FLOAT,
    precipitation_sum FLOAT,
    wind_speed_10m_max FLOAT,

    CONSTRAINT FK_fact_flights_dim_date
        FOREIGN KEY (date_key)
        REFERENCES gold.dim_date(date_key),

    CONSTRAINT FK_fact_flights_dim_airport
        FOREIGN KEY (departure_apt_key)
        REFERENCES gold.dim_airport(airport_key)
);
"""

with engine.begin() as conn:
    conn.execute(text(sql_script))

print("Gold schema and tables created successfully.")