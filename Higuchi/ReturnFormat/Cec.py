import pdfplumber
import pandas as pd
from datetime import datetime, timedelta,time
import re
import calendar
from Higuchi import Higuchi

# Cec読み込み関数
# 勤怠情報をExcelから読み込み、必要なカラムを抽出する関数
def read_cec_file(file_path):
    # 名前の取得
    full_name = extract_name_from_cec(file_path)
    print("ファイルの対象ユーザーは"+full_name+"です。")
    #何も編集がされていないテーブル
    pure_df = extract_cec_table(file_path)
    # テーブルを第一フォーマットの形に変更
    firstFormat_df = change_firstFormat_cec(pure_df,file_path)
     # カラム名を変更
    englishFormat_df = firstFormat_df.rename(columns={
        "日付": "day", "実働時間": "worktime", "開始時間": "starttime",
        "終了時間": "endtime", "休憩時間": "resttime", "備考": "note"
        })
    # データフレームを辞書のリスト形式に変換
    dict_list = englishFormat_df.to_dict(orient='records')
    # 'day' の Timestamp を変換
    dict_list = Higuchi.convert_timestamps(dict_list)
    # work_data(名前と勤怠データを合わせたフォーマットにして返す
    work_data = Higuchi.format_to_work_data(full_name, dict_list)
    return work_data

def change_firstFormat_cec(pure_df,file_path):
    # 年と月をExcelから取得
    year, month = extract_year_and_month_from_excel(file_path)
    # 月の日数を取得
    year = int(year)
    month = int(month)
    _, days_in_month = calendar.monthrange(year, month)
    
    result_df = pure_df.rename(columns={"Unnamed: 1": "日付"})
    # 日付列のデータを数値型に変換。数値に変換できないデータは NaN として扱う
    result_df["日付"] = pd.to_numeric(result_df["日付"], errors="coerce")
    # 45413形式のシリアル値を日付形式に変換
    base_date = datetime(1899, 12, 30)  # Excelの日付シリアルの基準日
    result_df["日付"] = result_df["日付"].apply(
        lambda x: base_date + timedelta(days=x) if pd.notnull(x) else None
    )
    # 休憩時間のフォーマットを変更
    result_df["③休憩時間"] = result_df["③休憩時間"].apply(format_time)
    time_columns = ["①作業開始時刻", "②作業終了時刻", "③休憩時間", "④作業時間\n②-①-③"]
    for col in time_columns:
        result_df[col] = result_df[col].apply(
            lambda x: (
                f"{int(x.total_seconds() // 3600):02}:{int((x.total_seconds() % 3600) // 60):02}"
                if isinstance(x, pd.Timedelta)
                else x
            )
        )
    # 空のカラムを追加（フォーマットを合わせるため）
    result_df.loc[:, "備考"] = None
    # カラム名を変更
    result_df = result_df.rename(
        columns={"①作業開始時刻": "開始時間", "②作業終了時刻": "終了時間","③休憩時間": "休憩時間", "④作業時間\n②-①-③": "実働時間"}
    )
    # カラムの順番を調整
    result_df = result_df[["日付", "実働時間", "開始時間", "終了時間", "休憩時間", "備考"]]
    
    # ここでいらない日付の行を消す(レコード数をその月の最大日数に制限)
    # いらない日付の行を削除（月の日数を超える日付を削除）
    result_df = result_df[result_df["日付"].dt.day <= days_in_month]
    # NaT、NaN、Noneを空文字に変える
    result_df = result_df.fillna("")
    return result_df

def format_time(x):
    # datetime.time型の場合、HH:MMにフォーマット
    if isinstance(x, time):
        return x.strftime("%H:%M")
    # 文字列型であればそのまま処理（必要に応じて文字列のカットなどを行う）
    elif isinstance(x, str) and len(x) == 8:
        return x[:5]
    # float型の場合、そのまま返す（もしくは他の処理をする）
    elif isinstance(x, float):
        return x
    # その他の場合、値をそのまま返す
    else:
        return x
   
def extract_year_and_month_from_excel(file_path):
    # Excelファイルを読み込む（年と月が特定のセルにあると仮定）
    wb = pd.read_excel(file_path, sheet_name="作業時間報告", engine="openpyxl")
    # 年は2行目のUnnamed: 2列、月は2行目のUnnamed: 4列にあります（0インデックスのため行は2）
    year = str(wb.loc[2, 'Unnamed: 2']).strip()  # 不要なスペースを削除
    month = str(wb.loc[2, 'Unnamed: 4']).strip()  # 不要なスペースを削除
    return year, month

# pure_dfの取り出し
def extract_cec_table(file_path):
    df = pd.read_excel(
        file_path, sheet_name="作業時間報告", engine="openpyxl", header=5
    )
    # 必要なカラムを抽出
    excel_df = df[
        [
            "Unnamed: 1",
            "①作業開始時刻",
            "②作業終了時刻",
            "③休憩時間",
            "④作業時間\n②-①-③",
            "⑤超過/控除",
        ]
    ]
    return excel_df

def extract_name_from_cec(file_path):
    df = pd.read_excel(
        file_path, sheet_name="作業時間報告", engine="openpyxl", header=0
    )
    dict_list = df.to_dict(orient='records')
    data = dict_list[2]
    # "Unnamed: 8"の値を取得
    name = data.get('Unnamed: 8')
    # 空白(全角/半角)を削除
    full_name = name.replace("　", "").replace(" ", "")
    return full_name
