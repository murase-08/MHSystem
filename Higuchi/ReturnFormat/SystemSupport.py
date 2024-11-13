import pdfplumber
import pandas as pd
import calendar
from Higuchi import Higuchi
# 株式会社システムサポートのPDF読み込み関数
def read_systemsupport_file(file_path):
    # 名前の取得
    full_name = extract_name_from_systemsupport(file_path)
    print("ファイルの対象ユーザーは"+full_name+"です。")
    #何も編集がされていないテーブル
    pure_df = extract_systemsupport_table(file_path)
    # テーブルを第一フォーマットの形に変更
    firstFormat_df = change_firstFormat_systemsupport(pure_df,file_path)
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

def change_firstFormat_systemsupport(pure_df,file_path):
    # 必要なカラムだけ抽出
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
    # 実働時間のフォーマットを「8:00」から「08:00」に変換
    result_df["実働時間"] = result_df["実働時間"].apply(lambda x: x.zfill(5) if pd.notnull(x) and ':' in x else x)
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

# pure_dfの取り出し
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

# PDFから名前を取り出す
def extract_name_from_systemsupport(file_path):
    with pdfplumber.open(file_path) as pdf:
        page = pdf.pages[0]
        tables = page.extract_tables()
        name = tables[0][6][12]
        # 改行で分割して下の名前部分を取得、空白を削除
        full_name = name.replace(" ", "")
        return full_name