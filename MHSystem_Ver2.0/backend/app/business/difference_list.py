from app.data_access import dbconnect

def get_false_data():
    # データベースからデータを取得
    false_datas = dbconnect.get_false_data_table()
    print(false_datas)
    differences = []

    # 各データを処理してフォーマット
    for false_data in false_datas:
        # 修正箇所: 辞書キーを正しく記述（変数名ではなく文字列で囲む）
        difference = {
            'yearMonth': false_data['check_year_month'],
            'fileName': false_data['file_name'],
            'name': false_data['name'],
            'dates': false_data['false_days'].split(', ')  # 文字列を配列に変換
        }
        # 修正箇所: `defferences` → `differences`（スペルミス修正）
        differences.append(difference)
    
    # 修正箇所: 正しい戻り値を返す（`differences` を返す）
    return differences