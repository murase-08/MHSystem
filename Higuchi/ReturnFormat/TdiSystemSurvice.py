import pdfplumber
import pandas as pd
from datetime import datetime, timedelta
import re
import calendar
# TDIシステムサービス株式会社のPDF読み込み関数
def read_tdisystem_file(file_path):
    # PDFから名前を取り出す
    full_name = extract_name_from_tdisystem(file_path)
    print("ファイルの対象ユーザーは"+full_name+"です。")
    #何も編集がされていないテーブル
    pure_df = extract_tdisystem_table(file_path)
    format_df = sanitize_tdisystem(pure_df,file_path)
    # カラム名を変更
    format_df = format_df.rename(columns={"日付": "day", "実働時間": "worktime", "開始時間": "starttime", "終了時間": "endtime", "休憩時間": "resttime", "備考": "note"})
    dict_list = format_df.to_dict(orient='records')
    # 'day' の Timestamp を変換
    dict_list = convert_timestamps(dict_list)
    # work_dataにフォーマット
    work_data = format_to_work_data(full_name, dict_list)
    return work_data

def sanitize_tdisystem(pure_df, file_path):
    result_df = pure_df[["日付", "実働時間", "業務内容"]]
    
    # 空のカラムを追加（フォーマットを合わせるため）
    result_df.loc[:, "開始時間"] = None
    result_df.loc[:, "終了時間"] = None
    result_df.loc[:, "休憩時間"] = None
    
    # カラム名を変更
    result_df = result_df.rename(columns={"業務内容": "備考"})
    
    # PDFから動的に西暦と月を抽出して、日付を "20xx-MM-01" 形式に変更する
    year, month = extract_year_and_month_from_pdf(file_path)
    result_df["日付"] = result_df["日付"].apply(lambda x: convert_to_full_date(year, month, x))
    # 実働時間の小数点表記を "HH:MM" 表記に変換
    result_df["実働時間"] = result_df["実働時間"].apply(convert_working_hours)
    
    # 日付カラムを datetime 型に変換し、無効な日付を除外
    result_df["日付"] = pd.to_datetime(result_df["日付"], errors='coerce', format="%Y-%m-%d")
    
    # 年と月を確認し、float型になっていた場合は整数に変換
    max_day = calendar.monthrange(int(year), int(month))[1]

    # 日付がNoneでないかつその月の日付数以内のデータだけを抽出
    result_df = result_df[result_df["日付"].notna() & (result_df["日付"].dt.day <= max_day)]

    # カラムの順番を調整
    result_df = result_df[["日付", "実働時間", "開始時間", "終了時間", "休憩時間", "備考"]]

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

# 実働時間の小数点を "HH:MM" に変換する関数
def convert_working_hours(hours):
    # None または空文字の場合はそのまま返す
    if hours is None or hours == "":
        return None
    try:
        # 実働時間を小数（例: 8.25）から "HH:MM" の形式に変換する
        hours_float = float(hours)
        hours_int = int(hours_float)
        minutes = int((hours_float - hours_int) * 60)
        return f"{hours_int:02d}:{minutes:02d}"
    except ValueError:
        return None  # 実働時間が無効な形式の場合も None を返す
    
def extract_tdisystem_table(file_path):
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
    return pdf_df
# 'day' の Timestamp を文字列に変換する関数
def convert_timestamps(dict_list):
    for record in dict_list:
        if isinstance(record['day'], pd.Timestamp):
            record['day'] = record['day'].strftime('%Y-%m-%d')
    return dict_list

# PDFから名前を取り出す
def extract_name_from_tdisystem(file_path):
    with pdfplumber.open(file_path) as pdf:
        page = pdf.pages[0]
        tables = page.extract_tables()
        # 株式会社アイティークロス\n大平 崇
        name = tables[0][35][0]
        # 改行で分割して下の名前部分を取得、空白を削除
        full_name = name.split('\n')[-1].replace(" ", "")
        
        # 出力結果: 大平崇
        return full_name
def format_to_work_data(name, dict_list):
    # work_dataフォーマットに変換
    work_data = {
        "name": name,
        "work_days": dict_list
    }
    return work_data