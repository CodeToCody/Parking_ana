"""分析停車場內實際車輛數與停車格上限的關係，並繪製相關圖表（已整合補正邏輯）。"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from tqdm import tqdm

# 常數設定
MAGIC_NUM = 0
PARKING_CAPACITY = 1475
PEAK_HOUR_START = 9
PEAK_HOUR_END = 16
FONT_FAMILY = "Microsoft JhengHei"


def get_paths(magic_num: int) -> tuple[Path, pd.DataFrame]:
    if magic_num == 0:
        base_path = Path("C:/Cody/Research/clean_data")
    elif magic_num == 1:
        base_path = Path("D:/Research/clean_data")
    else:
        raise ValueError("magic_num 錯誤，只能為 0 或 1")

    prepare_path = base_path / "prepare.csv"
    error_df = pd.read_csv(base_path / "daily_error_count.csv")
    error_df["date"] = pd.to_datetime(error_df["date"]).dt.date
    return prepare_path, error_df


def build_corrected_timeline(df: pd.DataFrame, error_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    df["in_time"] = pd.to_datetime(df["全時間格式進入時間"])
    df["out_time"] = pd.to_datetime(df["全時間格式出場時間"])

    # 計算尖峰比例
    df["in_hour"] = df["in_time"].dt.hour
    peak_ratio = len(df[(df["in_hour"] >= PEAK_HOUR_START) & (df["in_hour"] <= PEAK_HOUR_END)]) / len(df)

    time_changes = {}
    for _, row in tqdm(df.iterrows(), total=len(df), desc="建立差分時間點"):
        time_changes[row["in_time"]] = time_changes.get(row["in_time"], 0) + 1
        time_changes[row["out_time"]] = time_changes.get(row["out_time"], 0) - 1

    count = 0
    timeline = []
    for time_point in tqdm(sorted(time_changes), desc="累加計算在場車輛數"):
        count += time_changes[time_point]
        timeline.append((time_point, count))

    timeline_df = pd.DataFrame(timeline, columns=["timestamp", "cars_in_parking"])
    # 重新取樣為每 15 分鐘一筆資料，並用當時最大車數代表該時段
    timeline_df.set_index("timestamp", inplace=True)
    timeline_df = timeline_df.resample("15min").max().dropna().reset_index()


    # 每日最大值並補正
    timeline_df["date"] = timeline_df["timestamp"].dt.date
    idx = timeline_df.groupby("date")["cars_in_parking"].idxmax()
    peak_df = timeline_df.loc[idx].copy()
    peak_df["error_count"] = peak_df["date"].map(error_df.set_index("date")["error_count"]).fillna(0)
    peak_df["estimated_peak_addition"] = (peak_df["error_count"] * peak_ratio).round().astype(int)
    peak_df["corrected_peak"] = peak_df["cars_in_parking"] + peak_df["estimated_peak_addition"]
    peak_df = peak_df[["date", "timestamp", "cars_in_parking", "error_count", "estimated_peak_addition", "corrected_peak"]]

    return timeline_df, peak_df


def plot_full_timeline(timeline_df: pd.DataFrame, output_dir: Path):
    plt.rcParams["font.family"] = FONT_FAMILY
    plt.figure(figsize=(16, 5))
    plt.plot(timeline_df["timestamp"], timeline_df["cars_in_parking"], label="在場車輛數")
    plt.xlabel("時間")
    plt.ylabel("在場車數")
    plt.title("停車場在場車輛即時變化")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_dir / "全年停車狀況折線圖.png", dpi=300)
    plt.show()


def plot_monthly_bars(daily_max: pd.DataFrame, output_dir: Path):
    daily_max["month"] = pd.to_datetime(daily_max["date"]).dt.to_period("M")
    for month, group in daily_max.groupby("month"):
        plt.figure(figsize=(16, 4))
        colors = ["orange" if d.weekday() < 5 else "skyblue" for d in group["date"]]
        plt.bar(group["date"].astype(str), group["corrected_peak"], color=colors)
        plt.axhline(PARKING_CAPACITY, color="red", linestyle="--", label="上限")
        plt.title(f"{month} 每日最大在場車輛數")
        plt.ylabel("車輛數")
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_dir / f"{month}_每日最大在場車數.png", dpi=300)
        plt.close()

    out_csv = daily_max[["date", "timestamp", "cars_in_parking", "error_count", "estimated_peak_addition", "corrected_peak"]]
    out_csv.columns = ["日期", "尖峰時間", "原始最大車數", "錯誤資料數", "補正車數", "補正後最大車數"]
    out_csv.to_csv(output_dir / "每日補正車數統計.csv", index=False, encoding="utf-8-sig")
    print("每日補正車數統計表已儲存")



def main():
    output_dir = Path.cwd() / "Realtime_situation_chart"
    prepare_path, error_df = get_paths(MAGIC_NUM)
    df = pd.read_csv(prepare_path)
    timeline_df, daily_max = build_corrected_timeline(df, error_df)
    plot_full_timeline(timeline_df, output_dir)
    plot_monthly_bars(daily_max, output_dir)


if __name__ == "__main__":
    main()
