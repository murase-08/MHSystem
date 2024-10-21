import pdfplumber
import pandas as pd
from datetime import datetime, timedelta
import re

# ㈱テクノクリエイティブのPDF読み込み関数
def read_tecnocreative_file(file_path):
    # 実働時間を計算するために、「開始」「終了」「休憩」「残業」を datetime 型に変換する関数
    def convert_to_time(val):
        try:
            return datetime.strptime(val, "%H:%M") if isinstance(val, str) else None
        except ValueError:
            return None

    # 実働時間を計算（終了 - 開始 - 休憩）
    def calculate_working_time(row):
        if pd.notnull(row["開始"]) and pd.notnull(row["終了"]):
            total_working_time = row["終了"] - row["開始"]
            if pd.notnull(row["休憩"]):
                total_working_time -= timedelta(
                    hours=row["休憩"].hour, minutes=row["休憩"].minute
                )
            return total_working_time
        return None

    # 実働時間を文字列で HH:MM 形式に変換
    def format_timedelta(td):
        if pd.notnull(td):
            total_seconds = int(td.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            return f"{hours:02}:{minutes:02}"
        return None

    def format_time(val):
        if pd.notnull(val):
            return val.strftime("%H:%M")
        return None

    # データの読み込みと処理
    data = []
    with pdfplumber.open(file_path) as pdf:
        page = pdf.pages[0]
        tables = page.extract_tables()
        for table in tables:
            for row in table[2:]:
                data.append(
                    {
                        "日付": row[0],
                        "開始": row[3],
                        "終了": row[4],
                        "休憩": row[5],
                        "定時": row[8],
                        "残業": row[9],
                        "深夜": row[10],
                        "休出": row[11],
                        "届出": row[12],
                        "備考": row[13],
                    }
                )
    pdf_df = pd.DataFrame(data)

    # '開始', '終了', '休憩', '残業' を datetime に変換
    pdf_df["開始"] = pdf_df["開始"].apply(convert_to_time)
    pdf_df["終了"] = pdf_df["終了"].apply(convert_to_time)
    pdf_df["休憩"] = pdf_df["休憩"].apply(convert_to_time)
    pdf_df["残業"] = pdf_df["残業"].apply(convert_to_time)

    # 実働時間の計算
    pdf_df["実働時間"] = pdf_df.apply(calculate_working_time, axis=1)

    # 実働時間を HH:MM 形式にフォーマット
    pdf_df["実働時間"] = pdf_df["実働時間"].apply(format_timedelta)
    # 開始、終了、休憩、残業をdatetimeからHH:MM 形式に直す
    pdf_df["開始"] = pdf_df["開始"].apply(
        lambda x: format_time(x) if isinstance(x, datetime) else x
    )
    pdf_df["終了"] = pdf_df["終了"].apply(
        lambda x: format_time(x) if isinstance(x, datetime) else x
    )
    pdf_df["休憩"] = pdf_df["休憩"].apply(
        lambda x: format_time(x) if isinstance(x, datetime) else x
    )
    pdf_df["残業"] = pdf_df["残業"].apply(
        lambda x: format_time(x) if isinstance(x, datetime) else x
    )
    # データを表示
    result_df = pdf_df[["日付", "実働時間", "開始", "終了", "休憩", "備考"]]
    print(result_df)