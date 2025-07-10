import pandas as pd
import os
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 設定環境
magic_num = 1
if magic_num == 0:
    source_path1 = r"C:/Cody/Research/clean_data/prepare.csv"
    source_path2 = r"C:/Cody/Research/clean_data/prepare2.csv"
    output_graph_file = r"C:/Cody/Research/Chapter4資料探勘與趨勢分析/compare/"
elif magic_num == 1:
    source_path1 = r"D:/Research/clean_data/prepare.csv"
    source_path2 = r"D:/Research/clean_data/prepare2.csv"
    output_graph_file = r"D:/Research/Chapter4資料探勘與趨勢分析/compare/"
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
    df = pd.read_csv(source_path1, usecols=["車號", "全時間格式進入時間", "全時間格式出場時間"])
    df["全時間格式進入時間"] = pd.to_datetime(df["全時間格式進入時間"], errors="coerce")
    df["全時間格式出場時間"] = pd.to_datetime(df["全時間格式出場時間"], errors="coerce")
    df = df.dropna(subset=["全時間格式進入時間", "全時間格式出場時間"])
    print("數據載入成功，筆數:", len(df))
    df2 = pd.read_csv(source_path2, usecols=["車號", "全時間格式進入時間", "全時間格式出場時間"])
    df2["全時間格式進入時間"] = pd.to_datetime(df2["全時間格式進入時間"], errors="coerce")
    df2["全時間格式出場時間"] = pd.to_datetime(df2["全時間格式出場時間"], errors="coerce")
    df2 = df2.dropna(subset=["全時間格式進入時間", "全時間格式出場時間"])
    print("數據載入成功，筆數:", len(df2))
    
except Exception as e:
    print("數據載入失敗:", e)
    exit(1)

# 計算2024停留時數（小時）
df["stay_hours"] = (df["全時間格式出場時間"] - df["全時間格式進入時間"]).dt.total_seconds() / 3600
# 計算2025停留時數（小時）
df2["stay_hours"] = (df2["全時間格式出場時間"] - df2["全時間格式進入時間"]).dt.total_seconds() / 3600



print("2024 1月到3月25號停留時數範圍:", df["stay_hours"].min(), "至", df["stay_hours"].max())
print("2025 1月到3月25號停留時數範圍:", df2["stay_hours"].min(), "至", df2["stay_hours"].max())


# 篩選工作日（週一至週五）
df["is_workday"] = df["全時間格式進入時間"].dt.weekday < 5
df2["is_workday"] = df2["全時間格式進入時間"].dt.weekday < 5
df = df[df["is_workday"]]
df2 = df2[df2["is_workday"]]
print("工作日數據筆數:", len(df))
print("工作日數據筆數:", len(df2))
if len(df) == 0 or len(df2) == 0:
    print("錯誤：無工作日數據，無法繼續。")
    exit(1)

# 定義時間範圍
start_date = pd.Timestamp("2024-01-01")
end_date = pd.Timestamp("2024-03-25 23:59:59")

# 過濾：只要進入或出場時間有落在這個範圍內
df_target = df[
    ((df["全時間格式進入時間"] >= start_date) & (df["全時間格式進入時間"] <= end_date)) |
    ((df["全時間格式出場時間"] >= start_date) & (df["全時間格式出場時間"] <= end_date))
]


print("供分析數據筆數:", len(df_target))
print("供分析數據筆數:", len(df2))

#############################################################
def analyze_stay_distribution(df, label_prefix=""):
    
    bin_width = 0.25
    short_start, short_end = 0.5, 1
    regular_start, regular_end = 6, 10

    short_start_idx = int(short_start / bin_width)
    short_end_idx = int(short_end / bin_width)
    regular_start_idx = int(regular_start / bin_width)
    regular_end_idx = int(regular_end / bin_width)

    max_hours = 16
    bins = np.arange(0, max_hours + bin_width, bin_width)

    df["date"] = df["全時間格式進入時間"].dt.date
    df["month"] = df["全時間格式進入時間"].dt.to_period("M")

    daily_histograms = []
    for date, group in df.groupby("date"):
        hist, _ = np.histogram(group["stay_hours"], bins=bins)
        daily_histograms.append(pd.Series(hist, index=bins[:-1], name=date))
    daily_hist_df = pd.DataFrame(daily_histograms)

    monthly_avg = {}
    for month, group in df.groupby("month"):
        month_dates = group["date"].unique()
        if len(month_dates) == 0:
            continue
        try:
            month_hist = daily_hist_df.loc[month_dates].mean()
            if not month_hist.isna().all():
                monthly_avg[month] = month_hist
        except:
            continue

    for month, hist in monthly_avg.items():
        try:
            month_data = df[df["month"] == month]
            total_records = len(month_data)
            within_16h_records = len(month_data[month_data["stay_hours"] <= 16])
            percentage = (within_16h_records / total_records * 100) if total_records > 0 else 0
            # 設定中文字型
            plt.rcParams['font.family'] = ['Microsoft JhengHei']
            plt.rcParams['axes.unicode_minus'] = False  # 確保負號顯示正確
            plt.figure(figsize=(12, 6))
            sns.barplot(x=hist.index, y=hist.values, color="skyblue", edgecolor="black")
            plt.title(f"{label_prefix}工作日停留時數平均分佈 ({month})", fontsize=14)
            plt.xlabel("停留時數 (小時)", fontsize=12)
            plt.ylabel("平均停車記錄數", fontsize=12)
            plt.grid(True, alpha=0.3)

            plt.axvspan(short_start_idx, short_end_idx, color="lime", alpha=0.2, label="短時間停留 (0.5 到 1 小時)")
            plt.axvspan(regular_start_idx, regular_end_idx, color="purple", alpha=0.2, label="常規停留 (6 到 10 小時)")
            plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

            tick_positions = np.arange(0, max_hours + bin_width, bin_width)
            label_positions = np.arange(0, max_hours + 0.5, 0.5)
            label_indices = (label_positions / bin_width).astype(int)
            plt.xticks(label_indices, [f"{x:.2f}" if x % 1 else f"{x:.0f}" for x in label_positions])
            plt.xlim(-0.5, len(bins) - 1.5)

            plt.text(0.95, 0.90, f"0-16 小時數據占比：{percentage:.2f}%", 
                     transform=plt.gca().transAxes, fontsize=12, 
                     verticalalignment='top', horizontalalignment='right',
                     bbox=dict(facecolor='white', alpha=0.8, edgecolor='black'))

            plt.tight_layout()
            print(f"\n{label_prefix} {month} 熱門停留區間（前 5）：")
            top_indices = hist.nlargest(5).index
            for idx in top_indices:
                print(f"{idx:.2f}-{idx+bin_width:.2f} 小時: {hist[idx]:.2f} 筆")

            filename = f"{label_prefix}stay_duration_workday_{month}.png"
            output_path = os.path.join(output_graph_file, filename)
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"圖表已儲存: {output_path}")
        except Exception as e:
            print(f"{label_prefix} 繪製 {month} 圖表失敗:", e)

print("▶ 分析 df_target")
analyze_stay_distribution(df_target, label_prefix="df_target_")

print("▶ 分析 df2（2025 資料）")
analyze_stay_distribution(df2, label_prefix="df2_")



