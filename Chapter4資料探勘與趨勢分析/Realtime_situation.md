## code 解釋
```python 
time_changes = {}

for _, row in df.iterrows():
    in_time = row["in_time"]
    out_time = row["out_time"]
    time_changes[in_time] = time_changes.get(in_time, 0) + 1
    time_changes[out_time] = time_changes.get(out_time, 0) - 1
```
- 不想每秒都去數場內有多少車，太慢了，只關心啥時變化->ex. 幾點幾分有車進來，就記錄下來。
- ```time_changes``` 先建立差分字典，如下圖範例之動作
    - "差分"的意思是相鄰兩數的差值，例如一個數列a1 a2 a3 a4...，就是指a2-a1 a3-a2...
##
(範例) 假設有三台車子進出場紀錄
| 車輛 | 進場時間  | 出場時間  |
| -- | ----- | ----- |
| A  | 08:00 | 08:30 |
| B  | 08:15 | 08:45 |
| C  | 08:30 | 09:00 |
- 則他會建立一個字典:
```python
time_changes = {
    '08:00': +1,  # A 進場
    '08:15': +1,  # B 進場
    '08:30': -1,  # A 出場
    '08:30': +1,  # C 進場 -> 所以變成 +=1
    '08:45': -1,  # B 出場
    '09:00': -1   # C 出場
}
```
- 同一個時間點可能進出多台車，所以用``` .get(..., 0) + 1```來累加。
```python
time_changes[in_time] = time_changes.get(in_time, 0) + 1
time_changes[out_time] = time_changes.get(out_time, 0) - 1
```
這樣結果就會變成
```python
time_changes = {
    '08:00': +1,
    '08:15': +1,
    '08:30': 0,    # -1 (A 出) +1 (C 進)
    '08:45': -1,
    '09:00': -1
}
```
##
- 接著對這些時間 1.排序 2.累加
```python
timeline = []
count = 0

for time in sorted(time_changes.keys()):
    count += time_changes[time]
    timeline.append((time, count))
```
| 時間    | 場內車數          |
| ----- | ------------- |
| 08:00 | 1（A進）         |
| 08:15 | 2（B進）         |
| 08:30 | 2（A出但C進，所以不變） |
| 08:45 | 1（B出）         |
| 09:00 | 0（C出）         |



### 總結
<span style="color: white; background-color: black; font-size: 20px"><b>💥 ```time_changes``` 就是一個字典，紀錄 "那些時間點數量會變化" 以及 "變化量"，這樣就可以快速算出每個有變化時間點的總車數</b></span>



### 📄 每日補正車輛數表格欄位說明：
| 欄位名稱        | 說明                                        |
| ----------- | ----------------------------------------- |
| **尖峰時間**    | 指當天**在場車數最多**發生的時間點（例如：13:15 也就是實際上的 13:15:00 ~ 13:29:59）。是當日車流的高峰時刻。 |
| **原始最大車數**  | 當天根據有效資料計算出的**最大在場車輛數**。不包含任何補正（即：純淨統計值）。 |
| **錯誤資料數**   | 該日被排除的異常資料筆數，例如：車牌錯誤、進出時間缺失、不合法紀錄等。       |
| **補正車數**    | 根據錯誤資料估算應補回的車輛數，假設這些錯誤中有一定比例屬於尖峰時段進場。     |
| **補正後最大車數** | 將原始最大車數加上補正車數後得到的**修正值**，用來更貼近實際場內車流。     |


### 關於補正車數

- 補正邏輯是根據以下假設：
```
錯誤資料雖然被排除，但其中一部分應該也發生在尖峰時段，所以我們用「尖峰時段佔全部進場的比例」來估算這些錯誤資料中有多少應該算進尖峰車流。
```

<span style="color: yellow; background-color: black; font-size: 20px">補正車數=漏算筆數資料數×尖峰進場比例</span>

**尖峰比例** = 統計所有資料中有多少車是在尖峰時間（9~16）進場
```python
# 計算尖峰比例（在 in_time 中）
df["in_hour"] = df["in_time"].dt.hour
peak_ratio = len(df[(df["in_hour"] >= PEAK_HOUR_START) & (df["in_hour"] <= PEAK_HOUR_END)]) / len(df)
```

假設錯誤資料的時間分布也差不多，用這個 **尖峰比例** 乘上 **錯誤筆數** ，<span style="color: yellow; background-color: black; font-size: 20px">大概估計出那天漏算了幾台尖峰車</span>
1. 算補正車數（estimated_peak_addition）
2. 加到原始最大車數上，得到補正後最大車數（corrected_peak）
```python
peak_df["estimated_peak_addition"] = (peak_df["error_count"] * peak_ratio).round().astype(int)
peak_df["corrected_peak"] = peak_df["cars_in_parking"] + peak_df["estimated_peak_addition"]
```

