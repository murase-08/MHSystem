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
    dict_list = Higuchi.convert_timestamps(dict_list)
    # work_data(名前と勤怠データを合わせたフォーマットにして返す
    work_data = Higuchi.format_to_work_data(full_name, dict_list)
    return work_data

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
    result_df["開始時間"] = result_df["開始時間"].apply(Higuchi.convert_to_time)
    result_df["終了時間"] = result_df["終了時間"].apply(Higuchi.convert_to_time)
    result_df["休憩時間"] = result_df["休憩時間"].apply(Higuchi.convert_to_time)
    result_df["残業時間"] = result_df["残業時間"].apply(Higuchi.convert_to_time)

    # 実働時間の計算
    result_df["実働時間"] = result_df.apply(Higuchi.calculate_working_time, axis=1)

    # 実働時間を HH:MM 形式にフォーマット
    result_df["実働時間"] = result_df["実働時間"].apply(Higuchi.format_timedelta)
    # 開始、終了、休憩、残業を datetime から HH:MM 形式に直す
    result_df["開始時間"] = result_df["開始時間"].apply(lambda x: Higuchi.format_time(x) if isinstance(x, datetime) else x)
    result_df["終了時間"] = result_df["終了時間"].apply(lambda x: Higuchi.format_time(x) if isinstance(x, datetime) else x)
    result_df["休憩時間"] = result_df["休憩時間"].apply(lambda x: Higuchi.format_time(x) if isinstance(x, datetime) else x)
    result_df["残業時間"] = result_df["残業時間"].apply(lambda x: Higuchi.format_time(x) if isinstance(x, datetime) else x)
    
    # データを表示
    result_df = result_df[["日付", "実働時間", "開始時間", "終了時間", "休憩時間", "備考"]]
    # PDFから動的に西暦と月を抽出して、日付を "20xx-MM-01" 形式に変更する
    year, month = Higuchi.extract_year_and_month_from_pdf(file_path)
    result_df["日付"] = result_df["日付"].apply(lambda x: Higuchi.convert_to_full_date_p1(year, month, x))
    # 日付カラムを datetime 型に変換し、無効な日付を除外
    result_df["日付"] = pd.to_datetime(result_df["日付"], errors='coerce', format="%Y-%m-%d")
    
    # 年と月を確認し、float型になっていた場合は整数に変換
    max_day = calendar.monthrange(int(year), int(month))[1]

    # 日付がNoneでないかつその月の日付数以内のデータだけを抽出
    result_df = result_df[result_df["日付"].notna() & (result_df["日付"].dt.day <= max_day)]
    # レコード数をその月の最大日数に制限する
    result_df = result_df.head(max_day)
    
    return result_df

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