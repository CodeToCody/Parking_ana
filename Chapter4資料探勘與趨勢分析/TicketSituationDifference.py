# 票種使用比例與使用行為差異 <br/>ex.短時vs長時
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import time
from tqdm import tqdm

# 設定環境
magic_num = 1
# laptop = 0
# desktop = 1
if magic_num == 0:
    source_path = r"C:/Cody/Research/clean_data/prepare.csv"
    output_graph_file = r"C:/Cody/Research/Chapter4資料探勘與趨勢分析/TicketSituationDifference_chart/"
elif magic_num == 1:
    source_path = r"D:/Research/clean_data/prepare.csv"
    output_graph_file = r"D:/Research/Chapter4資料探勘與趨勢分析/TicketSituationDifference_chart/"
else:
    print("wrong magic num.")
    exit(1)


data = pd.read_csv(source_path)
data["全時間格式進入時間"] = pd.to_datetime(data["全時間格式進入時間"], errors="coerce")
data["全時間格式出場時間"] = pd.to_datetime(data["全時間格式出場時間"], errors="coerce")
# 移除時間缺失與異常值
data = data.dropna(subset=["全時間格式進入時間", "全時間格式出場時間"])
data = data[data["全時間格式出場時間"] > data["全時間格式進入時間"]]

# 新增時間欄位
data["進場日期"] = data["全時間格式進入時間"].dt.date
data["出場日期"] = data["全時間格式出場時間"].dt.date
data["出場時間"] = data["全時間格式出場時間"].dt.time
data["進場時間"] = data["全時間格式進入時間"].dt.time
data["是否工作日"] = data["全時間格式進入時間"].dt.weekday < 5



# 1. 分票種
tag = data["票種"].unique()
print(tag)
ticket_directory = {}



'''
    2. 過夜情況統計
    a. 定義"過夜" -> 出場日為進場日之後之某日早上8.之後
'''
overnight_mask = (data["出場日期"] > data["進場日期"]) & (data["全時間格式出場時間"].dt.time > time(8, 0))
data["是否過夜"] = overnight_mask

# 統計結果儲存用
result_summary = []

for each_cat in tag:
    temp_df = data[data["票種"] == each_cat]
    ticket_directory[each_cat] = temp_df
    if temp_df.empty:
        continue
    overnight_df = temp_df[temp_df["是否過夜"]]
    total_records = len(temp_df)
    overnight_count = len(overnight_df)
    overnight_ratio = overnight_count / total_records * 100
    overnight_per_day = overnight_df.groupby("進場日期").size().mean()
    avg_user_overnight = overnight_df["車號"].nunique() / temp_df["進場日期"].nunique()

    result_summary.append({
        "票種": each_cat,
        "工作日紀錄數": total_records,
        "過夜紀錄數": overnight_count,
        "過夜比例(%)": overnight_ratio,
        "平均每日有多少人會過夜": overnight_per_day,
        "平均每日過夜有多少不同用戶": avg_user_overnight
    })

# 整理為 DataFrame
summary_df = pd.DataFrame(result_summary)
summary_df.to_excel(output_graph_file + "過夜情況.xlsx",sheet_name="過夜情況分析")

# 顯示表格
print(summary_df)

# 繪圖
plt.rcParams["font.family"] = ["Arial Unicode MS", "DejaVu Sans", "Microsoft JhengHei"]
plot_df = summary_df.sort_values("過夜比例(%)", ascending=False)

plt.figure(figsize=(12, 6))
plt.barh(plot_df["票種"], plot_df["過夜比例(%)"], color="orange")
plt.xlabel("過夜比例 (%)")
plt.title("各票種過夜比例比較")
plt.grid(True, axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig(output_graph_file + "票種過夜占比.png")

'''
    3. 一天停留時間分布
'''

df = data.copy()
df["start_floor"] = df["全時間格式進入時間"].dt.floor("30min")
df["leave_floor"] = (df["全時間格式出場時間"] + pd.Timedelta(minutes=29)).dt.floor("30min") # 未滿 30 就進位

# 建立每筆資料的所有停留時間格
def generate_time_blocks(row):
    return pd.date_range(start=row["start_floor"], end=row["leave_floor"] - pd.Timedelta(minutes=1), freq="30min")

tqdm.pandas(desc="建立所有停留時間格（支援跨日）")
df["time_blocks"] = df.progress_apply(generate_time_blocks, axis=1)

# 展開為每半小時一筆資料
exploded = df.explode("time_blocks")
exploded["時間標籤"] = exploded["time_blocks"].dt.strftime("%H:%M")


# 統計每個票種在每個時間格的總數
pivot_table = exploded.groupby(["時間標籤", "票種"]).size().unstack(fill_value=0)

# 確保順序一致
bin_labels = [t.strftime("%H:%M") for t in pd.date_range("00:00", "23:30", freq="30min")]
pivot_table = pivot_table.reindex(bin_labels)

# 除以天數，取得每日平均
avg_table = pivot_table / len(data["出場日期"].unique())

# 匯出
avg_table.to_excel(output_graph_file + "每日平均停留_含跨日_半小時統計.xlsx")

'''
    4. 每周進出情況
'''


'''
    5. 票種之間比較
'''
# 加入停留時間欄位
data["停留時數"] = (data["全時間格式出場時間"] - data["全時間格式進入時間"]).dt.total_seconds() / 3600

# 計算每票種平均停留時間
avg_stay_by_ticket = data.groupby("票種")["停留時數"].mean().sort_values(ascending=False)

# 繪圖
plt.figure(figsize=(12, 6))
avg_stay_by_ticket.plot(kind="bar", color="skyblue", edgecolor="black")
plt.ylabel("平均停留時數")
plt.title("各票種平均停留時數比較")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(output_graph_file + "各票種平均停留時數.png", dpi=300)
plt.close()


'''
    比較
'''
# 標記短停與長停
data["停留分類"] = pd.cut(data["停留時數"], bins=[0, 1, 8, 100],
                         labels=["短停(<=1h)", "中停(1~8h)", "長停(>8h)"])

# 計算票種與停留分類的交叉表
cross_tab = pd.crosstab(data["票種"], data["停留分類"], normalize='index') * 100

# 繪圖（堆疊條形圖）
cross_tab.plot(kind='bar', stacked=True, figsize=(12, 6), colormap="tab20c")
plt.ylabel("佔比 (%)")
plt.title("各票種短/中/長停比例")
plt.legend(title="停留分類")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(output_graph_file + "票種短中長停比例.png", dpi=300)
plt.close()

