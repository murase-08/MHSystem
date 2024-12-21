import pandas as pd
import re
from datetime import datetime, timedelta
import pdfplumber
import os
import numpy as np

# work_data(名前と勤怠データを合わせたフォーマットにして返す
def format_to_work_data(full_name, dict_list):
    # work_dataフォーマットに変換
    work_data = {
        "name": full_name,
        "work_days": dict_list
    }
    return work_data

# 'day' の pd.Timestamp 型を文字列(YYYY-MM-DD)に変換する関数
def convert_timestamps(dict_list):
    for record in dict_list:
        # 'day' キーに対応する値が、pd.Timestamp 型かどうかを確認
        if isinstance(record['day'], pd.Timestamp):
            record['day'] = record['day'].strftime('%Y-%m-%d')
    return dict_list

# 日付フォーマット "2024/05/01" → "2024-05-01" に変更する関数
def convert_date_format(date_str):
    try:
        return date_str.replace('/', '-')  # スラッシュをハイフンに置き換え
    except AttributeError:
        return date_str  # 万が一エラーが出た場合は元の値を返す
    
# 日付を "20xx-MM-01" 形式に変換する関数
def convert_to_full_date_p1(year, month, day):
    # 日付が None または空の場合は None を返す
    if day is None or day == "":
        return None
    try:
        return f"{year}-{month}-{int(day):02d}"
    except ValueError:
        return None

# 日付をフォーマットする関数 (例: 5/1(水) -> 2024-05-01)
def convert_to_full_date_p2(year, raw_date):
    # 例: "5/1(水)" から "5/1" を抽出
    date_match = re.match(r"(\d{1,2})/(\d{1,2})", raw_date)
    if date_match:
        month, day = date_match.groups()
        # "2024-05-01" 形式に変換
        formatted_date = f"{year}-{int(month):02d}-{int(day):02d}"
        return formatted_date
    return None

# 日付けをフォーマットする関数(5月1日 → 2024-05-01)
def convert_to_full_date_p3(year, partial_date):
    # 正規表現で「月」と「日」を抽出
    match = re.match(r"(\d+)月(\d+)日", partial_date)
    if not match:
        # 無効な形式の場合は None を返す
        return None
    # 月と日を抽出してゼロ埋め
    month = match.group(1).zfill(2)
    day = match.group(2).zfill(2)
    # 完全な日付を生成
    full_date = f"{year}-{month}-{day}"
    return full_date

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
        
# PDFから西暦と月を抽出する関数
def extract_year_and_month_from_pdf(file_path):
    # PDFから西暦（20xx）と月を抽出する処理
    year_pattern = r"20\d{2}"
    month_pattern = r"([1-9]|1[0-2])\s*月"
    with pdfplumber.open(file_path) as pdf:
        # PDFの最初のページを対象とする
        page = pdf.pages[0]
        text = page.extract_text()
        # 年の抽出
        year_match = re.search(year_pattern, text)
        year = year_match.group(0) if year_match else None
        # 月の抽出
        month_match = re.search(month_pattern, text)
        if month_match:
            month = month_match.group(1).zfill(2)  # 1桁の場合は0埋めする
        else:
            month = None  # 月が見つからない場合は None を返す
        # 年または月が抽出できない場合の例外処理（必要に応じて）
        if not year or not month:
            raise ValueError("年または月がPDFから抽出できませんでした。")
        return year, month
    
# 実働時間の小数点を "HH:MM" に変換する関数　8.25→08:15
def convert_hours_to_time(hours):
    if hours is None or hours == "":  # 空またはNoneのチェック
        return None
    try:
        # 文字列型を浮動小数点型に変換
        hours_float = float(hours)
        # 時間を取得
        h = int(hours_float)
        # 分に変換して取得
        m = int((hours_float - h) * 60)
        return f"{h:02d}:{m:02d}"
    except ValueError:
        return None  # 値が無効な場合(例えば "abc" など)はNoneを返す
    
# 時間を文字列から datetime.time 型に変換
def convert_to_time(val):
    try:
        return datetime.strptime(val, "%H:%M") if isinstance(val, str) else None
    except ValueError:
        return None
    
# timedelta 型の値を「HH：MM」形式の文字列に変換
def format_timedelta(td):
    if pd.notnull(td):
        total_seconds = int(td.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}"
    return None

# datetime 型や time 型の値を「HH：MM」形式の文字列に変換
def format_time(val):
    if pd.notnull(val):
        return val.strftime("%H:%M")
    return None

# 実働時間をフォーマット
def format_worktimeB(val):
    if isinstance(val, str) and re.match(r"^\d{1,2}:\d{2}$", val):  # HH:MM形式の文字列をチェック
        hours, minutes = val.split(":")
        return f"{int(hours):02d}:{minutes}"  # 時間を2桁にフォーマット
    return val  # 無効な値はそのまま返す

# 無効な値を NaN に変換する関数
def replace_invalid_with_nan(val):
    if isinstance(val, str) and not pd.isna(val):  # 値が文字列で有効でない場合
        if not re.match(r"^\d{1,2}:\d{2}$", val):  # 正規表現に一致しない場合
            return np.nan
    return val  # 有効な値または NaN の場合はそのまま返す

# 実働時間を計算（終了 - 開始 - 休憩）
def calculate_working_time(row):
    if pd.notnull(row["開始時間"]) and pd.notnull(row["終了時間"]):
        total_working_time = row["終了時間"] - row["開始時間"]
        # 休憩時間 が存在しない場合は、「終了時間 - 開始時間」を返します。
        if pd.notnull(row["休憩時間"]):
            total_working_time -= timedelta(
                hours=row["休憩時間"].hour, minutes=row["休憩時間"].minute
            )
        return total_working_time
    return None

# 従業員名と一致するジョブカンのファイルパスを返す
def find_file_with_name(directory, keyword):
    # フォルダ以下を再帰的に検索
    for root, dirs, files in os.walk(directory):
        for file in files:
            if keyword in file:  # ファイル名にキーワードが含まれているか
                file_path = os.path.join(root, file)
                return file_path  # 最初に見つかったファイルのパスを返す
    return None  # 見つからない場合は None を返す
    
# ファイルパスを取得してplumberが使えるPDFだけを返す
def get_plumber_can_read_files(specific_customer_file_path):
    with pdfplumber.open(specific_customer_file_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            if tables:
                return specific_customer_file_path