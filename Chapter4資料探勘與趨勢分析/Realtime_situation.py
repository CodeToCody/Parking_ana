# 實際停放車輛與停車格上限關係
import pandas as pd
import os
from tqdm import tqdm
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

magic_num = 0
# 0 for notebook
# 1 for desktop

directory = os.getcwd()
output_graph_file = os.path.join(directory,"Realtime_situation_chart/")

if magic_num == 0:
    source_path = r"C:/Cody/Research/clean_data/prepare.csv"
elif magic_num == 1:
    source_path = r"D:/Research/clean_data/prepare.csv"
else:
    print("wrong magic num.")
    exit(1)

# Topic 資源使用率分析

df = pd.read_csv(source_path)

# 將時間字串轉為 datetime
df["in_time"] = pd.to_datetime(df["全時間格式進入時間"])
df["out_time"] = pd.to_datetime(df["全時間格式出場時間"])

# 建立一個時間區間字典：{時間戳: 場內車數}
time_changes = {}

for _, row in tqdm(df.iterrows(), total=len(df), desc="建立差分時間點"):
    in_time = row["in_time"]
    out_time = row["out_time"]
    # 差分操作
    time_changes[in_time] = time_changes.get(in_time, 0) + 1
    time_changes[out_time] = time_changes.get(out_time, 0) - 1

# 將所有時間點排序後累加
timeline = []
count = 0
for time_point in tqdm(sorted(time_changes.keys()), desc="累加計算在場車輛數"):
    count += time_changes[time_point]
    timeline.append((time_point, count))

# 轉為 DataFrame
timeline_df = pd.DataFrame(timeline, columns=["timestamp", "cars_in_parking"])


plt.rcParams['font.family'] = 'Microsoft JhengHei'

# 視覺化 折線圖
plt.figure(figsize=(16, 5))
plt.plot(timeline_df["timestamp"], timeline_df["cars_in_parking"], label="在場車輛數")
plt.axhline(y=1475, color='red', linestyle='--', label="停車格上限 1475")
plt.xlabel("時間")
plt.ylabel("在場車數")
plt.title("停車場在場車輛即時變化")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(output_graph_file + "_全年停車狀況折線圖.png", dpi=300)  # 儲存圖表為 PNG 高畫質


print("折線分析圖片已儲存")
plt.show()


# 長條圖 每日最大在場車數
# 依日期取最大值（每一天）
daily_max = timeline_df.groupby(timeline_df["timestamp"].dt.date)["cars_in_parking"].max()
daily_max = daily_max.reset_index()
daily_max["date"] = pd.to_datetime(daily_max["timestamp"])
daily_max["month"] = daily_max["date"].dt.to_period("M")  # 加上月份欄位

# 依月份分組畫圖
for month, group in daily_max.groupby("month"):
    plt.figure(figsize=(16, 4))

    # 設定顏色，週一到週五用橘色，週末用天藍色
    colors = ["orange" if date.weekday() < 5 else "skyblue" for date in group["date"]]


    plt.bar(group["date"].dt.strftime("%Y-%m-%d"), group["cars_in_parking"], color=colors)
    plt.axhline(1475, color="red", linestyle="--", label="上限")
    plt.title(f"{month} 每日最大在場車輛數")
    plt.ylabel("車輛數")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()

    # 建立每月圖檔名稱，例如 "2024-03_每日最大在場車數.png"
    output_file = f"{output_graph_file}_{month}_每日最大在場車數.png"
    plt.savefig(output_file, dpi=300)
    plt.close()



