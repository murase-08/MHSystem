import pandas as pd

def compare_working_hours(company_data, jobkan_data):
    """
    会社の勤怠データとジョブカンの勤怠データを比較し、
    差異がある日をリストとして返す。
    
    Parameters:
        company_data (pd.DataFrame): 会社の勤怠データ（実働時間など）
        jobkan_data (pd.DataFrame): ジョブカンから取得した基準データ（実働時間など）

    Returns:
        List[str]: 差異がある日付のリスト
    """
    # 差異のある日付を記録するリスト
    difference_days = []

    # 日ごとの実働時間を比較する
    for i, row in company_data.iterrows():
        company_date = row['day']
        company_hours = row['worktime']

        # ジョブカンのデータと比較
        jobkan_row = jobkan_data[jobkan_data['day'] == company_date]
        if not jobkan_row.empty:
            jobkan_hours = jobkan_row.iloc[0]['worktime']
            
            # 完全一致比較
            if company_hours != jobkan_hours:
                # 差異があれば日付をリストに追加
                difference_days.append(company_date)
        else:
            # ジョブカンにその日付のデータが存在しない場合も差異として扱う
            difference_days.append(company_date)

    return difference_days


