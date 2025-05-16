pre_filter_count = len(reorder_data)
    # reorder_data = reorder_data[
    #     (~reorder_data["車號"].str.contains(r"\*", na=False)) &  # 移除 `*`
    #     (reorder_data["車號"].str.len().between(4, 7))  # 保留長度 4~7 碼
    # ]
    # car_number_dropped = pre_filter_count - len(reorder_data)
    # print(f"因車號異常（長度不在 4~7）刪除了 {car_number_dropped} 筆資料")