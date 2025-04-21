from tqdm import tqdm
import pandas as pd
import os
import matplotlib.pyplot as plt



here = os.getcwd()
source_data_location = os.path.join(here,r"Report_sheet/工作日統計_8月前.csv")

source_data = pd.read_csv(source_data_location)
source_data["全時間格式進入時間"] = pd.to_datetime(source_data["全時間格式進入時間"])
source_data["全時間格式出場時間"] = pd.to_datetime(source_data["全時間格式出場時間"])


# 建立時段 index（每小時一筆）
time_index = pd.date_range(start="2024-01-01 00:00:00", end="2024-07-31 23:00:00", freq="h")
in_parking_count = pd.Series(0, index=time_index)  # 每小時場內車輛數量初始化為 0

# 跑每一筆記錄，依照車輛實際停留的每個小時 +1
for _, row in tqdm(source_data.iterrows(), total=len(source_data), desc="建立場內車輛統計"):
    start_time = row["全時間格式進入時間"]
    end_time = row["全時間格式出場時間"]

    # 資料清理
    if pd.isna(start_time) or pd.isna(end_time):
        continue
    if end_time <= start_time:
        continue
    if (end_time - start_time) < pd.Timedelta(seconds=60):
        continue

    # 將車輛實際在場的每一小時記錄下來（只要那一小時開始時還在就算）
    start_hour = start_time.floor("h")
    end_hour = end_time.floor("h")  # 不進位、不四捨五入

    # 所有整點時刻的車輛停在校內
    duration_hours = pd.date_range(start=start_hour, end=end_hour - pd.Timedelta(hours=1), freq="h")
    for hour in duration_hours:
        if hour in in_parking_count.index:
            in_parking_count[hour] += 1


plt.rcParams["font.sans-serif"] = ["Microsoft JhengHei"]
plt.rcParams["axes.unicode_minus"] = False
plt.figure(figsize=(15, 5))
in_parking_count.plot()
plt.axhline(1475, color='red', linestyle='--', label='停車格上限（1475）')
plt.title('每小時場內實際停放車輛數')
plt.xlabel('時間')
plt.ylabel('車輛數')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
