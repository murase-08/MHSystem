import pdfplumber
import pandas as pd
from datetime import datetime, timedelta
import re

# 株式会社システムシェアードのPDF読み込み関数
def read_systemshared_file(file_path):
    #何も編集がされていないそのまんまのテーブル
    pure_df = extract_systemshared_table(file_path)
    #フォーマットをそろえる
    format_df = sanitize_table(pure_df,file_path)
    #オブジェクトにformat_tableを入れて戻り値として返す
    # データフレームを辞書のリスト形式に変換
    dict_list = format_df.to_dict(orient='records')
    return dict_list
    
def sanitize_table(pure_df,file_path):
    #必要なカラムだけ抽出
    result_df = pure_df[["日付", "労働時間", "開始", "終了", "休憩時間", "メモ"]]
    # カラム名を変更
    result_df = result_df.rename(
        columns={"労働時間": "実働時間","開始": "開始時間", "終了": "終了時間", "メモ": "備考"}
    )
    # PDF内から20xxの年を抽出
    year = extract_year_from_pdf(file_path)
    
    # 日付を20xx-05-01形式に変換
    result_df["日付"] = result_df["日付"].apply(lambda x: convert_to_full_date(year, x))
    return result_df

# PDFから20xx年の年を抽出する関数
def extract_year_from_pdf(file_path):
    year_pattern = r"20\d{2}"
    with pdfplumber.open(file_path) as pdf:
        page = pdf.pages[0]
        text = page.extract_text()
        # 年の抽出
        match = re.search(year_pattern, text)
        if match:
            return match.group(0)  # 20xx形式の年を返す

# 日付をフォーマットする関数 (例: 5/1(水) -> 2024-05-01)
def convert_to_full_date(year, raw_date):
    # 例: "5/1(水)" から "5/1" を抽出
    date_match = re.match(r"(\d{1,2})/(\d{1,2})", raw_date)
    if date_match:
        month, day = date_match.groups()
        # "2024-05-01" 形式に変換
        formatted_date = f"{year}-{int(month):02d}-{int(day):02d}"
        return formatted_date
    return None

def extract_systemshared_table(file_path):
    data = []
    with pdfplumber.open(file_path) as pdf:
        page = pdf.pages[0]
        tables = page.extract_tables()

        # 勤怠データの処理
        for table in tables:
            for row in table[1:]:
                if len(row) == 11:
                    data.append(
                        {
                            "日付": row[0],
                            "勤怠区分": row[1],
                            "開始": row[2],
                            "終了": row[3],
                            "休憩時間": row[4],
                            "労働時間": row[5],
                            "時間外": row[6],
                            "深夜": row[7],
                            "法定休日": row[8],
                            "法定休日深夜": row[9],
                            "メモ": row[10],
                        }
                    )
    # データフレームに変換
    pdf_df = pd.DataFrame(data)
    return pdf_df