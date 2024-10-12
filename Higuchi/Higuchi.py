import pdfplumber
import pandas as pd

# 株式会社システムシェアードのPDF読み込み関数
def read_systemshared_pdf(pdf_path):
    data = []
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        tables = page.extract_tables()
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
    pdf_df = pd.DataFrame(data)
    print(pdf_df)

# TDIシステムサービス株式会社のPDF読み込み関数
def read_tdisystem_pdf(pdf_path):
    data = []
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        tables = page.extract_tables()
        for table in tables:
            for row in table[1:]:
                if len(row) >= 4:
                    data.append(
                        {
                            "日付": row[0],
                            "曜日": row[1],
                            "出勤日": row[2],
                            "実働時間": row[3],
                            "業務内容": row[4],
                        }
                    )
    pdf_df = pd.DataFrame(data)
    print(pdf_df)

# 株式会社システムサポートのPDF読み込み関数
# 未完成
def read_systemsupport_pdf(pdf_path):
    data = []
    with pdfplumber.open(pdf_path) as pdf:
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
                            "終了": row[3],
                            "休憩": row[4],
                            "作業時間": row[5],
                            "作業内容": row[6],
                        }
                    )
    pdf_df = pd.DataFrame(data)
    print(pdf_df)

# 株式会社アイティークロスのPDF読み込み関数
def read_itcross_pdf(pdf_path):
    data = []
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        tables = page.extract_tables()
        for table in tables:
            for row in table[3:]:
                if len(row) >= 15:
                    data.append(
                        {
                            "日": row[0],
                            "曜日": row[1],
                            "勤怠": row[2],
                            "始業時刻": row[3],
                            "終業時刻": row[4],
                            "休憩": row[5],
                            "勤務時間計": row[6],
                            "標準時間": row[7],
                            "平均残業": row[8],
                            "平日深夜": row[9],
                            "休日": row[10],
                            "休日深夜": row[11],
                            "法定休日": row[12],
                            "法定深夜": row[13],
                            "備考": row[14],
                        }
                    )
    pdf_df = pd.DataFrame(data)
    print(pdf_df)

# ㈱テクノクリエイティブのPDF読み込み関数
def read_tecnocreative_pdf(pdf_path):
    data = []
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        tables = page.extract_tables()
        for table in tables:
            for row in table[1:]:
                data.append(
                    {
                        "日付": row[0],
                        "開始": row[1],
                        "終了": row[2],
                        "提示": row[3],
                        "残業": row[4],
                    }
                )
    pdf_df = pd.DataFrame(data)
    print(pdf_df)

# 公共ｼｽﾃﾑ事業部 第1ｼｽﾃﾑ部 第7ｸﾞﾙｰﾌﾟのPDF読み込み関数
def read_kokyosystem_pdf(pdf_path):
    data = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table[1:]:
                    data.append(
                        {
                            "日付": row[0],
                            "開始": row[1],
                            "終了": row[2],
                            "普通": row[3],
                            "深夜": row[4],
                        }
                    )
    pdf_df = pd.DataFrame(data)
    print(pdf_df)

# 松井の会社のPDF読み込み関数
# 未完成(取得する列が先頭の日付から出力されない)
def read_matuicompany_pdf(pdf_path):
    data = []
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        tables = page.extract_tables()
        for table in tables:
            for row in table[7:]:
                if len(row) >= 3:
                    data.append(
                        {
                            "日付": row[0],
                            "➀作業開始時刻": row[1],
                            "➁作業終了時刻": row[2],
                            "➂休憩時間": row[3],
                            "➃作業時間➁-➀-➂": row[4],
                            "◯超過時間": row[5]
                        }
                    )
    pdf_df = pd.DataFrame(data)
    print(pdf_df)

# 赤井の会社のPDF読み込み関数
# 未完成(1つのセルに複数の日付や値が含まれているため、意図した形で表データが抽出されていない)
def read_akaicompany_pdf(pdf_path):
    data = []
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]  
        tables = page.extract_tables() 
        for table in tables:
            for row in table[1:]: 
                # 空行や無効な行をスキップ
                if len(row) >1:
                    data.append(
                        {
                            "年休": row[0] ,
                            "欠勤": row[1] ,
                            "日付": row[2],
                            "曜日": row[3],
                            "始業": row[4] ,
                            "終業": row[5] ,
                            "休憩": row[6] ,
                            "時間": row[7] ,
                            "備考": row[8] 
                        }
                    )
    pdf_df = pd.DataFrame(data)
    print(pdf_df)

# 各会社の勤怠情報を読み込み、リストとして出力する関数
def read_pdf(company_code, pdf_path):
    if company_code == 1:
        read_systemshared_pdf(pdf_path)
    elif company_code == 2:
        read_tdisystem_pdf(pdf_path)
    elif company_code == 3:
        read_systemsupport_pdf(pdf_path)
    elif company_code == 4:
        read_itcross_pdf(pdf_path)
    elif company_code == 5:
        read_tecnocreative_pdf(pdf_path)
    elif company_code == 6:
        read_kokyosystem_pdf(pdf_path)
    elif company_code == 7:
        read_matuicompany_pdf(pdf_path)
    elif company_code == 8:
        read_akaicompany_pdf(pdf_path)
    else:
        print("未対応の会社コードです。")
