import pdfplumber
import pandas as pd
import re
import calendar
from app.business import util
# ジョブカンPDFファイルの読み込み関数
def read_jobkan_file(file_path):
    # 名前の取得
    full_name = extract_name_from_jobkan(file_path)
    print(full_name)
    #何も編集がされていないテーブル
    pure_df = extract_jobkan_table(file_path)
    # テーブルを第一フォーマットの形に変更
    firstFormat_df = change_firstFormat_jobkan(pure_df,file_path)
     # カラム名を変更
    englishFormat_df = firstFormat_df.rename(columns={
        "日付": "day", "実働時間": "worktime", "開始時間": "starttime",
        "終了時間": "endtime", "休憩時間": "resttime", "備考": "note"
        })
    # データフレームを辞書のリスト形式に変換
    dict_list = englishFormat_df.to_dict(orient='records')
    # work_data(名前と勤怠データを合わせたフォーマットにして返す
    work_data = util.format_to_work_data(full_name, dict_list)
    return work_data
    
def change_firstFormat_jobkan(pure_df,file_path):
    result_df = pure_df[["日付", "出勤時刻", "退勤時刻", "実労働時間", "休憩時間"]]
    # 空のカラムを追加（フォーマットを合わせるため）
    # result_df.loc[:, "備考"] = None
    result_df = result_df.assign(備考=None)
    # カラム名を変更
    result_df = result_df.rename(
        columns={"実労働時間": "実働時間","出勤時刻": "開始時間", "退勤時刻": "終了時間"}
    )
    # カラムの順番を調整
    result_df = result_df[["日付", "実働時間", "開始時間", "終了時間", "休憩時間", "備考"]]
    # PDF内から20xxの年を抽出
    year = util.extract_year_from_pdf(file_path)
    
    # 日付を20xx-05-01形式に変換
    result_df["日付"] = result_df["日付"].apply(lambda x: util.convert_to_full_date_p2(year, x))
    # その月の日付数以内のデータのみをフィルタリング
    # 下記の処理は他と重複するため共通化する余地あり
    if not result_df["日付"].isnull().all():
        # 月と年を取得
        first_valid_date = result_df["日付"].dropna().iloc[0]
        month = int(first_valid_date.split("-")[1])
        day_count = calendar.monthrange(int(year), month)[1]
        
        # 日付が None ではなく、その月の最大日数以内のデータをフィルタリング
        result_df = result_df.dropna(subset=["日付"])
        result_df = result_df[result_df["日付"].apply(lambda x: int(x.split("-")[2]) <= day_count)]
    return result_df

# pure_dfの取り出し
def extract_jobkan_table(file_path):
    data = []
    with pdfplumber.open(file_path) as pdf:
        page = pdf.pages[0]
        tables = page.extract_tables()
        for table in tables[1:]:
            # 必要なデータが含まれている部分（10行目以降）を抽出
            for row in table[1:]:
                if len(row) >= 14:
                    data.append(
                        {
                            "日付": row[0],
                            "勤怠状況": row[1],
                            "休日区分": row[2],
                            "打刻場所": row[3],
                            "出勤時刻": row[4],
                            "退勤時刻": row[5],
                            "実労働時間": row[6],
                            "実残業時間": row[7],
                            "実深夜時間": row[8],
                            "実残業時間": row[9],
                            "休日労働時間": row[10],
                            "休憩時間": row[11],
                            "有休時間": row[12],
                            "遅刻早退時間": row[13]
                        }
                    )
    # データフレームに変換して表示
    return pd.DataFrame(data)

# PDFから名前を取り出す
def extract_name_from_jobkan(file_path):
    with pdfplumber.open(file_path) as pdf:
        page = pdf.pages[0]
        tables = page.extract_tables()
        full_name = tables[0][2][0]
        # 改行で分割して下の名前部分を取得、空白を削除
        return full_name.replace(" ", "").replace("　","")