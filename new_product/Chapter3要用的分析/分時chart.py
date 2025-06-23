import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# 設定環境
magic_num = 0
# laptop = 0
# desktop = 1
if magic_num == 0:
    source_path = r"C:/Cody/Research/clean_data/prepare.csv"
    output_graph_file = r"C:/Cody/Research/new_product/Chapter3要用的分析/"
elif magic_num == 1:
    source_path = r"D:/Research/clean_data/prepare.csv"
    output_graph_file = r"D:/Research/new_product/Chapter3要用的分析/"
else:
    print("wrong magic num.")
    exit(1)

# 時段從 08:00 到 18:00，每 30 分鐘為單位
results = {}
time_labels = []

# 載入資料
df = pd.read_csv(source_path)
df['全時間格式進入時間'] = pd.to_datetime(df['全時間格式進入時間'])
df['全時間格式出場時間'] = pd.to_datetime(df['全時間格式出場時間'])

# 選出 4 月和 5 月的工作日
selected_days = ['2024-04-17', '2024-04-24', '2024-05-08', '2024-05-15']  
results = {}

for day in selected_days:
    # 建立半小時時間區間
    time_range = pd.date_range(start=f'{day} 08:00:00', end=f'{day} 18:00:00', freq='30min')
    count_per_halfhour = []

    for start_time in time_range:
        end_time = start_time + pd.Timedelta(minutes=30)

        # 有進來但還沒出去的車：進場時間 <= end_time, 且 出場時間 > start_time
        count = df[
            (df['全時間格式進入時間'] <= end_time) &
            (df['全時間格式出場時間'] > start_time)
        ].shape[0]
        count_per_halfhour.append(count)

        # 儲存 label（僅第一次儲存一次）
        if day == selected_days[0]:
            time_labels.append(start_time.strftime("%H:%M"))

    results[day] = count_per_halfhour

# 畫圖
plt.rcParams["font.family"] = ["DejaVu Sans", "Microsoft JhengHei"]
plt.figure(figsize=(14, 6))
for day, counts in results.items():
    plt.plot(time_labels, counts, marker='o', label=day)

plt.axhline(y=1475, color='red', linestyle='--', label='停車格上限 1475')
plt.title("校園在場車輛數（每 30 分鐘）")
plt.xlabel("時間")
plt.ylabel("在場車輛數")
plt.xticks(rotation=45)
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

time_range_labels = []
results_dict = {}

# 統計每半小時在場車輛數
for day in selected_days:
    time_range = pd.date_range(start=f'{day} 08:00:00', end=f'{day} 18:00:00', freq='30min')
    counts = []

    for start_time in time_range:
        end_time = start_time + pd.Timedelta(minutes=30)
        count = df[
            (df['全時間格式進入時間'] <= end_time) &
            (df['全時間格式出場時間'] > start_time)
        ].shape[0]
        counts.append(count)

        if day == selected_days[0]:
            label = f"{start_time.strftime('%H:%M')}–{end_time.strftime('%H:%M')}"
            time_range_labels.append(label)

    results_dict[day] = counts

# 建立結果表格
result_df = pd.DataFrame(results_dict, index=time_range_labels)

# 匯出成 Exce
result_df.to_excel("C:/Cody/Research/new_product/Chapter3要用的分析/在場車輛統計表.xlsx")
