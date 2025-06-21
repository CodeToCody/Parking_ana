# 要在對應資料夾啟動
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from tqdm import tqdm
import numpy as np

# 常數設定
MAGIC_NUM = 1
PARKING_CAPACITY = 1475
PEAK_HOUR_START = 9
PEAK_HOUR_END = 16
FONT_FAMILY = "Microsoft JhengHei"
DATETIME_FORMAT = "%Y/%m/%d" 

def get_paths(magic_num: int) -> Path:
    if magic_num == 0:
        base_path = Path("C:/Cody/Research/clean_data")
    elif magic_num == 1:
        base_path = Path("D:/Research/clean_data")
    else:
        raise ValueError("magic_num 錯誤，只能為 0 或 1")

    prepare_path = base_path / "raw_concat.csv"
    return prepare_path


def build_corrected_timeline(df: pd.DataFrame) -> pd.DataFrame:
    # 轉換時間欄位
    df["進入日"] = pd.to_datetime(df["進入日"], errors="coerce").dt.strftime(DATETIME_FORMAT)
    df["出場日"] = pd.to_datetime(df["出場日"], errors="coerce").dt.strftime(DATETIME_FORMAT)

    df.replace("nan", np.nan, inplace=True)
    df["in_time"] = pd.to_datetime(df["進入日"] + " " + df["進入時間"], format="%Y/%m/%d %H:%M:%S", errors="coerce")
    df["out_time"] = pd.to_datetime(df["出場日"] + " " + df["出場時間"], format="%Y/%m/%d %H:%M:%S", errors="coerce")

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

    return timeline_df

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






def main():
    output_dir = Path.cwd() / "initial_state_ana"
    prepare_path= get_paths(MAGIC_NUM)
    df = pd.read_csv(prepare_path)
    timeline_df= build_corrected_timeline(df)
    plot_full_timeline(timeline_df, output_dir)


if __name__ == "__main__":
    main()
