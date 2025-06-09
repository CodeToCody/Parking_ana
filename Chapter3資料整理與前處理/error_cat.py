import os
import pandas as pd
import numpy as np
from datetime import timedelta

# === 基本參數與路徑設定 ===
DATETIME_FORMAT = "%Y/%m/%d"
MAGIC_NUM = 0  # 0 for notebook, 1 for desktop
INPUT_PATHS = {
    0: r"C:/Cody/Research/clean_data/dropped_records.csv",
    1: r"D:/Research/clean_data/dropped_records.csv"
}
OUTPUT_FILES = {
    0: r"C:/Cody/Research/Chapter3資料整理與前處理/Error_Analyze.xlsx",
    1: r"D:/Research/Chapter3資料整理與前處理/Error_Analyze.xlsx"
}

CLEAN_DATA_PATH = {
    0: r"C:/Cody/Research/clean_data/prepare.csv",
    1: r"D:/Research/clean_data/prepare.csv"
}

OUTPUT_FILES_dropped_stat = {
    0: r"C:/Cody/Research/clean_data/daily_error_count.csv",
    1: r"D:/Research/clean_data/daily_error_count.csv"
}

prepare_data = pd.read_csv(CLEAN_DATA_PATH[MAGIC_NUM])

if MAGIC_NUM not in INPUT_PATHS:
    raise ValueError("Invalid MAGIC_NUM. Please set to 0 or 1.")

# === 讀取資料 ===
data = pd.read_csv(INPUT_PATHS[MAGIC_NUM], dtype={15: str, 16: str})
output_file = OUTPUT_FILES[MAGIC_NUM]

# === 時間欄位格式轉換 ===
data["全時間格式進入時間"] = pd.to_datetime(data["全時間格式進入時間"], errors="coerce")
data["全時間格式出場時間"] = pd.to_datetime(data["全時間格式出場時間"], errors="coerce")

# === 定義工具函數 ===
def is_identifiable_plate(plate):
    if pd.isna(plate):
        return False
    plate_str = str(plate).strip()
    return 4 <= len(plate_str) <= 7 and '*' not in plate_str

def is_meaningful(val):
    if pd.isna(val):
        return False
    val_str = str(val).strip()
    return val_str != "" and set(val_str) != {","}

# === 初步分類 ===
useless_data = data[data["車號"].isna()].copy()
usable_data = data[data["車號"].notna()].copy()

# 車號可辨識性
flag = usable_data["車號"].apply(is_identifiable_plate)
identify_data = usable_data[flag]
something_data = usable_data[~flag]

# 魔幻進出時間
time_error_data = data[data["全時間格式進入時間"] > data["全時間格式出場時間"]].copy()

# 時間欄位有效性分析
exclude_col = "刪除原因"
cols_to_check = [col for col in data.columns if col != exclude_col]
valid_counts = data[cols_to_check].apply(lambda row: sum(is_meaningful(v) for v in row), axis=1)
cleaned_data = data[valid_counts > 1]
entry_na = cleaned_data["全時間格式進入時間"].isna()
exit_na = cleaned_data["全時間格式出場時間"].isna()
both_na = entry_na & exit_na
only_entry_na = entry_na & ~exit_na
only_exit_na = ~entry_na & exit_na

# 停留時間分析
data["停留時間"] = data["全時間格式出場時間"] - data["全時間格式進入時間"]
stay_over_7_days = data[data["停留時間"] > timedelta(days=7)]

# 停留超過7天票種統計
ticket_stats = pd.DataFrame()
if "票種" in stay_over_7_days.columns:
    ticket_stats = stay_over_7_days["票種"].value_counts(dropna=False).reset_index()
    ticket_stats.columns = ["票種", "筆數"]

# 無車號資料的時間欄位缺失分析
something_entry_na = something_data["全時間格式進入時間"].isna()
something_exit_na = something_data["全時間格式出場時間"].isna()
something_both_na = something_entry_na & something_exit_na
something_only_entry_na = something_entry_na & ~something_exit_na
something_only_exit_na = ~something_entry_na & something_exit_na

# === 票種分類統計分析 ===
group_by_ticket = usable_data.groupby("票種")
summary_list = []
ticket_type_total_counts = usable_data["票種"].value_counts().to_dict()
prepare_ticket_counts = prepare_data["票種"].value_counts().to_dict()

for ticket_type, group in group_by_ticket:
    group = group.copy()
    group["全時間格式進入時間"] = pd.to_datetime(group["全時間格式進入時間"], errors="coerce")
    group["全時間格式出場時間"] = pd.to_datetime(group["全時間格式出場時間"], errors="coerce")
    stay_time = group["全時間格式出場時間"] - group["全時間格式進入時間"]

    group_total = len(group)
    total_in_prepare = prepare_ticket_counts.get(ticket_type, 0)
    usable_count = len(group)

    summary_list.append({
        "票種": ticket_type,
        "票種錯誤資料數": group_total,
        "各票種正確總筆數": total_in_prepare,
        "錯誤占比(%)": round(usable_count / total_in_prepare * 100, 2) if total_in_prepare else np.nan,
        "魔幻進出時間": (group["全時間格式進入時間"] > group["全時間格式出場時間"]).sum(),
        "停留 >7天": (stay_time > timedelta(days=7)).sum(),
        "缺進": group["全時間格式進入時間"].isna().sum(),
        "缺出": group["全時間格式出場時間"].isna().sum(),
        "進出皆無": ((group["全時間格式進入時間"].isna()) & (group["全時間格式出場時間"].isna())).sum()
    })

summary_df = pd.DataFrame(summary_list)

# === 輸出至 Excel ===
with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
    summary_df.to_excel(writer, sheet_name="票種異常統計", index=False)
    ticket_stats.to_excel(writer, sheet_name="超過7天票種統計", index=False)

# === 錯誤資料出場日期統計 ===
usable_data["錯誤出場日"] = pd.to_datetime(usable_data["全時間格式出場時間"], errors="coerce").dt.date
daily_error_count = usable_data["錯誤出場日"].value_counts().reset_index()
daily_error_count.columns = ["date", "error_count"]

# 輸出成 CSV
daily_error_count.to_csv(OUTPUT_FILES_dropped_stat[MAGIC_NUM], index=False)

