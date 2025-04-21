import os 
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
from datetime import datetime, timedelta
# plotly

source_path = r"C:\Cody\Research\clean_data\prepare.csv"
data = pd.read_csv(source_path)

data["全時間格式進入時間"] = pd.to_datetime(data["全時間格式進入時間"])
data["全時間格式出場時間"] = pd.to_datetime(data["全時間格式出場時間"])
data["進入日"] = pd.to_datetime(data["進入日"])
data["出場日"] = pd.to_datetime(data["出場日"])


bounded_data = data[(data["進入日"] >= "2024-01-01") & (data["進入日"] <= "2024-12-31")]

bounded_data.to_csv("C:\Cody\Research\實驗區\check.csv",index=False)

time_index = pd.date_range(start="2024-01-01 00:00:00",end="2024-12-31 23:00:00",freq="h")

weekday_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

columns = ["Weekday","In","Out","Stay"]

Table = pd.DataFrame(0,index=time_index,columns=columns)

# 0 表示星期一 6表示星期日
Table["Weekday"] = Table.index.weekday


skipped_count = 0
# iterrows會返回 tuple -> (index, row) ，所以這樣指定才能對 row 做操作
# 直接給一個參數會變成一個 tuple
for _,row in tqdm(bounded_data.iterrows(),total=len(bounded_data),desc="處理停車紀錄"):
    start_time = row["全時間格式進入時間"]
    end_time = row["全時間格式出場時間"]
    entry_date = row["進入日"]
    # 跳過無效記錄
    if pd.isna(start_time) or pd.isna(end_time):
        skipped_count += 1
        # tqdm.write(f"警告：車號 {row.get('車號', '票種')} 無時間，跳過")
        continue
    
    # 檢查出場時間是否早於進入時間
    if end_time <= start_time:
        skipped_count += 1
        # tqdm.write(f"警告：車號 {row.get('車號', '票種')} 出場時間異常，跳過")
        continue

    # 計算停留時間
    temp = end_time - start_time
    
    # 確定進場和出場的小時
    start_hour = start_time.floor('h')
    end_hour = end_time.floor('h')
    
    # 短停留記錄（小於1小時）
    if temp < pd.Timedelta(hours=1):
        # tqdm.write(f"短停留記錄：車號 {row.get('車號', '未知')}，停留 {temp}")
        if start_hour in Table.index:
            tqdm.write(f"短停留記錄：車號 {row.get('車號', '未知')}，進入時間紀錄於{start_hour}")
            Table.loc[start_hour, "In"] += 1
        if end_hour in Table.index:
            tqdm.write(f"短停留記錄：車號 {row.get('車號', '未知')}，出場時間紀錄於{end_hour}")
            Table.loc[end_hour, "Out"] += 1
        continue  # 短停留不計入 Stay
    
    # 正常記錄的處理
    if start_hour in Table.index:
        tqdm.write(f"停留記錄：車號 {row.get('車號', '未知')}，入場時間紀錄於{start_hour}")
        Table.loc[start_hour, "In"] += 1
    if end_hour in Table.index:
        tqdm.write(f"停留記錄：車號 {row.get('車號', '未知')}，出場時間紀錄於{end_hour}")
        Table.loc[end_hour, "Out"] += 1
    
    # 記錄停留
    current_hour = start_hour
    while current_hour <= end_hour and current_hour in Table.index:
        Table.loc[current_hour, "Stay"] += 1
        current_hour += timedelta(hours=1)  # 使用 timedelta

Table.to_csv(r"C:\Cody\Research\實驗區\final_table.csv")

plt.rcParams["font.sans-serif"] = ["Microsoft JhengHei"]
plt.rcParams["axes.unicode_minus"] = False
output_chart_dir = r"實驗區"
# 繪製折線圖
plt.figure(figsize=(12, 4))
sns.lineplot(x=Table.index, y=Table["Stay"], label='總停留車輛')
plt.axhline(1475, color='red', linestyle='--', label='容量上限1475')
plt.title('全')
plt.xlabel('時間')
plt.ylabel('車輛數')
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(output_chart_dir, 'all_graph.png'), dpi=300)

print(f"✅ 趨勢圖已儲存於：{output_chart_dir}")