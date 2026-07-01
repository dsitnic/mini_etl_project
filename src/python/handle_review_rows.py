import pandas as pd
from pathlib import Path
import pandas as pd

# create folder paths
silver_folder = Path(".") / "data" / "silver"

# read review rows
review_rows = pd.read_csv(silver_folder / "review_rows.csv")

# reasons to reject
reason1= """MISSING_DEPARTURES_DATA_SUBMITTED; MISSING_DELAY_MINUTES; """
reason2 = """MISSING_DATE; MISSING_AIRPORT_NAME; MISSING_ICAO; MISSING_COUNTRY; MISSING_LATITUDE; MISSING_LONGITUDE; MISSING_DEPARTURES; MISSING_DEPARTURES_DATA_SUBMITTED; MISSING_DELAY_MINUTES; MISSING_TEMPERATURE_2M_MEAN; MISSING_PRECIPITATION_SUM; MISSING_WIND_SPEED_10M_MAX; INVALID_LONGITUDE; INVALID_LATITUDE; INVALID_TEMPERATURE; INVALID_PRECIPITATION; INVALID_WINDSPEED; INVALID_DATE; INVALID_ICAO_LENGTH; """

# get rejected rows
rejected_rows = review_rows.loc[review_rows["review_reason"].isin([reason1, reason2])]

# write file
rejected_rows.to_csv(silver_folder / "rejected_rows.csv", index=False)