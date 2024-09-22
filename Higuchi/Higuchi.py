import pdfplumber
import pandas as pd

# 各社会社PDF読み込み関数
# 各会社の勤怠情報を読み込み、リストとして出力します
def read_pdf(company_code, pdf_path):
    
    # 株式会社システムシェアードのPDF読み込み関数
    if company_code == 1:
        def read_systemshared_pdf(pdf_path):
            data = []
            with pdfplumber.open(pdf_path) as pdf:
                page = pdf.pages[0]
                tables = page.extract_tables()
                for table in tables:
                    for row in table[1:]:
                        data.append({
                            "日付": row[0],
                            "開始": row[1],
                            "終了": row[2],
                            "休憩時間": row[3],
                            "労働時間": row[4],
                            "時間外": row[5]
                        })
            pdf_df = pd.DataFrame(data)
            print(pdf_df)
        # 株式会社システムシェアードのPDF読み込み関数を実行
        read_systemshared_pdf(pdf_path)

    # TDIシステムサービス株式会社のPDF読み込み関数
    elif company_code == 2:
        def read_tdisystem_pdf(pdf_path):
            data = []
            with pdfplumber.open(pdf_path) as pdf:
                page = pdf.pages[0]
                tables = page.extract_tables()
                for table in tables:
                    for row in table[1:]:
                        data.append({
                            "日付": row[0],
                            "実働時間": row[1]
                        })
            pdf_df = pd.DataFrame(data)
            print(pdf_df)
        # TDIシステムサービス株式会社のPDF読み込み関数を実行
        read_tdisystem_pdf(pdf_path)

    # 株式会社システムサポートのPDF読み込み関数
    elif company_code == 3:
        def read_systemsupport_pdf(pdf_path):
            data = []
            with pdfplumber.open(pdf_path) as pdf:
                page = pdf.pages[0]
                tables = page.extract_tables()
                for table in tables:
                    for row in table[1:]:
                        data.append({
                            "日": row[0],
                            "開始": row[1],
                            "終了": row[2],
                            "休憩": row[3],
                            "作業時間": row[4]
                        })
            pdf_df = pd.DataFrame(data)
            print(pdf_df)
        # 株式会社システムサポートのPDF読み込み関数を実行
        read_systemsupport_pdf(pdf_path)

    # 株式会社アイティークロスのPDF読み込み関数
    elif company_code == 4:
        def read_itcross_pdf(pdf_path):
            data = []
            with pdfplumber.open(pdf_path) as pdf:
                page = pdf.pages[0]
                tables = page.extract_tables()
                for table in tables:
                    for row in table[1:]:
                        data.append({
                            "日": row[0],
                            "始業時間": row[1],
                            "休憩": row[2],
                            "勤務時間計": row[3],
                            "平日残業": row[4]
                        })
            pdf_df = pd.DataFrame(data)
            print(pdf_df)
        # 株式会社アイティークロスのPDF読み込み関数を実行
        read_itcross_pdf(pdf_path)

    # ㈱テクノクリエイティブのPDF読み込み関数
    elif company_code == 5:
        def read_tecnocreative_pdf1(pdf_path):
            data = []
            with pdfplumber.open(pdf_path) as pdf:
                page = pdf.pages[0]
                tables = page.extract_tables()
                for table in tables:
                    for row in table[1:]:
                        data.append({
                            "日付": row[0],
                            "開始": row[1],
                            "終了": row[2],
                            "提示": row[3],
                            "残業": row[4]
                        })
            pdf_df = pd.DataFrame(data)
            print(pdf_df)
        # ㈱テクノクリエイティブのPDF読み込み関数を実行
        read_tecnocreative_pdf1(pdf_path)

    # 公共ｼｽﾃﾑ事業部 第1ｼｽﾃﾑ部 第7ｸﾞﾙｰﾌﾟのPDF読み込み関数
    elif company_code == 6:
        def read_kokyosystem_pdf(pdf_path):
            data = []
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    for table in tables:
                        for row in table[1:]:
                            data.append({
                                "日付": row[0],
                                "開始": row[1],
                                "終了": row[2],
                                "普通": row[3],
                                "深夜": row[4]
                            })
            pdf_df = pd.DataFrame(data)
            print(pdf_df)
        # 公共ｼｽﾃﾑ事業部 第1ｼｽﾃﾑ部 第7ｸﾞﾙｰﾌﾟのPDF読み込み関数を実行
        read_kokyosystem_pdf(pdf_path)