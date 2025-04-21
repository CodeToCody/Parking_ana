import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns


this_file_path = os.getcwd()

source_path = os.path.join(this_file_path,r"temp_file/sample_sheet_first.xlsx")

data = pd.read_excel(source_path)


'''
樣態分析: 分月分時停留數量,票種占比,進出時間
'''

data['時間'] = pd.to_datetime(data['Unnamed: 0'])
data['月份'] = data['時間'].dt.strftime('%Y-%m')

# 整合所有停留欄位成一個「總停留數」
stay_cols = [col for col in data.columns if '_停留' in col]
data['總停留數'] = data[stay_cols].sum(axis=1)

# 儲存圖檔資料夾
output_dir = os.path.join(this_file_path, "monthly_stay_charts")
os.makedirs(output_dir, exist_ok=True)

# 分月畫圖
for month, df_month in data.groupby('月份'):
    plt.rcParams["font.sans-serif"] = ["Microsoft JhengHei"]
    plt.rcParams["axes.unicode_minus"] = False
    plt.figure(figsize=(12, 4))
    sns.lineplot(x=df_month['時間'], y=df_month['總停留數'], label='總停留車輛')
    plt.axhline(1475, color='red', linestyle='--', label='容量上限1475')
    plt.title(f'{month} 每小時停留車輛數')
    plt.xlabel('時間')
    plt.ylabel('車輛數')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'{month}_停留趨勢.png'))
    plt.close()

print(f"✅ 每月趨勢圖已儲存於：{output_dir}")