import pdfplumber
import pandas as pd
from datetime import datetime, timedelta
import re
from Higuchi import Higuchi
# TOTEC読み込み関数
def read_totec_file(file_path):
    # 名前の取得
    full_name = extract_name_from_totec(file_path)
    print("ファイルの対象ユーザーは"+full_name+"です。")
    #何も編集がされていないテーブル
    pure_df = extract_totec_table(file_path)
    # テーブルを第一フォーマットの形に変更
    firstFormat_df = change_firstFormat_totec(pure_df)
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

# テーブルを第一フォーマットの形に変更
def change_firstFormat_totec(pure_df):
    # カラム名を変更
    pure_df = pure_df.rename(columns={"備考": "実働時間","開始": "開始時間", "終了": "終了時間"})
    # 実働時間の列から改行以降の文字を削除して、数値部分だけを取得する処理
    # レコードの備考を実働時間として抽出してます。時間以外にも文字列が同時にカラムに混じってるので取り出す際に危険がある
    pure_df["実働時間"] = pure_df["実働時間"].apply(lambda x: x.split('\n')[0] if isinstance(x, str) else x)
    # 時間外普通と時間外深夜を "HH:MM" 形式に変換
    pure_df['実働時間'] = pure_df['実働時間'].apply(Higuchi.convert_hours_to_time)
    # 日付を "2024/05/01" → "2024-05-01" 形式に変更
    pure_df['日付'] = pure_df['日付'].apply(Higuchi.convert_date_format)
    
    # 空のカラムを追加（フォーマットを合わせるため）
    pure_df.loc[:, "休憩時間"] = None
    pure_df.loc[:, "備考"] = None
    # カラムの順番を調整
    pure_df = pure_df[["日付", "実働時間", "開始時間", "終了時間", "時間外普通", "時間外深夜","休憩時間","備考"]]
    # 必要なカラムだけ抽出
    result_df = pure_df[["日付", "実働時間", "開始時間", "終了時間", "休憩時間", "備考"]]
    return result_df
    
# pure_dfの取り出し
def extract_totec_table(file_path):
    data = []
    with pdfplumber.open(file_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            if page_num == 1:  # 1ページ目は extract_tables を使用
                tables = page.extract_tables()
                for table in tables:
                    for row in table[2:]:
                        data.append(
                            {
                                "日付": row[0],
                                "開始": row[3],
                                "終了": row[4],
                                "時間外普通": row[5],
                                "時間外深夜": row[6],
                                "備考": row[9]
                            }
                        )
            else:  # 2ページ目以降は extract_text を使用して解析
                text = page.extract_text()
                # 正規表現：時間外部分と備考欄に数値のみをキャプチャする
                pattern = r"(\d{4}/\d{2}/\d{2})\s+\S+\s+\S+\s+(\d{2}:\d{2})\s+(\d{2}:\d{2})\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)"
                # マッチを取得
                matches = re.findall(pattern, text)
                for match in matches:
                    data.append({
                        "日付": match[0],
                        "開始": match[1],
                        "終了": match[2],
                        "時間外普通": match[3],
                        "時間外深夜": match[4],
                        # ここに備考欄も追加　(備考と言っているが実働時間)
                        # テストPDFは日曜残業の欄がすべて空白になっているのでmatch[5]でいいですが、
                        # 日曜残業に少しでもデータが混じったらアウトです。
                        "備考": match[5]
                    })
    pdf_df = pd.DataFrame(data)
    return pdf_df
    
# PDFから名前を取り出す
def extract_name_from_totec(file_path):
    with pdfplumber.open(file_path) as pdf:
        page = pdf.pages[0]
        text = page.extract_text()
        # print(text)
        # 正規表現で「名前：」の後に続く名前部分を抽出
        match = re.search(r"名前：([^\s]+ [^\s]+)", text)
        full_name = match.group(1).replace(" ", "").replace("　", "") # 空白を削除して連結
        return full_name