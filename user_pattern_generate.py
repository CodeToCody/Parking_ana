from datetime import datetime, timedelta
import pandas as pd
from tqdm import tqdm
import os 


here = os.getcwd()
source_data_location = os.path.join(here,"clean_data/prepare.csv")
output_data_location = os.path.join(here,"temp_file/sample.csv")




# make a sheet with defined format
time_index = pd.date_range(start="2024-01-01 00:00:00",end="2024-12-31 23:00:00",freq="h")

# define the weekday's name
weekday_names = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
columns = []


for weekday in weekday_names:
    for suffix in ['進','出','停留']:
        columns.append(f'{weekday}_{suffix}')

# print(columns)

source_data = pd.read_csv(source_data_location)

print(source_data.head())
