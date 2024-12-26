import pdfplumber
import re
import pandas as pd
import calendar
import pdfplumber
import pandas as pd
from datetime import datetime, timedelta
import re
import calendar
from app.business import util

# ジョブカンPDFファイルの読み込み関数
def read_ntpsystem_file(file_path):
    # 名前の取得
    full_name = extract_name_from_ntpsystem(file_path)
    #何も編集がされていないテーブル
    pure_df = extract_ntpsystem_table(file_path)
    # テーブルを第一フォーマットの形に変更
    firstFormat_df = change_firstFormat_ntpsystem(pure_df,file_path)
     # カラム名を変更
    englishFormat_df = firstFormat_df.rename(columns={
        "日付": "day", "実働時間": "worktime", "開始時間": "starttime",
        "終了時間": "endtime", "休憩時間": "resttime", "備考": "note"
        })
    # データフレームを辞書のリスト形式に変換
    dict_list = englishFormat_df.to_dict(orient='records')
    # 'day' の Timestamp を変換
    dict_list = util.convert_timestamps(dict_list)
    # work_data(名前と勤怠データを合わせたフォーマットにして返す
    work_data = util.format_to_work_data(full_name, dict_list)
    return work_data

def change_firstFormat_ntpsystem(pure_df,file_path):
    result_df = pure_df[["日", "勤怠時間計", "始業時刻", "終業時刻","備考"]]
    # 空のカラムを追加（フォーマットを合わせるため）
    # result_df.loc[:, "備考"] = None
    result_df = result_df.assign(休憩時間=None)
    # カラム名を変更
    result_df = result_df.rename(
        columns={"日": "日付","勤怠時間計": "実働時間", "始業時刻": "開始時間", "終業時刻": "終了時間"}
    )
    # カラムの順番を調整
    result_df = result_df[["日付", "実働時間", "開始時間", "終了時間", "休憩時間", "備考"]]
    
    # 実働時間のフォーマットを「8:00」から「08:00」に変換
    result_df["実働時間"] = result_df["実働時間"].apply(lambda x: x.zfill(5) if pd.notnull(x) and ':' in x else x)
    # 開始時間のフォーマットを「8:00」から「08:00」に変換
    result_df["開始時間"] = result_df["開始時間"].apply(lambda x: x.zfill(5) if pd.notnull(x) and ':' in x else x)
    # 終了時間のフォーマットを「8:00」から「08:00」に変換
    result_df["終了時間"] = result_df["終了時間"].apply(lambda x: x.zfill(5) if pd.notnull(x) and ':' in x else x)
    
    # PDFから動的に西暦と月を抽出して、日付を "20xx-MM-01" 形式に変更する
    year, month = util.extract_year_and_month_from_pdf(file_path)
    result_df["日付"] = result_df["日付"].apply(lambda x: util.convert_to_full_date_p1(year, month, x))
    # 日付カラムを datetime 型に変換し、無効な日付を除外
    result_df["日付"] = pd.to_datetime(result_df["日付"], errors='coerce', format="%Y-%m-%d")
    
    
    # 年と月を確認し、float型になっていた場合は整数に変換
    max_day = calendar.monthrange(int(year), int(month))[1]

    # 日付がNoneでないかつその月の日付数以内のデータだけを抽出
    result_df = result_df[result_df["日付"].notna() & (result_df["日付"].dt.day <= max_day)]
    return result_df

# pure_dfの取り出し
def extract_ntpsystem_table(file_path):
    data = []
    with pdfplumber.open(file_path) as pdf:
        page = pdf.pages[0]
        tables = page.extract_tables()
        for table in tables[2:]:
            # 必要なデータが含まれている部分（10行目以降）を抽出
            for row in table[2:]:
                    data.append(
                        {
                            "日": row[0],
                            "曜日": row[1],
                            "勤怠": row[2],
                            "始業時刻": row[3],
                            "終業時刻": row[4],
                            "通常休憩": row[5],
                            "深夜休憩": row[6],
                            "勤怠時間計": row[7],
                            "標準時間": row[8],
                            "平日残業": row[9],
                            "平日深夜": row[10],
                            "休日": row[11],
                            "休日深夜": row[12],
                            "法定休日": row[13],
                            "法休深夜": row[14],
                            "備考": row[15]
                        }
                    )
    # データフレームに変換して表示
    return pd.DataFrame(data)

# PDFから名前を取り出す
def extract_name_from_ntpsystem(file_path):
    with pdfplumber.open(file_path) as pdf:
        page = pdf.pages[0]
        tables = page.extract_tables()
        name = tables[0][2][1].replace(" ","")
        return name