import pdfplumber
import pandas as pd
from datetime import datetime, timedelta
import re

# 株式会社システムサポートのPDF読み込み関数
def read_systemsupport_file(file_path):
    data = []
    with pdfplumber.open(file_path) as pdf:
        page = pdf.pages[0]
        tables = page.extract_tables()
        for table in tables:
            for row in table[9:]:
                if len(row) >= 6:
                    data.append(
                        {
                            "日": row[0],
                            "曜日": row[1],
                            "開始": row[2],
                            "終了": row[4],
                            "休憩": row[6],
                            "作業時間": row[7],
                            "作業内容": row[8],
                        }
                    )
    pdf_df = pd.DataFrame(data)
    result_df = pdf_df[["日", "作業時間", "開始", "終了", "休憩", "作業内容"]]
    # カラム名を変更
    result_df = result_df.rename(
        columns={
            "日": "日付",
            "作業時間": "実働時間",
            "開始": "開始時間",
            "終了": "終了時間",
            "休憩": "休憩時間",
            "作業内容": "備考",
        }
    )
    print(result_df)