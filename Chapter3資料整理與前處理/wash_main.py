"""主程式入口，進行原始 Excel 停車紀錄資料清洗與整理。

依據日期與車號修正票種資訊，並過濾無效紀錄後輸出成統一格式。
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime

# Constants
DATETIME_FORMAT = "%Y/%m/%d"
MAGIC_NUM = 0  # 0: notebook, 1: desktop


# Set paths
directory_path = os.getcwd()
if MAGIC_NUM == 0:
    INPUT_DIR = r"C:/Cody/Research/source"
    OUTPUT_FILE = r"C:/Cody/Research/clean_data/prepare.csv"
elif MAGIC_NUM == 1:
    INPUT_DIR = r"D:/Research/source"
    OUTPUT_FILE = r"D:/Research/clean_data/prepare.csv"
else:
    print("Invalid MAGIC_NUM setting.")
    exit(1)

# Expected column order
COLUMN_NAMES = [
    "車號", "票種", "子場站", "進出及付費狀態", "校正狀態",
    "進站設備", "出站設備", "進入日", "進入時間", "出場日",
    "出場時間", "停留時數", "計價代碼", "紀錄時間"
]

# Mapping for standardizing ticket types
TICKET_TYPE_MAPPING = {
    "教職汽車證": "教職員汽車",
    "教職計次證": "教職員計次",
    "學生長時汽車證": "學生長時汽車",
    "學生計次證": "學生計次汽車",
    "廠商汽車": "長時廠商汽車",
    "退休校友證": "退休及校友汽車識別證",
    "在職專班證": "在職專班汽車"
}