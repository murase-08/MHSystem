import pdfplumber
import pandas as pd
import os

# 会社CD判別
def return_company_code(file_path):
    # ファイルの拡張子を取得
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension == ".pdf":
        # PDFを開く
        with pdfplumber.open(file_path) as pdf:
            # PDF内のすべてのページを走査
            for page_number, page in enumerate(pdf.pages, start=1):
                # 各ページからテーブルを抽出
                tables = page.extract_tables()

                if tables:
                    # print(f"Page {page_number}:")
                    for table_number, table in enumerate(tables, start=1):
                        # print(f"  Table {table_number}:")
                        for row in table:
                            # print(row)
                            # 1番目のテーブルを取得
                            first_table = tables[0]
                            # 1番目の配列（行）を取得
                            first_row = first_table[0]
                            # first_tableに3行目があるか確認
                            if len(first_table) > 2:
                                third_row = first_table[2]
                            else:
                                third_row = None

                            # 条件を確認
                            if first_row[0] == "スタッフ情報" and first_row[9] == "基本項目":
                                print("これはジョブカンのPDFです")
                                return 0
                            elif first_row[1] == "株式会社システムシェアード":
                                print("これは株式会社システムシェアードのPDFです")
                                return 1
                            elif first_row[1] == "萩原北都テクノ株式会社":
                                print("これはテクノクリエイティブのPDFです")
                                return 2
                            elif (
                                first_row[0] == "日\n付"
                                and first_row[1] == "曜\n日"
                                and first_row[2] == "出\n勤\n日"
                                and first_row[3] == "実働時間"
                                and first_row[4] == "業務内容"
                            ):
                                print("これはTDIシステムサービスのPDFです")
                                return 3
                            elif (
                                first_row[0] == "4月"
                                and first_row[1] == "5月"
                                and first_row[2] == "6月"
                                and first_row[3] == "7月"
                                and first_row[4] == "8月"
                                and first_row[5] == "9月"
                                and first_row[6] == "10月"
                                and first_row[7] == "11月"
                                and first_row[8] == "12月"
                                and first_row[9] == "1月"
                                and first_row[10] == "2月"
                                and first_row[11] == "3月"
                            ):
                                print("これはトーテックのPDFです")
                                return 4
                            elif third_row[0] == "株式会社システムサポート 御中":
                                print("これはシステムサポートのPDFです")
                                return 5
                            else:
                                print("どの会社のPDFでもありません")
    elif file_extension in [".xls", ".xlsx"]:
        # 会社の一番目のシートを選択します。
        df = pd.read_excel(file_path, sheet_name=0, engine="openpyxl")
        # df.iloc[4, 2]は、データフレームの**5行目（インデックス4）の3列目（インデックス2）**の値を取得
        if (
            df.iloc[4, 2] == "①作業開始時刻"
            and df.iloc[4, 3] == "②作業終了時刻"
            and df.iloc[4, 4] == "③休憩時間"
            and df.iloc[4, 6] == "⑤超過/控除"
        ):
            print("これはCECのExcelです")
            return 6