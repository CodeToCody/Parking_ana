import os
import pandas as pd
import numpy as np
from datetime import datetime

# 設定格式
datetime_format = "%Y/%m/%d"

directory_path = os.getcwd()

# 輸入設定
input_file_path = os.path.join(directory_path,"source")

# 輸出設定
output_file = os.path.join(directory_path,"clean_data/prepare.csv")

# 自訂欄位順序（移除「索引」欄位）
column_names = ["車號", "票種", "子場站", "進出及付費狀態", "校正狀態", 
                "進站設備", "出站設備", "進入日", "進入時間", "出場日", 
                "出場時間", "停留時數", "計價代碼", "紀錄時間"]

# 票種對應字典
ticket_type_mapping = {
    "教職汽車證": "教職員汽車",
    "教職計次證": "教職員計次",
    "學生長時汽車證": "學生長時汽車",
    "學生計次證": "學生計次汽車",
    "廠商汽車": "長時廠商汽車",
    "退休校友證": "退休及校友汽車識別證",
    "在職專班證": "在職專班汽車"
}

# **載入車號對應票種**
def load_ticket_mapping(ticket_path):
    """ 載入車號 -> 票種的正確對應表"""
    ticket_mapping = {}
    try:
        excel_data = pd.ExcelFile(ticket_path,engine="xlrd")

        for sheet_name in excel_data.sheet_names:
            df = pd.read_excel(ticket_path, sheet_name=sheet_name, header=2, dtype=str)     # 讀取第3列後的資料
            if "車號" in df.columns:
                df["車號"] = df["車號"].str.replace("-", "", regex=True).str.strip()         # 去除 `-`
                mapped_ticket_type = ticket_type_mapping.get(sheet_name, sheet_name)        # 如果沒有對應，保持原票種名
                df["票種"] = mapped_ticket_type
                ticket_mapping.update(df.set_index("車號")["票種"].to_dict())

        print(f"成功載入 {len(ticket_mapping)} 筆車號對應票種資料")

    except Exception as e:
        print(f"讀取票種資料失敗: {e}")

    return ticket_mapping

# **處理票種校正**
def correct_ticket_type(row, mapping1,mapping2):
    """ 校正 8/1 之前的對應票種 """
    car_number = row["車號"].strip().upper() # 標準化

    # 確保進入日為 datatime 物件
    try:
        entry_date = datetime.strptime(row["進入日"],"%Y/%m/%d")
    except ValueError:
        return row # 日期有誤(格式錯誤)，跳過修正
    
    # 校正 8/1 前的紀錄
    cutoff_date = datetime(entry_date.year, 8, 1)  # 設定 8/1 作為分界點

    # **8/1 之前 → 用 `mapping1` 校正**
    if entry_date < cutoff_date and car_number in mapping1:
        expected_ticket = mapping1[car_number]
        if row["票種"] != expected_ticket:
            print(f"🚗 修正車號 {car_number} (8/1 前): 票種從 {row['票種']} → {expected_ticket}")
            row["票種"] = expected_ticket

    # **8/1 之後 → 用 `mapping2` 校正**
    elif entry_date >= cutoff_date and car_number in mapping2:
        expected_ticket = mapping2[car_number]
        if row["票種"] != expected_ticket:
            print(f"🚗 修正車號 {car_number} (8/1 後): 票種從 {row['票種']} → {expected_ticket}")
            row["票種"] = expected_ticket

    return row

# **輸入流函式**（讀取多個 Excel 檔案）
def input_stream(path):
    all_data = []
    for file in os.listdir(path):
        if file.endswith(".xlsx") or file.endswith(".xls"):
            file_path = os.path.join(path, file)
            try:
                df = pd.read_excel(file_path, header=2, dtype=str)  # 讀取為字串避免格式錯誤
                df.rename(columns={'Unnamed: 0': '索引'}, inplace=True)
                print(f"成功讀取檔案: {file}，欄位名稱: {df.columns.tolist()}")
                all_data.append(df)
            except Exception as e:
                print(f"讀取檔案 {file} 失敗: {e}")
    return pd.concat(all_data, ignore_index=True) if all_data else None




# **格式化紀錄時間函式**
def format_record_time(df,path1,path2):
    if df is None:
        return
    
    # 刪除「索引」欄位
    df.drop(columns=["索引"], errors="ignore", inplace=True)

    # 處理紀錄時間
    if "紀錄時間" in df.columns:
        print("開始處理紀錄時間數據...")
        record_time = df["紀錄時間"].astype(str).fillna("")
        merge_record = []
        temp_date = None
        for idx, value in enumerate(record_time):
            if len(value) == 19:
                temp_date = value.split(" ")[0]
            elif len(value) == 8:
                merge_record.append(f"{temp_date} {value}")
                merge_record.append("")
                temp_date = None
        df["紀錄時間"] = merge_record
        print("紀錄時間數據處理完成。")
    else:
        print("資料中不包含 '紀錄時間' 欄位。")

    # 重新排列欄位
    reorder_data = df.reindex(columns=column_names, fill_value=np.nan)
    reorder_data = reorder_data.dropna(subset=["子場站"], how="all")

    # 清理異常車號
    reorder_data = reorder_data[
        (~reorder_data["車號"].str.contains(r"\*", na=False)) &  # 移除 `*`
        (reorder_data["車號"].str.len().between(4, 7))  # 保留長度 4~7 碼
    ]


    # 轉換進入日與出場日為 datetime，然後格式化為 "%Y/%m/%d"
    reorder_data["進入日"] = pd.to_datetime(reorder_data["進入日"], errors="coerce").dt.strftime("%Y/%m/%d")
    reorder_data["出場日"] = pd.to_datetime(reorder_data["出場日"], errors="coerce").dt.strftime("%Y/%m/%d")

    reorder_data["進入日"] = reorder_data["進入日"].astype(str).str.strip()
    reorder_data["出場日"] = reorder_data["出場日"].astype(str).str.strip()
    reorder_data["進入時間"] = reorder_data["進入時間"].astype(str).str.strip()
    reorder_data["出場時間"] = reorder_data["出場時間"].astype(str).str.strip()

    # 避免 NaN 影響，將 "nan" 轉為 NaN
    reorder_data.replace("nan", np.nan, inplace=True)

    # 計算全時間格式
    reorder_data["全時間格式進入時間"] = pd.to_datetime(
        reorder_data["進入日"] + " " + reorder_data["進入時間"], 
        format="%Y/%m/%d %H:%M:%S", errors="coerce"
    )
    reorder_data["全時間格式出場時間"] = pd.to_datetime(
        reorder_data["出場日"] + " " + reorder_data["出場時間"], 
        format="%Y/%m/%d %H:%M:%S", errors="coerce"
    )

    

    reorder_data["停留時數"] = ((reorder_data["全時間格式出場時間"] - reorder_data["全時間格式進入時間"]).dt.total_seconds()/3600).round(2)

    # 校正 8/1 前的車號票種
    if "車號" in reorder_data.columns and "票種" in reorder_data.columns:
        reorder_data = reorder_data.apply(lambda row: correct_ticket_type(row,path1,path2), axis=1)
    

    # **輸出 CSV**
    try:
        reorder_data.to_csv(output_file, index=False, encoding="utf-8-sig")
        print(f"處理完成，已儲存到 {output_file}")
    except Exception as e:
        print(f"儲存檔案 {output_file} 失敗: {e}")



ticket_verify1_path = os.path.join(directory_path,"112_confirm.xls")
ticket_verify2_path = os.path.join(directory_path,"113_confirm.xls")


# 執行流程
first_hlaf_mapping = load_ticket_mapping(ticket_verify1_path)
second_half_mapping = load_ticket_mapping(ticket_verify2_path)

data = input_stream(input_file_path)

format_record_time(data,first_hlaf_mapping,second_half_mapping)
