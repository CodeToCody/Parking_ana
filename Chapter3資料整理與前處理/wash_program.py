# 重構後版本
import os
import pandas as pd
import numpy as np
from datetime import datetime

# === 基本參數 ===
DATETIME_FORMAT = "%Y/%m/%d"
MAGIC_NUM = 1  # 0 for notebook, 1 for desktop

# === 路徑設定 ===
BASE_DIR = os.getcwd()
INPUT_PATHS = {
    0: r"C:/Cody/Research/source",
    1: r"D:/Research/source"
}
OUTPUT_FILES = {
    0: r"C:/Cody/Research/clean_data/prepare.csv",
    1: r"D:/Research/clean_data/prepare.csv"
}

if MAGIC_NUM not in INPUT_PATHS:
    raise ValueError("Invalid MAGIC_NUM. Please set to 0 or 1.")

input_file_path = INPUT_PATHS[MAGIC_NUM]
output_file = OUTPUT_FILES[MAGIC_NUM]
dropped_file = output_file.replace("prepare.csv", "dropped_records.csv")

# === 欄位與票種對應 ===
COLUMN_NAMES = ["車號", "票種", "子場站", "進出及付費狀態", "校正狀態", "進站設備", "出站設備", "進入日", "進入時間", "出場日", "出場時間", "停留時數", "計價代碼", "紀錄時間"]

TICKET_TYPE_MAPPING = {
    "教職汽車證": "教職員汽車",
    "教職計次證": "教職員計次",
    "學生長時汽車證": "學生長時汽車",
    "學生計次證": "學生計次汽車",
    "廠商汽車": "長時廠商汽車",
    "退休校友證": "退休及校友汽車識別證",
    "在職專班證": "在職專班汽車"
}

# === 載入票種對應 ===
def load_ticket_mapping(ticket_path):
    mapping = {}
    try:
        excel_data = pd.ExcelFile(ticket_path, engine="xlrd")
        for sheet in excel_data.sheet_names:
            df = pd.read_excel(ticket_path, sheet_name=sheet, header=2, dtype=str)
            if "車號" in df.columns:
                df["車號"] = df["車號"].str.replace("-", "", regex=True).str.strip()
                df["票種"] = TICKET_TYPE_MAPPING.get(sheet, sheet)
                mapping.update(df.set_index("車號")["票種"].to_dict())
        print(f"成功載入 {len(mapping)} 筆車號對應票種資料")
    except Exception as e:
        print(f"讀取票種資料失敗: {e}")
    return mapping

# === 校正票種 ===
def correct_ticket_type(row, mapping1, mapping2):
    car = row["車號"].strip().upper()
    try:
        date = datetime.strptime(row["進入日"], DATETIME_FORMAT)
    except ValueError:
        return row

    cutoff = datetime(date.year, 8, 1)
    if date < cutoff and car in mapping1:
        row["票種"] = mapping1[car]
    elif date >= cutoff and car in mapping2:
        row["票種"] = mapping2[car]
    return row

# === 合併 Excel 檔案 ===
def load_input_data(path):
    frames = []
    for f in os.listdir(path):
        if f.endswith(('.xls', '.xlsx')):
            try:
                df = pd.read_excel(os.path.join(path, f), header=2, dtype=str)
                df.rename(columns={"Unnamed: 0": "索引"}, inplace=True)
                print(f"成功讀取檔案: {f}")
                frames.append(df)
            except Exception as e:
                print(f"讀取檔案 {f} 失敗: {e}")
    return pd.concat(frames, ignore_index=True) if frames else None

# === 清理與轉換資料 ===
def clean_data(df, map1, map2):
    if df is None:
        return

    df.drop(columns=["索引"], errors="ignore", inplace=True)
    df = df.reindex(columns=COLUMN_NAMES, fill_value=np.nan)

    # 處理紀錄時間
    if "紀錄時間" in df.columns:
        times = df["紀錄時間"].astype(str).fillna("")
        merged = []
        temp = None
        for val in times:
            if len(val) == 19:
                temp = val.split()[0]
            elif len(val) == 8:
                merged.append(f"{temp} {val}")
                merged.append("")
                temp = None
        df["紀錄時間"] = merged

    dropped_records = []

    # 清除異常車號
    before = len(df)
    invalid_car = df[(df["車號"].str.contains("\\*", na=False)) | (~df["車號"].str.len().between(4, 7))].copy()
    invalid_car["刪除原因"] = "車號異常"
    dropped_records.append(invalid_car)
    df = df.drop(invalid_car.index)
    print(f"異常車號刪除 {before - len(df)} 筆")

    # 轉換時間欄位
    df["進入日"] = pd.to_datetime(df["進入日"], errors="coerce").dt.strftime(DATETIME_FORMAT)
    df["出場日"] = pd.to_datetime(df["出場日"], errors="coerce").dt.strftime(DATETIME_FORMAT)

    df.replace("nan", np.nan, inplace=True)
    df["全時間格式進入時間"] = pd.to_datetime(df["進入日"] + " " + df["進入時間"], format="%Y/%m/%d %H:%M:%S", errors="coerce")
    df["全時間格式出場時間"] = pd.to_datetime(df["出場日"] + " " + df["出場時間"], format="%Y/%m/%d %H:%M:%S", errors="coerce")

    # 1. 時間為空
    missing_time = df[df["全時間格式進入時間"].isna() | df["全時間格式出場時間"].isna()].copy()
    missing_time["刪除原因"] = "時間為空"
    dropped_records.append(missing_time)
    df = df.drop(missing_time.index)

    # 2. 出場時間早於或等於進入時間
    invalid_time = df[df["全時間格式出場時間"] <= df["全時間格式進入時間"]].copy()
    invalid_time["刪除原因"] = "出場時間早於或等於進入時間"
    dropped_records.append(invalid_time)
    df = df.drop(invalid_time.index)

    # 3. 停留時間超過7天
    long_stay = df[(df["全時間格式出場時間"] - df["全時間格式進入時間"]) >= pd.Timedelta(days=7)].copy()
    long_stay["刪除原因"] = "停留時間超過7天"
    dropped_records.append(long_stay)
    df = df.drop(long_stay.index)

    if dropped_records:
        dropped_df = pd.concat(dropped_records, ignore_index=True)
        dropped_df.to_csv(dropped_file, index=False, encoding="utf-8-sig")
        print(f"被刪除的資料已儲存至 {dropped_file}")

    df["停留時數"] = ((df["全時間格式出場時間"] - df["全時間格式進入時間"]).dt.total_seconds() / 3600).round(2)
    df = df.apply(lambda row: correct_ticket_type(row, map1, map2), axis=1)

    # 儲存檔案
    try:
        df.to_csv(output_file, index=False, encoding="utf-8-sig")
        print(f"資料清理完成，儲存至 {output_file}")
    except Exception as e:
        print(f"儲存失敗: {e}")

# === 主程式 ===
if __name__ == "__main__":
    map_112 = load_ticket_mapping(os.path.join(BASE_DIR, "112_confirm.xls"))
    map_113 = load_ticket_mapping(os.path.join(BASE_DIR, "113_confirm.xls"))
    raw_data = load_input_data(input_file_path)

     # 儲存原始資料（未經清理與校正）
    try:
        raw_output_file = output_file.replace("prepare.csv", "raw_concat.csv")
        raw_data.to_csv(raw_output_file, index=False, encoding="utf-8-sig")
        print(f"原始合併資料已儲存至 {raw_output_file}")
    except Exception as e:
        print(f"原始資料儲存失敗: {e}")


    clean_data(raw_data, map_112, map_113)
