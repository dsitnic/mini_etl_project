# %%
import urllib
from sqlalchemy import create_engine
import pandas as pd
import platform
import getpass
from datetime import datetime

# %%
# 1. connection parameters
server = 'mini-etl-project-server.database.windows.net'
database = 'mini-etl-project-db'
username = 'sqladmin'
password = 'SQL.is.cool' 




# use driver
driver = '{ODBC Driver 18 for SQL Server}'

# %%
# 2. connection url
params = urllib.parse.quote_plus(
    f"DRIVER={driver};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"UID={username};"
    f"PWD={password};"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"  # Wichtig für Azure-Sicherheit
    "Connection Timeout=30;"
)

# params "Driver={ODBC Driver 18 for SQL Server};Server=tcp:mini-etl-project-server.database.windows.net,1433;Database=mini-etl-project-db;Uid=sqladmin;Pwd={SQL.is.cool.1};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"

# %%
# 3. create sqlalchemy engine
# 'mssql+pyodbc:///?odbc_connect='
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

print("connection configurated")

# %%
# create a test dataframe
user = getpass.getuser()    # username
os = platform.system()      # Windows, Darwin (macOS) or Linux
timestamp = datetime.now()  # timestamp

data = {
    'username': [user],
    'os': [os],
    'timestamp': [timestamp]
}
df = pd.DataFrame(data)

# format as datetime
df['timestamp'] = pd.to_datetime(df['timestamp'])

print("Following datafram will be written to the database:")
print(df)

# append data to the azure test table
df.to_sql(
    name='test_table', 
    con=engine, 
    schema='dbo', 
    if_exists='append',  # <-- 'append' 
    index=False
)

print("\nData successfully written")

readback = pd.read_sql("select * from dbo.test_table", engine)
print("\nreadback of test_table:")
print(readback)
