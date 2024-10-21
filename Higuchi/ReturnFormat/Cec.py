import pdfplumber
import pandas as pd
from datetime import datetime, timedelta
import re

# 松井の会社のExcel読み込み関数
# 勤怠情報をExcelから読み込み、必要なカラムを抽出する関数
def read_cec_file(file_path):
    df = pd.read_excel(
        file_path, sheet_name="作業時間報告", engine="openpyxl", header=5
    )
    # 必要なカラムを抽出
    attendance_data = df[
        [
            "Unnamed: 1",
            "①作業開始時刻",
            "②作業終了時刻",
            "③休憩時間",
            "④作業時間\n②-①-③",
            "⑤超過/控除",
        ]
    ]
    attendance_data = attendance_data.rename(columns={"Unnamed: 1": "日付"})

    # 日付列のデータを数値型に変換。数値に変換できないデータは NaN として扱う
    attendance_data["日付"] = pd.to_numeric(attendance_data["日付"], errors="coerce")
    # 45413形式のシリアル値を日付形式に変換
    base_date = datetime(1899, 12, 30)  # Excelの日付シリアルの基準日
    attendance_data["日付"] = attendance_data["日付"].apply(
        lambda x: base_date + timedelta(days=x) if pd.notnull(x) else None
    )

    # 開始時刻・終了時刻・休憩時間のフォーマットを変更（'09:00:00' → '09:00'）
    time_columns = ["①作業開始時刻", "②作業終了時刻", "③休憩時間", "④作業時間\n②-①-③"]
    for col in time_columns:
        attendance_data[col] = attendance_data[col].apply(
            lambda x: (
                f"{int(x.total_seconds() // 3600):02}:{int((x.total_seconds() % 3600) // 60):02}"
                if isinstance(x, pd.Timedelta)
                else x
            )
        )
    # データを表示
    print(attendance_data)