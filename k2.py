# 停車資料分析：每小時停留車輛數（差分累加法 + Plotly）
import pandas as pd
import plotly.graph_objs as go
# 讀取資料
df = pd.read_csv("prepare.csv")
df["全時間格式進入時間"] = pd.to_datetime(df["全時間格式進入時間"], errors="coerce")
df["全時間格式出場時間"] = pd.to_datetime(df["全時間格式出場時間"], errors="coerce")
# 過濾不合法紀錄與超過 72 or 240 小時停留
df = df.dropna(subset=["全時間格式進入時間", "全時間格式出場時間"])
df = df[df["全時間格式出場時間"] > df["全時間格式進入時間"]]
#df = df[(df["全時間格式出場時間"] - df["全時間格式進入時間"]) < pd.Timedelta(hours=72)]
df = df[(df["全時間格式出場時間"] - df["全時間格式進入時間"]) < pd.Timedelta(hours=240)]

# 轉換為整點時間
df["entry_hour"] = df["全時間格式進入時間"].dt.floor("h")
df["exit_hour"] = df["全時間格式出場時間"].dt.floor("h")
# 建立完整時間軸與初始值為 0
time_range = pd.date_range(df["entry_hour"].min(), df["exit_hour"].max(), freq="H")
count_series = pd.Series(0, index=time_range)
# 差分累加法計算在場車輛數
for _, row in df.iterrows():
    count_series.loc[row["entry_hour"]] += 1
    count_series.loc[row["exit_hour"]] -= 1
count_series = count_series.cumsum()

# Plotly 主圖：總體停留車輛
fig = go.Figure()
fig.add_trace(go.Scatter(x=count_series.index, y=count_series.values, mode='lines', name='停留車輛數'))
fig.add_trace(go.Scatter(x=[count_series.index.min(), count_series.index.max()], y=[1475, 1475],
                         mode='lines', line=dict(dash='dash', color='red'), name='停車位上限'))
fig.update_layout(title='每小時停留車輛數（差分累加法）', xaxis_title='時間', yaxis_title='停留車輛數', legend_title='圖例', height=500, width=1000)
fig.show()


# -- 各票種分類分析 --
vehicle_types = df["票種"].unique()
type_series_dict = {vtype: pd.Series(0, index=time_range) for vtype in vehicle_types}
for _, row in df.iterrows():
    entry, exit, vtype = row["entry_hour"], row["exit_hour"], row["票種"]
    if entry in time_range:
        type_series_dict[vtype].loc[entry] += 1
    if exit in time_range:
        type_series_dict[vtype].loc[exit] -= 1
for vtype in type_series_dict:
    type_series_dict[vtype] = type_series_dict[vtype].cumsum()

# Plotly 次圖：各票種
fig_type = go.Figure()
for vtype, series in type_series_dict.items():
    fig_type.add_trace(go.Scatter(x=series.index, y=series.values, mode='lines', name=vtype))
fig_type.update_layout(title='各票種每小時停留車輛數', xaxis_title='時間', yaxis_title='停留車輛數', legend_title='票種', height=500, width=1000)
fig_type.show()