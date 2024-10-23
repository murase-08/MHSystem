import pdfplumber
import pandas as pd
from datetime import datetime, timedelta
import re
import calendar

# 株式会社システムサポートのPDF読み込み関数
def read_systemsupport_file(file_path):
    #何も編集がされていないテーブル
    pure_df = extract_systemsupport_table(file_path)
    format_df = sanitize_systemsupport(pure_df,file_path)
    # カラム名を変更
    format_df = format_df.rename(columns={"日付": "day", "実働時間": "worktime", "開始時間": "starttime", "終了時間": "endtime", "休憩時間": "resttime", "備考": "note"})
    dict_list = format_df.to_dict(orient='records')
    # 'day' の Timestamp を変換
    dict_list = convert_timestamps(dict_list)
    return dict_list

#取得対象のテーブルを取得する
def extract_systemsupport_table(file_path):
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
    return pdf_df

def sanitize_systemsupport(pure_df,file_path):
    result_df = pure_df[["日", "作業時間", "開始", "終了", "休憩", "作業内容"]]
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
    # PDFから動的に西暦と月を抽出して、日付を "20xx-MM-01" 形式に変更する
    year, month = extract_year_and_month_from_pdf(file_path)
    result_df["日付"] = result_df["日付"].apply(lambda x: convert_to_full_date(year, month, x))
    # 日付カラムを datetime 型に変換し、無効な日付を除外
    result_df["日付"] = pd.to_datetime(result_df["日付"], errors='coerce', format="%Y-%m-%d")
    
    # 年と月を確認し、float型になっていた場合は整数に変換
    max_day = calendar.monthrange(int(year), int(month))[1]

    # 日付がNoneでないかつその月の日付数以内のデータだけを抽出
    result_df = result_df[result_df["日付"].notna() & (result_df["日付"].dt.day <= max_day)]
    # レコード数をその月の最大日数に制限する
    result_df = result_df.head(max_day)
    return result_df

def extract_year_and_month_from_pdf(file_path):
    # PDFから西暦（20xx）と月を抽出する処理
    year_pattern = r"20\d{2}"
    month_pattern = r"([1-9]|1[0-2])月"  # 「○月」の形式にマッチ
    with pdfplumber.open(file_path) as pdf:
        page = pdf.pages[0]
        text = page.extract_text()
        year_match = re.search(year_pattern, text)
        month_match = re.search(month_pattern, text)
        year = year_match.group(0) if year_match else "2024"
        # 「○月」形式にマッチする部分を探す
        month_match = re.search(month_pattern, text)
        if month_match:
            month = month_match.group(1).zfill(2)  # 1桁の場合は0埋めする
        else:
            month = "05"  # 月が見つからない場合のデフォルト値
        return year, month

# 日付を "20xx-MM-01" 形式に変換する関数
def convert_to_full_date(year, month, day):
    # 日付が None または空の場合は None を返す
    if day is None or day == "":
        return None
    try:
        return f"{year}-{month}-{int(day):02d}"
    except ValueError:
        return None
# 'day' の Timestamp を文字列に変換する関数
def convert_timestamps(dict_list):
    for record in dict_list:
        if isinstance(record['day'], pd.Timestamp):
            record['day'] = record['day'].strftime('%Y-%m-%d')
    return dict_list