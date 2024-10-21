import pdfplumber
import pandas as pd
from datetime import datetime, timedelta
import re
# TDIシステムサービス株式会社のPDF読み込み関数
def read_tdisystem_file(file_path):
    data = []
    with pdfplumber.open(file_path) as pdf:
        page = pdf.pages[0]
        tables = page.extract_tables()
        for table in tables:
            for row in table[1:]:
                if len(row) >= 4:
                    data.append(
                        {
                            "日付": row[0],
                            "曜日": row[1],
                            "出勤日": row[2],
                            "実働時間": row[3],
                            "業務内容": row[4],
                        }
                    )
    pdf_df = pd.DataFrame(data)
    result_df = pdf_df[["日付", "実働時間", "業務内容"]]
    # 空のカラムを追加（フォーマットを合わせるため）
    result_df["開始時間"] = None
    result_df["終了時間"] = None
    result_df["休憩時間"] = None

    # カラムの順番を調整
    result_df = result_df[
        ["日付", "実働時間", "開始時間", "終了時間", "休憩時間", "業務内容"]
    ]
    # カラム名を変更
    result_df = result_df.rename(columns={"業務内容": "備考"})
    print(result_df)