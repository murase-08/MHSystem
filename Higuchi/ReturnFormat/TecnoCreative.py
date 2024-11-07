import pdfplumber
import pandas as pd
from datetime import datetime, timedelta
import re
import calendar
from Higuchi import Higuchi

# ㈱テクノクリエイティブのPDF読み込み関数
def read_tecnocreative_file(file_path):
    # 名前の取得
    full_name = extract_name_from_tecnocreative(file_path)
    print("ファイルの対象ユーザーは"+full_name+"です。")
    # 何も編集がされていないテーブル
    pure_df = extract_tecnocreative_table(file_path)
    # テーブルを第一フォーマットの形に変更
    firstFormat_df = change_firstFormat_tecnocreative(pure_df,file_path)
    englishFormat_df = firstFormat_df.rename(columns={
        "日付": "day", "実働時間": "worktime", "開始時間": "starttime",
        "終了時間": "endtime", "休憩時間": "resttime", "備考": "note"
        })
    dict_list = englishFormat_df.to_dict(orient='records')
    # 'day' の Timestamp を変換
    dict_list = convert_timestamps(dict_list)
    # work_data(名前と勤怠データを合わせたフォーマットにして返す
    work_data = Higuchi.format_to_work_data(full_name, dict_list)
    return work_data
    
# 実働時間を計算するために、「開始」「終了」「休憩」「残業」を datetime 型に変換する関数
def convert_to_time(val):
    try:
        return datetime.strptime(val, "%H:%M") if isinstance(val, str) else None
    except ValueError:
        return None

# 実働時間を計算（終了 - 開始 - 休憩）
def calculate_working_time(row):
    if pd.notnull(row["開始時間"]) and pd.notnull(row["終了時間"]):
        total_working_time = row["終了時間"] - row["開始時間"]
        if pd.notnull(row["休憩時間"]):
            total_working_time -= timedelta(
                hours=row["休憩時間"].hour, minutes=row["休憩時間"].minute
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

def extract_tecnocreative_table(file_path):
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
    return pdf_df

def change_firstFormat_tecnocreative(pure_df,file_path):
    # 必要なカラムだけ抽出
    result_df = pure_df[["日付", "開始", "終了", "休憩", "残業", "備考"]]
    # 空のカラムを追加（フォーマットを合わせるため）
    result_df = result_df.assign(実働時間=None)
    # カラム名を変更
    result_df = result_df.rename(
        columns={"開始": "開始時間", "終了": "終了時間", "休憩": "休憩時間", "残業": "残業時間"}
    )
    # カラムの順番を調整
    result_df = result_df[["日付", "実働時間", "開始時間", "終了時間", "休憩時間", "備考", "残業時間"]]
    # '開始時間', '終了時間', '休憩時間', '残業時間' を datetime に変換
    result_df["開始時間"] = result_df["開始時間"].apply(convert_to_time)
    result_df["終了時間"] = result_df["終了時間"].apply(convert_to_time)
    result_df["休憩時間"] = result_df["休憩時間"].apply(convert_to_time)
    result_df["残業時間"] = result_df["残業時間"].apply(convert_to_time)

    # 実働時間の計算
    result_df["実働時間"] = result_df.apply(calculate_working_time, axis=1)

    # 実働時間を HH:MM 形式にフォーマット
    result_df["実働時間"] = result_df["実働時間"].apply(format_timedelta)
    # 開始、終了、休憩、残業を datetime から HH:MM 形式に直す
    result_df["開始時間"] = result_df["開始時間"].apply(lambda x: format_time(x) if isinstance(x, datetime) else x)
    result_df["終了時間"] = result_df["終了時間"].apply(lambda x: format_time(x) if isinstance(x, datetime) else x)
    result_df["休憩時間"] = result_df["休憩時間"].apply(lambda x: format_time(x) if isinstance(x, datetime) else x)
    result_df["残業時間"] = result_df["残業時間"].apply(lambda x: format_time(x) if isinstance(x, datetime) else x)
    
    # データを表示
    result_df = result_df[["日付", "実働時間", "開始時間", "終了時間", "休憩時間", "備考"]]
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

# PDFから名前を取り出す
def extract_name_from_tecnocreative(file_path):
    with pdfplumber.open(file_path) as pdf:
        page = pdf.pages[0]
        tables = page.extract_tables()
        # "寺内 雄基 ㊞"
        name = tables[0][0][3]
        # "㊞"を削除して空白も取り除く
        # "寺内雄基"
        full_name = name.replace("㊞", "").replace(" ", "")
        return full_name