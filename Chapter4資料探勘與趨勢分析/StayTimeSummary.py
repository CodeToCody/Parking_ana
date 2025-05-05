import pandas as pd
import os
import matplotlib
matplotlib.use("Agg")  # 使用非互動後端
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 設定環境
magic_num = 0
if magic_num == 0:
    source_path = r"C:/Cody/Research/clean_data/prepare.csv"
    output_graph_file = r"C:/Cody/Research/Chapter4資料探勘與趨勢分析/StayTimeSummary_chart/"
elif magic_num == 1:
    source_path = r"D:/Research/clean_data/prepare.csv"
    output_graph_file = r"D:/Research/Chapter4資料探勘與趨勢分析/StayTimeSummary_chart/"
else:
    print("wrong magic num.")
    exit(1)

# 確保輸出目錄存在
try:
    os.makedirs(output_graph_file, exist_ok=True)
    print("輸出目錄已確認:", output_graph_file)
except Exception as e:
    print("無法創建輸出目錄:", e)
    exit(1)

# 讀取數據
try:
    df = pd.read_csv(source_path, usecols=["車號", "全時間格式進入時間", "全時間格式出場時間"])
    df["全時間格式進入時間"] = pd.to_datetime(df["全時間格式進入時間"], errors="coerce")
    df["全時間格式出場時間"] = pd.to_datetime(df["全時間格式出場時間"], errors="coerce")
    df = df.dropna(subset=["全時間格式進入時間", "全時間格式出場時間"])
    print("數據載入成功，筆數:", len(df))
except Exception as e:
    print("數據載入失敗:", e)
    exit(1)

# 計算停留時數（小時）
df["stay_hours"] = (df["全時間格式出場時間"] - df["全時間格式進入時間"]).dt.total_seconds() / 3600
df = df[df["stay_hours"] >= 0]  # 移除負值
print("停留時數範圍:", df["stay_hours"].min(), "至", df["stay_hours"].max())

# 篩選工作日（週一至週五）
df["is_workday"] = df["全時間格式進入時間"].dt.weekday < 5
df = df[df["is_workday"]]
print("工作日數據筆數:", len(df))
if len(df) == 0:
    print("錯誤：無工作日數據，無法繼續。")
    exit(1)

# 檢查每月數據
print("每月工作日數據筆數:")
monthly_counts = df.groupby(df["全時間格式進入時間"].dt.to_period("M")).size()
print(monthly_counts)

# 定義直方圖的 bin（15 分鐘 = 0.25 小時）
bin_width = 0.25  # 15 分鐘
max_hours = 16  # 統計到 16 小時
bins = np.arange(0, max_hours + bin_width, bin_width)
print("Bins 數量:", len(bins) - 1)

# 按天分組，計算每日停留時數分佈
df["date"] = df["全時間格式進入時間"].dt.date
daily_histograms = []
for date, group in df.groupby("date"):
    hist, _ = np.histogram(group["stay_hours"], bins=bins)
    daily_histograms.append(pd.Series(hist, index=bins[:-1], name=date))
daily_hist_df = pd.DataFrame(daily_histograms)
print("每日直方圖數量:", len(daily_hist_df))

# 按月平均
df["month"] = df["全時間格式進入時間"].dt.to_period("M")
monthly_avg = {}
for month, group in df.groupby("month"):
    month_dates = group["date"].unique()
    if len(month_dates) == 0:
        print(f"警告：{month} 無工作日數據，跳過。")
        continue
    try:
        month_hist = daily_hist_df.loc[month_dates].mean()
        if month_hist.isna().all():
            print(f"警告：{month} 直方圖數據無效，跳過。")
            continue
        monthly_avg[month] = month_hist
    except Exception as e:
        print(f"計算 {month} 平均直方圖失敗:", e)
print("生成每月平均直方圖:", list(monthly_avg.keys()))

# 設定中文字型
plt.rcParams['font.family'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False  # 確保負號顯示正確

# 繪製每個月的工作日平均長條圖
for month, hist in monthly_avg.items():
    try:
        # 計算 0-16 小時數據占比
        month_data = df[df["month"] == month]
        total_records = len(month_data)
        within_16h_records = len(month_data[month_data["stay_hours"] <= 16])
        percentage = (within_16h_records / total_records * 100) if total_records > 0 else 0
        print(f"{month} 0-16 小時數據占比: {percentage:.2f}%")

        plt.figure(figsize=(12, 6))
        sns.barplot(x=hist.index, y=hist.values, color="skyblue", edgecolor="black")
        plt.title(f"光復校區停車場工作日停留時數平均分佈 ({month})", fontsize=14)
        plt.xlabel("停留時數 (小時)", fontsize=12)
        plt.ylabel("平均停車記錄數", fontsize=12)
        plt.grid(True, alpha=0.3)

        # 標記關鍵區間
        plt.axvspan(0.5, 1, color="orange", alpha=0.2, label="短停 (0.5-1 小時)")
        plt.axvspan(6, 8, color="green", alpha=0.2, label="常規停留 (6-8 小時)")
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))  # 圖例外部右側

        # 設置 x 軸刻度（每 15 分鐘刻度，每 0.5 小時標籤）
        tick_positions = np.arange(0, max_hours + bin_width, bin_width)  # 每 15 分鐘
        label_positions = np.arange(0, max_hours + 0.5, 0.5)  # 每 0.5 小時標籤
        label_indices = (label_positions / bin_width).astype(int)  # 對應 bin 索引
        plt.xticks(label_indices, [f"{x:.2f}" if x % 1 else f"{x:.0f}" for x in label_positions])
        plt.xlim(-0.5, len(bins) - 1.5)  # 確保所有 bar 顯示

        # 添加百分比文字（右上角，稍下移）
        plt.text(0.95, 0.90, f"0-16 小時數據占比：{percentage:.2f}%", 
                 transform=plt.gca().transAxes, fontsize=12, 
                 verticalalignment='top', horizontalalignment='right',
                 bbox=dict(facecolor='white', alpha=0.8, edgecolor='black'))

        plt.tight_layout()

        # 儲存圖表
        output_path = os.path.join(output_graph_file, f"stay_duration_workday_{month}.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')  # 保留外部圖例
        plt.close()
        print(f"圖表已儲存: {output_path}")

        # 統計熱門區間
        print(f"\n{month} 熱門停留區間（前 5）：")
        top_indices = hist.nlargest(5).index
        for idx in top_indices:
            count = hist[idx]
            if count > 0:
                print(f"{idx:.2f}-{idx+bin_width:.2f} 小時: {count:.2f} 筆")
    except Exception as e:
        print(f"繪製 {month} 圖表失敗:", e)

print("所有圖表已儲存至:", output_graph_file)
