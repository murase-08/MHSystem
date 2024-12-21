import pdfplumber
import re
import pandas as pd
import calendar
from app.business import util

def read_trancomTIS_file(file_path):
    # 名前の取得
    full_name = extract_name_from_trancomTIS(file_path)
    #何も編集がされていないテーブル
    pure_df = extract_trancomTIS_table(file_path)
    # テーブルを第一フォーマットの形に変更
    firstFormat_df = change_firstFormat_trancomTIS(pure_df,file_path)
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

def change_firstFormat_trancomTIS(pure_df, file_path):
    result_df = pure_df.assign(休憩時間=None)
    result_df = result_df.assign(備考=None)
    # カラムの順番を調整
    result_df = result_df[["日付", "実働時間", "開始時間", "終了時間", "休憩時間", "備考"]]
    # PDFから動的に西暦と月を抽出して、日付を "20xx-MM-01" 形式に変更する
    year, month = util.extract_year_and_month_from_pdf(file_path)
    result_df["日付"] = result_df["日付"].apply(lambda x: util.convert_to_full_date_p1(year, month, x))
    # 日付カラムを datetime 型に変換し、無効な日付を除外
    result_df["日付"] = pd.to_datetime(result_df["日付"], errors='coerce', format="%Y-%m-%d")
    # 年と月を確認し、float型になっていた場合は整数に変換
    max_day = calendar.monthrange(int(year), int(month))[1]
    # 日付がNoneでないかつその月の日付数以内のデータだけを抽出
    result_df = result_df[result_df["日付"].notna() & (result_df["日付"].dt.day <= max_day)]
    # 各列に適用して無効な値を NaN に置き換える
    for col in ["実働時間", "開始時間", "終了時間"]:
        result_df[col] = result_df[col].apply(util.replace_invalid_with_nan)
    # 実働時間列にフォーマット関数を適用
    result_df["実働時間"] = result_df["実働時間"].apply(util.format_worktimeB)
    result_df["開始時間"] = result_df["開始時間"].apply(util.format_worktimeB)
    result_df["終了時間"] = result_df["終了時間"].apply(util.format_worktimeB)
    
    return result_df

# pure_dfの取り出し
def extract_trancomTIS_table(file_path):
    with pdfplumber.open(file_path) as pdf:
            page = pdf.pages[0]
            tables = page.extract_tables()
            data = []  # 新しいリストを保存するためのリスト
            for row in tables[0]:
                data.append(
                    {
                        "日付": row[0],
                        "開始時間": row[3],
                        "終了時間": row[4],
                        "実働時間": row[6],
                    }
                )
    # データフレームに変換して表示
    return pd.DataFrame(data)

#トランコムTISファイルから名前を取得   
def extract_name_from_trancomTIS(output_pdf_path):
    # 再生成したPDFをpdfplumberで読み込む
    with pdfplumber.open(output_pdf_path) as pdf:
        for page in pdf.pages:
            texts = page.extract_text()
            if texts:
                # 氏名と契約の間にある名前を動的に取得
                # 改行や空白を含んでもマッチするよう修正
                match = re.search(r'氏\s*名\s*+([\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]+.*?)\s*\ 契約', texts, re.DOTALL)
                if match:
                    name = match.group(1).strip()  # 取得した名前の前後の空白を削除
                    name = name.replace(" ", "")  # 半角スペースを削除
                    return name
            else:
                print("テーブルが見つかりませんでした。")