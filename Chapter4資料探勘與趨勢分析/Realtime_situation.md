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



