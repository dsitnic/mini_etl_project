-- Create schema and tables scripts (FactFlights, DimDate, DimGeography)


-- Create "gold" schema
IF NOT EXISTS (
    SELECT 1
    FROM sys.schemas
    WHERE name = 'gold'
)
BEGIN
    EXEC('CREATE SCHEMA gold');
END;



-- Drop tables, if exist
DROP TABLE IF EXISTS gold.fact_flights;
DROP TABLE IF EXISTS gold.dim_airport;
DROP TABLE IF EXISTS gold.dim_date;

-- DimDate
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

-- DimAirport
CREATE TABLE gold.dim_airport (
    airport_key INT PRIMARY KEY,
    airport_name NVARCHAR(250),
    icao_code CHAR(4) NOT NULL UNIQUE,
    iata_code CHAR(3) UNIQUE,
    region NVARCHAR(50),
    country NVARCHAR(250),
    city NVARCHAR(250),
    latitude FLOAT,
    longitude FLOAT
);

-- FactFlights
CREATE TABLE gold.fact_flights (
    flight_key INT PRIMARY KEY,
    date_key INT NOT NULL,
    departure_apt_key INT NOT NULL,
    departures INT,
    total_departures_delay_m FLOAT,
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