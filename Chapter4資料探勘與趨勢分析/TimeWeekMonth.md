## code 解釋
- 沿用 Realtime_situation 的資料架構，新增 4 個欄位分別為"日期"(幾月幾號)、"月份"、"星期幾"、"幾點"
- dt.date 會傳回一個 ```datetime.date``` 的 numpy array，以下舉例:
```
>>> s = pd.Series(["1/1/2020 10:00:00+00:00", "2/1/2020 11:00:00+00:00"])
>>> s = pd.to_datetime(s)
>>> s
0   2020-01-01 10:00:00+00:00
1   2020-02-01 11:00:00+00:00
dtype: datetime64[ns, UTC]
s.dt.date
0    2020-01-01
1    2020-02-01
dtype: object
```
- 原始碼如下
```python
timeline_df = pd.DataFrame(timeline, columns=["timestamp", "cars_in_parking"])
timeline_df["date"] = timeline_df["timestamp"].dt.date                  # 日期
timeline_df["month"] = timeline_df["timestamp"].dt.to_period("M")       # 月份
timeline_df["weekday"] = timeline_df["timestamp"].dt.dayofweek          # 星期幾 (0=一, 6=日)
timeline_df["hour"] = timeline_df["timestamp"].dt.hour                  # 小時
```

### 分月份的停車需求變化
### 分星期的停車需求變化
### 分時段的停車需求變化