import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime

# 設置 Matplotlib 中文字體 (由左到右，電腦有就用)
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'Noto Sans CJK SC', 'SimHei', 'Arial']
# 讓負號（-）能正常顯示成「-」而不是亂碼或問號
plt.rcParams['axes.unicode_minus'] = False

# 設定路徑
data_file = os.getcwd()
input_file_path = os.path.join(data_file, "temp_file", "sample.csv")
output_dir = os.path.join(data_file, "temp_file")
os.makedirs(output_dir, exist_ok=True)

# 讀取數據
data = pd.read_csv(input_file_path)

# 確保時間格式正確
data['時間'] = pd.to_datetime(data['時間'], errors='coerce')

# 檢查缺失值
print("缺失的時間數量:", data['時間'].isna().sum())
print("缺失的停車數量:", data['停車數量'].isna().sum())
data = data.dropna(subset=['時間', '停車數量'])

# 添加星期和小時欄位
# Pandas 的 datetime 物件有的屬性
data['星期'] = data['時間'].dt.dayofweek  # 0=週一, 6=週日
data['小時'] = data['時間'].dt.hour

# 計算每週每小時的平均值和標準差
weekly_hourly_stats = data.groupby(['星期', '小時'])['停車數量'].agg(['mean', 'std']).reset_index()

# print(weekly_hourly_stats)

# 定義星期名稱（中文）
weekday_names = ['週一', '週二', '週三', '週四', '週五', '週六', '週日']

# --- 視覺化 1: 多子圖折線圖 ---
fig, axes = plt.subplots(7, 1, figsize=(10, 18), sharex=True)           # 整張圖的大小，單位是「英吋」，10 寬、18 高 sharex 意思是所有子圖共享 X軸刻度與範圍
fig.suptitle('2024年每週一到週日每小時平均停車數量與標準差', fontsize=14)

for i, day in enumerate(range(7)):  # 0=週一, 6=週日
    day_data = weekly_hourly_stats[weekly_hourly_stats['星期'] == day]  # 指定該星期的資料
    axes[i].plot(day_data['小時'], day_data['mean'], label='平均停車數量', color='blue') # 畫出平均停車數量，x是day_data['小時'] y是day_data["mean"] label是圖例名稱
    axes[i].fill_between(day_data['小時'], 
                         day_data['mean'] - day_data['std'], 
                         day_data['mean'] + day_data['std'], 
                         color='blue', alpha=0.2, label='標準差範圍')                   # 用淺色標出波動範圍  # x軸座標、下界、上界、顏色、透明度、圖例顯示名稱
    if i == 0:
        axes[i].legend() # 只在第一張圖給圖例
    
    # 標記高峰（例如均值+1.5倍標準差）
    peak_threshold = day_data['mean'] + 1.5 * day_data['std']
    peaks = day_data[day_data['mean'] > peak_threshold]
    if not peaks.empty:
        axes[i].scatter(peaks['小時'], peaks['mean'], color='red', s=50, label='高峰時段')
    
    axes[i].set_title(weekday_names[i], fontsize=12)
    axes[i].set_ylabel('停車數量')
    axes[i].grid(True)
    axes[i].set_xticks(range(24))

axes[-1].set_xlabel('小時')
plt.tight_layout(rect=[0, 0, 1, 0.98])

# 儲存折線圖
lineplot_path = os.path.join(output_dir, "parking_weekly_lineplot.png")
plt.savefig(lineplot_path, dpi=300, bbox_inches='tight')
plt.show()

# --- 視覺化 2: 熱力圖 ---
pivot_table = weekly_hourly_stats.pivot(index='星期', columns='小時', values='mean')
pivot_table.index = weekday_names  # 使用中文星期名稱

plt.figure(figsize=(15, 5))
sns.heatmap(pivot_table, cmap='YlOrRd', annot=True, fmt='.1f', cbar_kws={'label': '平均停車數量'})
plt.title('2024年每週一到週日每小時平均停車數量')
plt.xlabel('小時')
plt.ylabel('星期')
plt.tight_layout()

# 儲存熱力圖
heatmap_path = os.path.join(output_dir, "parking_weekly_heatmap.png")
plt.savefig(heatmap_path, dpi=300, bbox_inches='tight')
plt.show()

# 儲存統計數據到 CSV（無索引）
weekly_hourly_stats.to_csv(os.path.join(output_dir, "weekly_hourly_stats.csv"), index=False, encoding='utf-8-sig')
print("統計數據已儲存為:", os.path.join(output_dir, "weekly_hourly_stats.csv"))