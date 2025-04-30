import pandas as pd
import plotly.graph_objs as graph_browser
import os
from plotly.subplots import make_subplots

magic_num = 0
# 0 for notebook 
# 1 for desktop

if magic_num == 0:
    source_path = r"C:/Cody/Research/clean_data/prepare.csv"
    output_file = r"C:/Cody/Research/ana_charts"
else:
    source_path = r"D:/Research/clean_data/prepare.csv"
    output_file = r"D:/Research/ana_charts"

# 讀取資料
data = pd.read_csv(source_path)

# 轉換時間欄位
data["全時間格式進入時間"] = pd.to_datetime(data["全時間格式進入時間"], errors="coerce")
data["全時間格式出場時間"] = pd.to_datetime(data["全時間格式出場時間"], errors="coerce")

# 清除無效資料
data = data.dropna(subset=["全時間格式進入時間", "全時間格式出場時間"])

# 檢查目錄
print("目錄是否存在:", os.path.exists(output_file))
print("目錄可寫:", os.access(output_file, os.W_OK))

# --- 改這裡 ---
# 先建立子圖，列數 = 8（從7到14，共8個數字）
fig = make_subplots(
    rows=8, cols=1, 
    shared_xaxes=True, 
    vertical_spacing=0.02,
    subplot_titles=[f"{x}天內停留車輛數" for x in range(7, 15)]
)

# 處理每個時間段
for idx, x in enumerate(range(7, 15)):
    temp_data = data[data["全時間格式出場時間"] - data["全時間格式進入時間"] < pd.Timedelta(hours=x*24)].copy()

    # 整點化
    temp_data["entry_hour"] = temp_data["全時間格式進入時間"].dt.floor("h")
    temp_data["exit_hour"] = temp_data["全時間格式出場時間"].dt.floor("h")

    # 建立時間軸與初始化
    time_range = pd.date_range(temp_data["entry_hour"].min(), temp_data["exit_hour"].max(), freq="h")
    count_series = pd.Series(0, index=time_range)

    # 差分累加計算
    for _, row in temp_data.iterrows():
        count_series.loc[row["entry_hour"]] += 1
        count_series.loc[row["exit_hour"]] -= 1
    count_series = count_series.cumsum()

    # 加進子圖
    fig.add_trace(
        graph_browser.Scatter(x=count_series.index, y=count_series.values, mode='lines', name=f'{x}天內停留車輛數'),
        row=idx+1, col=1
    )

    # 加一條紅色虛線（1475上限）
    fig.add_trace(
        graph_browser.Scatter(
            x=[count_series.index.min(), count_series.index.max()],
            y=[1475, 1475],
            mode='lines',
            line=dict(dash='dash', color='red'),
            name='停車位上限'
        ),
        row=idx+1, col=1
    )

# 全局設定
fig.update_layout(
    height=400 * 8,  # 每張子圖400px高
    width=1200,
    title_text="刪除不同停留天數以上的用戶族群後，停留車輛數分析",
    showlegend=False  # 每張小圖都有自己的 legend 會很亂，乾脆關掉
)

fig.show()
