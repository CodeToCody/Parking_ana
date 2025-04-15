from datetime import datetime, timedelta
import pandas as pd
from tqdm import tqdm
import os 


here = os.getcwd()
source_data_location = os.path.join(here,"clean_data\prepare.csv")
output_data_location = os.path.join(here,"temp_file\sample.csv")


# make a sheet with defined format
time_index = pd.date_range(start="2024-01-01 00:00:00",end="2024-12-31 23:00:00",freq="h")

# define the weekday's name
weekday_names = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
columns = []


for weekday in weekday_names:
    for suffix in ['進','出','停留']:
        columns.append(f'{weekday}_{suffix}')



source_data = pd.read_csv(source_data_location)
source_data["全時間格式進入時間"] = pd.to_datetime(source_data["全時間格式進入時間"])
source_data["全時間格式出場時間"] = pd.to_datetime(source_data["全時間格式出場時間"])

# 檢查數據
print("數據預覽:")
print(source_data.head())
print("缺失值檢查:")
print("進入時間缺失:", source_data["全時間格式進入時間"].isna().sum())
print("出場時間缺失:", source_data["全時間格式出場時間"].isna().sum())

# create the table
hash_table = pd.DataFrame(0,index=time_index,columns=columns)

skipped_count = 0
for _,row in tqdm(source_data.iterrows(), total=len(source_data),desc="處理停車記錄"):
    start_time = row["全時間格式進入時間"]
    end_time = row["全時間格式出場時間"]

    # 跳過無效記錄
    if pd.isna(start_time) or pd.isna(end_time):
        skipped_count += 1
        continue
    # 檢查出場時間是否早於進入時間
    if end_time < start_time:
        skipped_count += 1
        tqdm.write(f"警告：車號 {row.get('車號', '未知')} 出場時間 {end_time} 早於進入時間 {start_time}，跳過")
        continue
    # 進
    entry_hour = start_time.floor('h') # ex 將 13:24:25 變成 13:00:00
    entry_weekday = weekday_names[entry_hour.weekday()]
    if entry_hour in hash_table.index:
        hash_table.at[entry_hour, f"{entry_weekday}_進"] += 1

    # 出
    exit_hour = end_time.floor('h')
    exit_weekday = weekday_names[exit_hour.weekday()]
    if exit_hour in hash_table.index:
        hash_table.at[exit_hour, f"{exit_weekday}_出"] += 1

hash_table.to_excel(os.path.join(here,"temp_file/sample_sheet.xlsx"))

### 分析總車次

### 分時車次

### 停車數量

### 平均停留時間

### 各項票種使用狀況