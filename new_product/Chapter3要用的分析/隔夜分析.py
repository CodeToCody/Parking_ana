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


df = pd.read_csv(source_path)
df['全時間格式進入時間'] = pd.to_datetime(df['全時間格式進入時間'])
df['全時間格式出場時間'] = pd.to_datetime(df['全時間格式出場時間'])


# 計算停留時間（小時）
df['停留時間_小時'] = (df['全時間格式出場時間'] - df['全時間格式進入時間']).dt.total_seconds() / 3600

# 判斷是否跨日
df['是否跨日'] = df['全時間格式出場時間'].dt.date != df['全時間格式進入時間'].dt.date
df['是否跨夜停車'] =  df['是否跨日']

# 篩選符合條件的資料
long_stay_df = df[df['是否跨夜停車']]

# 匯出明細為 Excel
long_stay_df[['全時間格式進入時間', '全時間格式出場時間', '停留時間_小時']].sort_values(
    by='全時間格式進入時間'
).to_excel("C:/Cody/Research/new_product/Chapter3要用的分析/長時間或隔夜停車明細.xlsx", index=False)

# 畫停留時間直方圖
plt.rcParams["font.family"] = ["DejaVu Sans", "Microsoft JhengHei"]
plt.figure(figsize=(10, 5))
plt.hist(long_stay_df['停留時間_小時'], bins=30, edgecolor='black')
plt.title("長時間或隔夜停車的停留時間分布")
plt.xlabel("停留時間（小時）")
plt.ylabel("車輛數")
plt.grid(True)
plt.tight_layout()
plt.show()

# 指定欲分析的工作日
selected_days = ['2024-04-17', '2024-04-24', '2024-05-08', '2024-05-15']

# 建立統計表
overnight_counts = []
from datetime import timedelta
for day in selected_days:
    day_ts = pd.to_datetime(day)
    next_day_8am = day_ts + timedelta(days=1, hours=8)  # 隔天早上8點

    # 注意：這邊直接與 Timestamp 比，不用 .dt.date
    count = df[
        (df['全時間格式進入時間'].dt.date == day_ts.date()) &  # 這邊是當天進場就好
        (df['全時間格式出場時間'] > next_day_8am)              # 出場時間超過隔天08:00
    ].shape[0]

    overnight_counts.append({'日期': str(day_ts.date()), '隔天08點後離場數量': count})

# 輸出為表格
result_df = pd.DataFrame(overnight_counts)
print(result_df)

# 可選：輸出成 Excel
result_df.to_excel(output_graph_file + "指定日跨夜停車數統計.xlsx", index=False)
