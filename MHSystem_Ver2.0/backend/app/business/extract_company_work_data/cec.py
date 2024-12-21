import pdfplumber
import pandas as pd
from datetime import datetime, timedelta,time
import re
import calendar
from app.business import util

# Cec読み込み関数
# 勤怠情報をExcelから読み込み、必要なカラムを抽出する関数
def read_cec_file(file_path):
    # 名前の取得
    full_name = extract_name_from_cec(file_path)
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
    dict_list = util.convert_timestamps(dict_list)
    # work_data(名前と勤怠データを合わせたフォーマットにして返す
    work_data = util.format_to_work_data(full_name, dict_list)
    return work_data

def change_firstFormat_cec(result_df,output_pdf_path):
    # カラム名を変更
    result_df = result_df.rename(
        columns={"作業開始時刻": "開始時間","作業終了時刻": "終了時間", "作業時間": "実働時間"}
    )
    # 不要なカラムを削除
    result_df = result_df.drop(columns=["超過/控除", "備考"], errors="ignore")
    result_df.loc[:, "備考"] = None
    # カラムの順序を変更
    result_df = result_df[["日付", "実働時間","開始時間", "終了時間", "休憩時間", "備考"]]
    # 実働時間のフォーマットを「8:00」から「08:00」に変換
    result_df["実働時間"] = result_df["実働時間"].apply(lambda x: x.zfill(5) if pd.notnull(x) and ':' in x else x)
    result_df["開始時間"] = result_df["開始時間"].apply(lambda x: x.zfill(5) if pd.notnull(x) and ':' in x else x)
    result_df["終了時間"] = result_df["終了時間"].apply(lambda x: x.zfill(5) if pd.notnull(x) and ':' in x else x)
    result_df["休憩時間"] = result_df["休憩時間"].apply(lambda x: x.zfill(5) if pd.notnull(x) and ':' in x else x)
    # PDFから動的に西暦と月を抽出して、日付を 5月1日から"2024-05-01" 形式に変更する
    year,month= util.extract_year_and_month_from_pdf(output_pdf_path)
    result_df["日付"] = result_df["日付"].apply(lambda x: util.convert_to_full_date_p3(year, x))
    # 日付カラムを datetime 型に変換し、無効な日付を除外
    result_df["日付"] = pd.to_datetime(result_df["日付"], errors='coerce', format="%Y-%m-%d")
    # 年と月を確認し、float型になっていた場合は整数に変換
    max_day = calendar.monthrange(int(year), int(month))[1]
    # 日付がNoneでないかつその月の日付数以内のデータだけを抽出
    result_df = result_df[result_df["日付"].notna() & (result_df["日付"].dt.day <= max_day)]
    return result_df

def extract_cec_table(output_pdf_path):
    # 再生成したPDFをpdfplumberで読み込む
    data = []
    with pdfplumber.open(output_pdf_path) as pdf:
        page = pdf.pages[0]
        tables = page.extract_tables()
        if tables and len(tables) > 0:
            # 最初のテーブルを取得
            table = tables[0]
            rows = table[1:]   # 2行目以降をデータとする
            for row in rows:
                # 辞書型データに変換
                data.append(
                    {
                        "日付": row[0],
                        "作業開始時刻": row[1],
                        "作業終了時刻": row[2],
                        "休憩時間": row[3],
                        "作業時間": row[4],
                        "超過/控除": row[5]
                    }
                )
    # Pandas DataFrameに変換して表示
    pdf_df = pd.DataFrame(data)
    return pdf_df

#CECファイルから名前を取得   
def extract_name_from_cec(output_pdf_path):
    # 再生成したPDFをpdfplumberで読み込む
    with pdfplumber.open(output_pdf_path) as pdf:
        for page in pdf.pages:
            texts = page.extract_text()
            if texts:
                # 氏名と会社名の間にある名前を動的に取得
                # 改行や空白を含んでもマッチするよう修正
                match = re.search(r'氏名\s+([\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]+.*?)\s*\（', texts, re.DOTALL)
                if match:
                    name = match.group(1).strip()  # 取得した名前の前後の空白を削除
                    name = name.replace(" ", "")  # 半角スペースを削除
                    return name
            else:
                print("テーブルが見つかりませんでした。")
           
        