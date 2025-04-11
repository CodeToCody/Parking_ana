from datetime import datetime, timedelta
import pandas as pd
from tqdm import tqdm

# 設定電腦路徑
computer_num = 1  # 1 for notebook, 0 for laptop

if computer_num == 1:
    data1 = pd.read_csv(r"C:/Cody/Research/Report_sheet/工作日統計_8月前.csv")
    data2 = pd.read_csv(r"C:/Cody/Research/Report_sheet/工作日統計_8月後.csv")
else:
    data1 = pd.read_csv(r"D:/Research/Report_sheet/工作日統計_8月前.csv")
    data2 = pd.read_csv(r"D:/Research/Report_sheet/工作日統計_8月後.csv")

# 合併數據
data = pd.concat([data1, data2], ignore_index=True)

# 確保時間格式正確
data['全時間格式進入時間'] = pd.to_datetime(data['全時間格式進入時間'], errors='coerce')
data['全時間格式出場時間'] = pd.to_datetime(data['全時間格式出場時間'], errors='coerce')

# 檢查是否有缺失值
print("缺失的進入時間數量:", data['全時間格式進入時間'].isna().sum())
print("缺失的出場時間數量:", data['全時間格式出場時間'].isna().sum())

# 修剪出場時間：如果出場時間在 2025 年或之後，限制為 2024-12-31 23:59:59
end_of_2024 = pd.Timestamp('2024-12-31 23:00:00')
data['全時間格式出場時間'] = data['全時間格式出場時間'].apply(
    lambda x: min(x, end_of_2024) if pd.notna(x) else x
)

# 初始化 hourly_parking
start_year = datetime(2024, 1, 1)
end_year = datetime(2024, 12, 31, 23, 59, 59)
hour_range = pd.date_range(start=start_year, end=end_year, freq='h')
hourly_parking = {hour: 0 for hour in hour_range}

skipped_count = 0
# 為每個車輛計算其停留的所有小時（添加進度條）
for index, row in tqdm(data.iterrows(), total=len(data), desc="處理車輛停留時間"):
    start = row['全時間格式進入時間']
    end = row['全時間格式出場時間']
    
    if pd.isna(start) or pd.isna(end):  # 跳過缺失值
        continue
        
    if end < start:
        skipped_count += 1
        tqdm.write(f"警告：車輛 {row['車號']} 的出場時間 {end} 早於進入時間 {start}，跳過。")
        continue
    
    current_hour = start.floor('h')  # 取整到最近的小時
    while current_hour <= end.floor('h'):
        hourly_parking[current_hour] += 1
        current_hour += timedelta(hours=1)

# 轉換為 DataFrame
hourly_df = pd.DataFrame.from_dict(hourly_parking, orient='index', columns=['停車數量'])
hourly_df.index.name = '時間'
hourly_df.reset_index(inplace=True)

# 檢查結果
print("每小時停車數量樣本:")
print(hourly_df.head())
if computer_num == 1:
    hourly_df.to_csv("C:/Cody/Research/temp_file/每小時停車數量樣本.csv")
else:
    hourly_df.to_csv("D:/Research/temp_file/每小時停車數量樣本.csv")