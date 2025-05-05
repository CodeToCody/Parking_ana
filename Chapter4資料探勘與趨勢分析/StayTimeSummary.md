## code 解析-1
```python

# 篩選工作日
df["is_workday"] = df["全時間格式進入時間"].dt.weekday < 5
df = df[df["is_workday"]]

# 計算停留時數（小時）
df["stay_hours"] = (df["全時間格式出場時間"] - df["全時間格式進入時間"]).dt.total_seconds() / 3600
df = df[df["stay_hours"] >= 0]  # 移除負值
```

1. ```df["全時間格式進入時間"].dt.weekday < 5```這個判斷式會 return 一個布林值。
2. ```df[df["is_workday"]]```就會將```is_workday```欄位為 True 的資料都留下來 (Boolean Masking)。


## code 解析-2
```python
# 定義直方圖的 bin（15 分鐘 = 0.25 小時）
bin_width = 0.25
short_start, short_end = 0.5, 1
regular_start, regular_end = 6, 8
# 換算為 index
short_start_idx = int(short_start / bin_width)
short_end_idx = int(short_end / bin_width)
regular_start_idx = int(regular_start / bin_width)
regular_end_idx = int(regular_end / bin_width)

max_hours = 16  # 統計到 16 小時
bins = np.arange(0, max_hours + bin_width, bin_width)
print("Bins 數量:", len(bins) - 1)
```
1. ```bin``` 就是指直方圖(histogram)區間單位，比如說 x 軸是 0 到 16 小時，則每個小區間假設你切每 15 分鐘一格，那這些格子就叫做 ```bin```。
2. ```short_start,short_end``` 指等等要在圖片上做標記的區間，這裡指的是短時間停留，設定為半小時到 1 小時。
3. ```regular_start,regular_end``` 同上，是要標記 "我認為是常見停留時間" 的時間，設定為 6 到 8 小時。
4. ```np.arrange()``` 會 return 一個數值陣列(array)，就像ex. [0,1,2,3 ...]，前後參數分別為```起始數值```、```間隔```、```尾數```。
5. ```idx``` 系列是在算要在對應圖片那個 bin


## code 解析-3
```python
# 按天分組，計算每日停留時數分佈
df["date"] = df["全時間格式進入時間"].dt.date
daily_histograms = []
for date, group in df.groupby("date"):
    hist, _ = np.histogram(group["stay_hours"], bins=bins)
    daily_histograms.append(pd.Series(hist, index=bins[:-1], name=date))
daily_hist_df = pd.DataFrame(daily_histograms)
print("每日直方圖數量:", len(daily_hist_df))

```
1. 先新增一個```date```欄位，去根據日期分組。
2. ```df.gropby("date")```會 return 一個 tuple，而這個 tuple 的 key 會是該資料的 ```date``` 。

ex.
```python
(
  datetime.date(2025, 5, 5),
  DataFrame[
    所有在這天的資料
  ]
)
```
3. ```np.histogram``` 非用來畫圖，是在計算每個 bin 裡有多少筆資料，第一個參數放你要統計的數值 array，第二個參數放定義的區間邊界(例如每 15 分鐘一格)。```np.histogram```會 return 兩個 array，一個是 bin 值 array，一個是各個 bin 內資料的數量。
4. ```hist``` 表示一個 array ，代表每個 bin 裡面有幾個人或紀錄([0,0,1,0,...])，```_``` 代表的是 bin 的邊界，不需要所以捨棄。
5. ```pd.Series(hist, index=bins[:-1], name=date)```把 histogram 封裝成一個 Series ，```index```參數對應每個 bin 起始值(bin 是一格)，```bins [:-1]```填 -1 是因為 python 的 slicing 語法，```:-1``` 就是將最後一個元素拿掉。而 bins 原本是類似 [1,2,3,4]，畫成軸的畫不能寫 4 ，因為他是最大位(每兩個數字是一格的概念)。 
6. ```daily_histograms``` 是一個 list，```name```被拿來識別是哪一天，所以存```date```參數。
```python
# 這是 daily_histograms 的樣子
pd.Series(
    data=[3, 1, 2, 0, ...],       # 每一格的統計人數
    index=[0.0, 0.25, 0.5, ...],  # 每一格 bin 的左邊界（起始值）!!!! 重要 !!!!
    name="2025-05-05"            # 這一列代表哪一天
)
# 整個 list 就是
[
  Series for 2025-05-05,
  Series for 2025-05-06,
  Series for 2025-05-07,
  ...
]

# 後來變成 (index 變成欄位)(name 變成橫軸)
           0.00  0.25  0.50
2025-05-05     3     1     2
2025-05-06     2     2     1
2025-05-07     1     0     0
```
7. ```pandas.DataFrame()``` 可以接受 多個 Series 組成一個表格，只要這些 Series 的 index 一樣，就會自動變成 row。(**是看 index !!**)

## code解析-4
```python
# 按月平均
df["month"] = df["全時間格式進入時間"].dt.to_period("M")
monthly_avg = {}

for month, group in df.groupby("month"):
    month_dates = group["date"].unique()
    if len(month_dates) == 0:
        print(f"警告：{month} 無工作日數據，跳過。")
        continue
    try:
        month_hist = daily_hist_df.loc[month_dates].mean()
        if month_hist.isna().all():
            print(f"警告：{month} 直方圖數據無效，跳過。")
            continue
        monthly_avg[month] = month_hist
    except Exception as e:
        print(f"計算 {month} 平均直方圖失敗:", e)
```

1. 新增 ```month``` 欄位，直接紀錄日期。
2. ```month_dates``` 抓出該月所有不重複的日期。
3. 將```month_dates``` 餵給```daily_hist_df```，篩出所有該月資料，並每個欄位取平均。(```daily_hist_df.loc[month_dates].mean()``` return 一個 Series)
4. ```monthly_avg[month]```是 dictionary，key = month，value 是 該月的每個 bin 區間的資料數量平均 array。


## code-5
🔍 圖示說明（模擬圖）
假設你有以下 bin：

|bin index	|數值範圍	|中心值	|對應條數|
|---|--|--|--|
0	|0.0 – 0.5|	0.25|	3|
1	|0.5 – 1.0|	0.75|	5|
2	|1.0 – 1.5|	1.25|	7|
3	|1.5 – 2.0|	1.75|	4|
...|	...	|...	|...|

**希望在 X 軸上標示出「真實位置」例如 0, 1, 2, 3, 4, 5。**

🔧 那三行程式碼的作用是：
先用 ```label_positions / bin_width ```算出位置在哪個 bin：
|那個確切的 bin |
|--|
|0 / 0.5 = 0 → index 0|
|1 / 0.5 = 2 → index 2|
|2 / 0.5 = 4 → index 4|
|3 / 0.5 = 6 → index 6|
|4 / 0.5 = 8 → index 8|
|5 / 0.5 = 10 → index 10|

- 接著用 plt.xticks([0,2,4,6,8,10], ['0','1','2','3','4','5']) 來設定顯示的刻度。

- 最後 ```xlim(-0.5, len(bins) - 1.5)``` 是保證 bar 從最左邊到最右邊完整顯示，不被框線切掉。

📌 最簡單的結論：
1. ```label_positions / bin_width``` 是為了把「實際數值」對應到 bar 的「索引位置」。

2. ```xticks(...)``` 是設定你要顯示的刻度文字。

3. ```xlim(...)``` 是調整整張圖的範圍。