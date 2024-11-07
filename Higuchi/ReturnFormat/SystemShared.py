import pdfplumber
import pandas as pd
from datetime import datetime, timedelta
import re
from Higuchi import Higuchi

# 株式会社システムシェアードのPDF読み込み関数
def read_systemshared_file(file_path):
    # 名前の取得
    full_name = extract_name_from_systemshared(file_path)
    print("ファイルの対象ユーザーは"+full_name+"です。")
    #何も編集がされていないテーブル
    pure_df = extract_systemshared_table(file_path)
    # テーブルを第一フォーマットの形に変更
    firstFormat_df = change_firstFormat_systemshared(pure_df,file_path)
    # カラム名を変更
    englishFormat_df = firstFormat_df.rename(columns={
        "日付": "day", "実働時間": "worktime", "開始時間": "starttime", 
        "終了時間": "endtime", "休憩時間": "resttime", "備考": "note"
        })
    # データフレームを辞書のリスト形式に変換
    dict_list = englishFormat_df.to_dict(orient='records')
    # work_data(名前と勤怠データを合わせたフォーマットにして返す
    work_data = Higuchi.format_to_work_data(full_name, dict_list)
    return work_data
    
def change_firstFormat_systemshared(pure_df,file_path):
    #必要なカラムだけ抽出
    result_df = pure_df[["日付", "労働時間", "開始", "終了", "休憩時間", "メモ"]]
    # カラム名を変更
    result_df = result_df.rename(
        columns={"労働時間": "実働時間","開始": "開始時間", "終了": "終了時間", "メモ": "備考"}
    )
    # PDF内から20xxの年を抽出
    year = Higuchi.extract_year_from_pdf(file_path)
    # 日付を20xx-05-01形式に変換
    result_df["日付"] = result_df["日付"].apply(lambda x: Higuchi.convert_to_full_date_p2(year, x))
    return result_df

#取得対象のテーブルを取得する関数
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

# PDFから名前を取り出す
def extract_name_from_systemshared(file_path):
    with pdfplumber.open(file_path) as pdf:
        page = pdf.pages[0]
        tables = page.extract_tables()
        # "Teacher-RecoRu0082 佐々木麻緒"
        full_name = tables[0][3][1]
        # 最後の要素を取得
        name = full_name.split()[-1].replace(" ", "")
    return name