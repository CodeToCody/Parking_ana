import pandas as pd

# 讀取資料
df = pd.read_csv(r"clean_data/prepare.csv")

# 將進出時間轉為 datetime 格式
df["全時間格式進入時間"] = pd.to_datetime(df["全時間格式進入時間"], errors="coerce")
df["全時間格式出場時間"] = pd.to_datetime(df["全時間格式出場時間"], errors="coerce")

# 過濾合法紀錄（有進出時間，且出場晚於進場）
df = df.dropna(subset=["全時間格式進入時間", "全時間格式出場時間"])
df = df[df["全時間格式出場時間"] > df["全時間格式進入時間"]]

# 計算停留時間（天）
df["停留時間"] = df["全時間格式出場時間"] - df["全時間格式進入時間"]
df["停留天數"] = df["停留時間"].dt.total_seconds() / 3600 / 24

# 篩選出停留超過 30 天的車輛
df_over_30_days = df[df["停留天數"] > 30].copy()
df_over_30_days = df_over_30_days.sort_values("停留天數", ascending=False)

# 顯示或輸出結果
print("🚗 停留超過 30 天的車輛數量：", len(df_over_30_days))
print(df_over_30_days[["車號", "票種", "全時間格式進入時間", "全時間格式出場時間", "停留天數"]])

df_over_30_days.to_csv("hihi.csv")