import pandas as pd

# None、NaN、空文字、特定の値を '' に変換する関数
def normalize_worktime(worktime):
    if pd.isna(worktime) or worktime in ('', '00:00'):
        return ''  # None, NaN, '', '00:00' を空文字に変換
    return worktime  # その他の値はそのまま返す

# データ正規化
def normalize_days(days):
    return [{'day': day['day'], 'worktime': normalize_worktime(day['worktime'])} for day in days]

# 比較処理
def compare_work_time(customer_work_days, jobkan_work_days):
    # 正規化
    customer_work_days = normalize_days(customer_work_days)
    jobkan_work_days = normalize_days(jobkan_work_days)

    # 結果を格納する配列
    gap_days = []

    # 日付の数をチェック
    if len(customer_work_days) != len(jobkan_work_days):
        return "Number of days mismatch"

    # 日付と worktime の比較
    for customer, jobkan in zip(customer_work_days, jobkan_work_days):
        if customer['day'] != jobkan['day'] or customer['worktime'] != jobkan['worktime']:
            gap_days.append(customer['day'])

    return gap_days