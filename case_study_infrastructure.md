# **關於研究架構圖**

## 🔧 「研究架構圖」：

### 1. 你研究的核心問題是什麼？
#### 🤷‍♂️ 國立陽明交通大學光復校區的上班尖峰時段總是找不到停車位，如何解決?

### 2. 你用哪些資料、方法、變數來分析？

| **相關資料**         | **內容**                                      |
|----------------------|----------------------------------------------|
| 🚗 車牌辨識系統資料  | `進出時間`、`日期`、`車號`、`票種`           |
| 🏤 校園交通管理規章、細則 | `票種領取規範`、`數量`、`申請資格`、`使用規則` |

---

### 方法與變數

- **方法**：
  - 📈 時間序列分析（Time Series Analysis）
  - 🔍 數據聚類（Clustering）
  - ✅ 統計檢驗（Statistical Testing）

- **變數**：
  - 獨立變數：`車號`、`票種`
  - 依賴變數：`進出時間` 、 `停車頻率`

---


### 3. 停車管理需求是什麼

### 1️⃣ <span style="background-color: #2c3e50; padding: 2px; color: white;"> 是否為過夜停車戶造成的 ?</span>

### 2️⃣ <span style="background-color: #ffff99; padding: 2px; color: #333333;"> 是否有可能為票種濫用/分發數量過多 ?</span>

### 3️⃣ <span style="background-color: #cce5ff; padding: 2px; color: #2c3e50;"> 停車位不足 ?</span>
---

# 碩論規劃

## Chapter1 緒論

```
文件
需求訪談，
寫不出文件就沒有用

學校的大巴士
需求是什麼?
車證的規則架構規則架構

問管理者的需求

需求 -> 分析 -> 呈現

把規則寫出來
```
- 研究背景（校園停車問題日益嚴重）
- 研究動機（教職員抱怨找不到位子，是否票種設計出問題？） 
- 研究目的與問題（有哪些因素造成平日停車不足？如何改善？）
- 研究範圍與限制（以陽明交大校區為主，資料僅限2023年）
- 研究流程簡圖

## Chapter2 文獻探討

- Case study 是什麼？選擇個案研究
  - What is a case study?    - Roberta Heale, Alison Twycross
```
需求管理系統
user需求是什麼(flow chart)


早期沒有車辨系統，有數據後就要開始思索如何管理，長期以來都是駐警隊在管，但缺乏完整評估過
```



- 數據如何處理?
  - A Review on Data Cleansing Methods for Big Data  - F. Ridzuan and W. M. N. W. Zainon
- 停車供需分析的相關理論(以車辨系統之資料做挖掘)
  - The effectiveness of parking policies to reduce parking demand pressure and car use -S. Norhisham and N. Ismail
- 國內外大學停車管理研究與改善實例
  - Dealing with parking issues on an urban campus: The case of UC Berkeley -W. Riggs

## Chapter3 研究方法

- 資料來源與說明（進出紀錄欄位有哪些？怎麼定義過夜停車、長期佔用等？）
- 分析架構與步驟（可用你之前那張圖修改為正式研究流程或研究架構）
- 分析方法：
  - 使用Python/Excel/R 等工具處理資料
  - 時段分析（哪些時間段最擁擠）
  - 過夜停車偵測（進出時間差超過24hr）
  - 車牌分類分析（是否學生用教職員票種？）
  - 分區負載率分析（每區車位使用率）

## Chapter4 研究結果與討論

- 各區各時段使用狀況
- 異常行為分析結果
- 與學生/教職員需求的落差
- 校方票種政策設計的盲點

## Chapter5 結論與建議

- 研究發現彙整
- 管理建議
- 後續研究建議