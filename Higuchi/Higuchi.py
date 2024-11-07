from Higuchi.ReturnFormat import Jobkan,SystemShared,TecnoCreative,TdiSystemSurvice,Totec,SystemSupport,Cec
import pandas as pd
import re
from datetime import datetime, timedelta
import pdfplumber
#会社コード(CD)に応じたFormat関数を呼び出します
def read_file(file_path,companyCode):
    # ジョブカン
    if companyCode == 0:
        return Jobkan.read_jobkan_file(file_path)
    # システムシェアード
    elif companyCode == 1:
        return SystemShared.read_systemshared_file(file_path)
    # テクノクリエイティブ
    elif companyCode == 2:
        return TecnoCreative.read_tecnocreative_file(file_path)
    # TDIシステムサービス
    elif companyCode == 3:
        return TdiSystemSurvice.read_tdisystem_file(file_path)
    # トーテック
    elif companyCode == 4:
        return Totec.read_totec_file(file_path)
    # システムサポート
    elif companyCode == 5:
        return SystemSupport.read_systemsupport_file(file_path)
    # CEC
    elif companyCode == 6:
        return Cec.read_cec_file(file_path)
    else:
        print("存在しない会社です。")
        
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