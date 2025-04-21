from datetime import datetime, timedelta
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt
import os 


here = os.getcwd()
source_data_location = os.path.join(here,r"Report_sheet/工作日統計_8月前.csv")


# make a table with time index (column direction)
# time_index = pd.date_range(start="2024-08-01 00:00:00",end="2024-12-31 23:00:00",freq="h")
time_index = pd.date_range(start="2024-01-01 00:00:00",end="2024-07-31 23:00:00",freq="h")

# define the weekday's name (row definition)
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
record_table = pd.DataFrame(0,index=time_index,columns=columns)

skipped_count = 0
for _,row in tqdm(source_data.iterrows(), total=len(source_data),desc="處理停車記錄"):
    start_time = row["全時間格式進入時間"]
    end_time = row["全時間格式出場時間"]

    # 跳過無效記錄
    if pd.isna(start_time) or pd.isna(end_time):
        skipped_count += 1
        continue
    # 檢查出場時間是否早於進入時間
    if end_time <= start_time:
        skipped_count += 1
        tqdm.write(f"警告：車號 {row.get('車號', '票種')} 出場時間 {end_time} 早於或等於進入時間 {start_time}，跳過")
        continue

    # 檢查異常情況
    if (end_time - start_time) < pd.Timedelta(seconds=60):
        skipped_count += 1
        tqdm.write(f"警告：車號 {row.get('車號', '票種')} 停留小於60秒，跳過")
        continue

    # 進
    entry_hour = start_time.floor('h') # ex 將 13:24:25 變成 13:00:00
    entry_weekday = weekday_names[entry_hour.weekday()]
    if entry_hour in record_table.index:
        record_table.at[entry_hour, f"{entry_weekday}_進"] += 1

    # 出
    exit_hour = end_time.floor('h')
    exit_weekday = weekday_names[exit_hour.weekday()]
    if exit_hour in record_table.index:
        record_table.at[exit_hour, f"{exit_weekday}_出"] += 1

    # 停留時間
    # 00:30:00 不是datetime.timedelta 合法的時間間隔物件 : pd.Timedelta(minutes=30)
    # 判斷是否出場時間超過 exit_hour 的 30 分鐘
    # if (end_time - exit_hour) >= pd.Timedelta(minutes=30):
    #     duration_hours = pd.date_range(entry_hour, exit_hour, freq="h")  # 包含最後小時
    # else:
    #     duration_hours = pd.date_range(entry_hour, exit_hour - pd.Timedelta(hours=1), freq="h")  # 不含最後小時

    start_floor = start_time.floor('h')
    end_floor = end_time.floor('h')
    if end_floor - start_floor < pd.Timedelta(hours=1):
        continue
    duration_hours = pd.date_range(start=start_floor, end=end_floor - pd.Timedelta(hours=1), freq='h')

    # 記錄停留欄位 +1
    for stay_hour in duration_hours:
        stay_weekday = weekday_names[stay_hour.weekday()]
        col_name = f"{stay_weekday}_停留"
        if col_name in record_table.columns and stay_hour in record_table.index:
            record_table.at[stay_hour, col_name] += 1


print(f"總共跳過異常或不合法紀錄數：{skipped_count}")
record_table.to_excel(os.path.join(here,"temp_file/sample_sheet_first.xlsx"))

record_table['總停留數'] = record_table[[c for c in record_table.columns if '_停留' in c]].sum(axis=1)
record_table['總停留數'].plot(figsize=(14, 4), title="每小時總停留車輛數")




plt.rcParams["font.sans-serif"] = ["Microsoft JhengHei"]
plt.rcParams["axes.unicode_minus"] = False
plt.axhline(1475, color='red', linestyle='--', label='停車位上限')
plt.legend()
plt.show()

### 分析總車次

### 分時車次

### 停車數量

### 平均停留時間

### 各項票種使用狀況