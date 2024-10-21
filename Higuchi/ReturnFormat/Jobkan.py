import pdfplumber
import pandas as pd
from datetime import datetime, timedelta
import re
def read_jobkan_file(file_path):
    data = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                print(table[2:])
                for row in table[2:]:
                    data.append(
                        {
                            "日付": row[0],
                            "開始": row[1],
                            "終了": row[2],
                            "普通": row[3],
                            "深夜": row[4],
                        }
                    )
    pdf_df = pd.DataFrame(data)
    print(pdf_df)