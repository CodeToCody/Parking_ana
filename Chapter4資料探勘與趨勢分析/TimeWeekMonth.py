# 分時段、分星期、分月份的停車需求變化
import pandas as pd
import os
from tqdm import tqdm
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

magic_num = 1
# 0 for notebook
# 1 for desktop

directory = os.getcwd()
output_graph_file = os.path.join(directory,"TimeWeekMonth_chart/")

if magic_num == 0:
    source_path = r"C:/Cody/Research/clean_data/prepare.csv"
elif magic_num == 1:
    source_path = r"D:/Research/clean_data/prepare.csv"
else:
    print("wrong magic num.")
    exit(1)

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
timeline_df["date"] = timeline_df["timestamp"].dt.date                  # 日期
timeline_df["month"] = timeline_df["timestamp"].dt.to_period("M")       # 月份
timeline_df["weekday"] = timeline_df["timestamp"].dt.dayofweek          # 星期幾 (0=一, 6=日)
timeline_df["hour"] = timeline_df["timestamp"].dt.hour                  # 小時


print(timeline_df.head())

plt.rcParams['font.family'] = 'MingLiU'

'''
    1.分月份的停車需求變化 -> 想知道幾月(季節?)會有什麼影響? 
'''
# 繼續使用 timeline_df 的 month 欄位
monthly_avg = timeline_df.groupby("month")["cars_in_parking"].mean().reset_index()
monthly_avg["month_num"] = monthly_avg["month"].dt.month

# 中文月份標籤
month_labels = ["1月", "2月", "3月", "4月", "5月", "6月",
                "7月", "8月", "9月", "10月", "11月", "12月"]
monthly_avg["month_label"] = monthly_avg["month_num"].apply(lambda x: f"{x}月")

# 定義季節顏色
def get_season_color(month):
    if month in [3, 4, 5]:
        return "forestgreen"   # 春
    elif month in [6, 7, 8]:
        return "firebrick"     # 夏
    elif month in [9, 10, 11]:
        return "darkorange"    # 秋
    else:
        return "royalblue"     # 冬

monthly_avg["color"] = monthly_avg["month_num"].apply(get_season_color)

# 畫圖
plt.figure(figsize=(10, 5))
plt.bar(monthly_avg["month_label"], monthly_avg["cars_in_parking"], color=monthly_avg["color"])
plt.ylabel("平均在場車數")
plt.title("各月份平均在場車輛數（季節配色）")
plt.grid(axis='y')
plt.tight_layout()
plt.savefig(output_graph_file + "分月份平均在場車數_季節配色.png", dpi=300)
plt.show()


'''
    2.分星期的停車需求變化 -> 想知道今天星期幾會影響什麼?
'''

# ===== (全部數據) 分星期平均在場車數 =====
weekday_avg = timeline_df.groupby("weekday")["cars_in_parking"].mean()
weekday_labels = ["一", "二", "三", "四", "五", "六", "日"]

plt.figure(figsize=(8, 4))
plt.bar(weekday_labels, weekday_avg, color="gray")
plt.ylabel("平均在場車數")
plt.title("星期幾平均在場車輛數")
plt.grid(axis='y')
plt.tight_layout()
plt.savefig(output_graph_file + "分星期平均在場車數.png", dpi=300)
plt.close()

# ===== 上班時間（08:00–18:00）分星期平均在場車數 =====
# 篩選上班時段
work_time_df = timeline_df[
    (timeline_df["timestamp"].dt.hour >= 8) &
    (timeline_df["timestamp"].dt.hour < 18)
].copy()

work_time_df["weekday"] = work_time_df["timestamp"].dt.weekday

weekday_avg_work = work_time_df.groupby("weekday")["cars_in_parking"].mean().reset_index()
weekday_avg_work["weekday_label"] = weekday_avg_work["weekday"].apply(lambda x: weekday_labels[x])

# 顏色：平日橘、假日藍
bar_colors = ["orange" if i < 5 else "skyblue" for i in weekday_avg_work["weekday"]]

plt.figure(figsize=(8, 4))
plt.bar(weekday_avg_work["weekday_label"], weekday_avg_work["cars_in_parking"], color=bar_colors)
plt.ylabel("平均在場車數")
plt.title("【上班時間】星期幾平均在場車輛數（08:00–18:00）")
plt.grid(axis='y')
plt.tight_layout()
plt.savefig(output_graph_file + "上班時間_分星期平均在場車數.png", dpi=300)
plt.close()


'''
    3.分時段的停車需求變化 -> 想知道每天什麼時段有什麼特別之處?
'''
hourly_avg = timeline_df.groupby("hour")["cars_in_parking"].mean()

plt.figure(figsize=(10, 4))
plt.plot(hourly_avg.index, hourly_avg.values, marker="o", color="green")
plt.xticks(range(0, 24))
plt.xlabel("時間點 (0~23)")
plt.ylabel("平均在場車數")
plt.title("各時段平均在場車輛數")
plt.grid()
plt.tight_layout()
plt.savefig(output_graph_file + "分時段平均在場車數.png", dpi=300)
plt.close()
