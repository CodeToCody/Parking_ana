import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
from pathlib import Path
import numpy as np
import os

# --------------------------------------------------------
# 常數
# --------------------------------------------------------
FONT_FAMILY = "Microsoft JhengHei"
PARKING_CAPACITY = 1475

# --------------------------------------------------------
# 檔案路徑
# --------------------------------------------------------
magic_num = 1
if magic_num == 0:
    source_path1 = Path(r"C:/Cody/Research/clean_data/prepare.csv")
    source_path2 = Path(r"C:/Cody/Research/clean_data/prepare2.csv")
    output_graph_file = Path(r"C:/Cody/Research/Chapter4資料探勘與趨勢分析/compare/")
elif magic_num == 1:
    source_path1 = Path(r"D:/Research/clean_data/prepare.csv")
    source_path2 = Path(r"D:/Research/clean_data/prepare2.csv")
    output_graph_file = Path(r"D:/Research/Chapter4資料探勘與趨勢分析/compare/")
else:
    raise ValueError("wrong magic num")

# --------------------------------------------------------
# 建立輸出目錄
# --------------------------------------------------------
output_graph_file.mkdir(parents=True, exist_ok=True)
print(f"✅ 輸出目錄已確認: {output_graph_file}")

# --------------------------------------------------------
# 讀取資料
# --------------------------------------------------------
def load_df(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, usecols=["車號", "全時間格式進入時間", "全時間格式出場時間"])
    df["全時間格式進入時間"] = pd.to_datetime(df["全時間格式進入時間"], errors="coerce")
    df["全時間格式出場時間"] = pd.to_datetime(df["全時間格式出場時間"], errors="coerce")
    df = df.dropna(subset=["全時間格式進入時間", "全時間格式出場時間"])
    return df

try:
    df = load_df(source_path1)
    df2 = load_df(source_path2)
    print(f"✅ prepare.csv 筆數: {len(df)}")
    print(f"✅ prepare2.csv 筆數: {len(df2)}")
except Exception as e:
    print(f"❌ 數據讀取失敗: {e}")
    exit(1)

# --------------------------------------------------------
# 計算停留時間
# --------------------------------------------------------
df["stay_hours"] = (df["全時間格式出場時間"] - df["全時間格式進入時間"]).dt.total_seconds() / 3600
df2["stay_hours"] = (df2["全時間格式出場時間"] - df2["全時間格式進入時間"]).dt.total_seconds() / 3600

print(f"2024 1~3月停留時數範圍: {df['stay_hours'].min():.2f} ~ {df['stay_hours'].max():.2f} hr")
print(f"2025 1~3月停留時數範圍: {df2['stay_hours'].min():.2f} ~ {df2['stay_hours'].max():.2f} hr")

# --------------------------------------------------------
# 篩選工作日
# --------------------------------------------------------
df = df[df["全時間格式進入時間"].dt.weekday < 5]
df2 = df2[df2["全時間格式進入時間"].dt.weekday < 5]

print(f"✅ 2024 工作日數據: {len(df)}")
print(f"✅ 2025 工作日數據: {len(df2)}")

if df.empty or df2.empty:
    raise ValueError("❌ 無工作日數據，無法繼續")

# --------------------------------------------------------
# 篩選特定分析期間
# --------------------------------------------------------
start_date = pd.Timestamp("2024-01-01")
end_date   = pd.Timestamp("2024-03-25 23:59:59")

df_target = df[
    (df["全時間格式進入時間"].between(start_date, end_date)) |
    (df["全時間格式出場時間"].between(start_date, end_date))
]
print(f"✅ df_target 供分析筆數: {len(df_target)}")
print(f"✅ df2 供分析筆數: {len(df2)}")

# --------------------------------------------------------
# 分析函式
# --------------------------------------------------------
def build_raw_timeline(df: pd.DataFrame, label: str, output_dir: Path):
    df = df.copy()
    df["in_time"] = df["全時間格式進入時間"]
    df["out_time"] = df["全時間格式出場時間"]

    time_changes = {}
    for _, row in tqdm(df.iterrows(), total=len(df), desc=f"建立差分({label})"):
        time_changes[row["in_time"]] = time_changes.get(row["in_time"], 0) + 1
        time_changes[row["out_time"]] = time_changes.get(row["out_time"], 0) - 1

    count = 0
    timeline = []
    for t in tqdm(sorted(time_changes), desc=f"累加({label})"):
        count += time_changes[t]
        timeline.append((t, count))

    timeline_df = pd.DataFrame(timeline, columns=["timestamp", "cars_in_parking"])
    timeline_df = timeline_df.set_index("timestamp").resample("15min").max().dropna().reset_index()

    # 每日最大
    timeline_df["date"] = timeline_df["timestamp"].dt.date
    idx = timeline_df.groupby("date")["cars_in_parking"].idxmax()
    peak_df = timeline_df.loc[idx, ["date", "timestamp", "cars_in_parking"]].copy()
    peak_df.rename(columns={"cars_in_parking": "raw_peak"}, inplace=True)

    # 年度折線
    plt.rcParams["font.family"] = FONT_FAMILY
    plt.figure(figsize=(16, 5))
    plt.plot(timeline_df["timestamp"], timeline_df["cars_in_parking"], label="在場車輛數")
    plt.xlabel("時間")
    plt.ylabel("在場車輛數")
    plt.title(f"{label} 全年在場車輛數")
    plt.tight_layout()
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_dir / f"{label}_全年折線圖.png", dpi=300)
    plt.close()

    # 月度長條
    peak_df["month"] = pd.PeriodIndex(peak_df["date"], freq="M")
    for month, g in peak_df.groupby("month"):
        plt.figure(figsize=(16, 4))
        colors = ["orange" if pd.Timestamp(d).weekday() < 5 else "skyblue" for d in g["date"]]
        plt.bar(g["date"].astype(str), g["raw_peak"], color=colors)
        plt.axhline(PARKING_CAPACITY, color="red", linestyle="--", label="停車格上限")
        plt.title(f"{label} {month} 每日最大在場車輛數")
        plt.ylabel("車輛數")
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_dir / f"{label}_{month}_每日最大車輛數.png", dpi=300)
        plt.close()

    # 匯出
    peak_df.to_csv(output_dir / f"{label}_每日最大車輛數.csv", index=False, encoding="utf-8-sig")
    print(f"✅ {label} 分析完成並輸出")

# --------------------------------------------------------
# 執行
# --------------------------------------------------------
output_dir = output_graph_file / "compare_raw"
output_dir.mkdir(parents=True, exist_ok=True)

build_raw_timeline(df_target, "df_target", output_dir)
build_raw_timeline(df2, "df2", output_dir)
