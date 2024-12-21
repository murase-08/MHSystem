def generate_difference_report(data):
    # 結果を格納する文字列
    result = ["実行結果"]

    # 配列内の各辞書を処理
    for record in data:
        # 各フィールドを取得
        file_name = record.get('customer_file_name', '不明なファイル名')
        employee_name = record.get('name', '不明な従業員名')
        gap_days = record.get('gap_days', [])

        # 差異日をカンマ区切りの文字列に変換
        gap_days_str = ','.join(gap_days) if gap_days else '差異日なし'

        # フォーマットを整えて文字列に追加
        result.append(f"ファイル名：{file_name}")
        result.append(f"従業員名  ：{employee_name}")
        result.append(f"差異日    ：{gap_days_str}")
        result.append("")  # 改行用

    # 最後のメッセージを追加
    result.append("差異検出は終了です")

    # 改行で文字列を結合して返す
    return '\n'.join(result)