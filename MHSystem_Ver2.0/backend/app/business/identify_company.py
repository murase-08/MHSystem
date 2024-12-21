import pdfplumber
import re

# 会社CD判別
def return_company_code(file_path):
    with pdfplumber.open(file_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables()
            texts = page.extract_text()
            # システムシェアード
            if texts and re.search(r'株式会社システムシェアード', texts):
                print("これはシステムシェアードです")
                return 1
            # テクノクリエイティブ
            elif texts and re.search(r'㈱テクノクリエイティブ', texts):
                print("これはテクノクリエイティブです")
                return 2
            # TDIシステムサービス
            elif texts and re.search(r'TDIシステムサービス株式会社', texts):
                print("これはTDIシステムサービス株式会社です")
                return 3
            # トーテック
            elif texts and re.search(r'公共ｼｽﾃﾑ事業部 第1ｼｽﾃﾑ部 第7ｸﾞﾙｰﾌﾟ', texts):
                print("これはトーテックです")
                return 4
            # システムサポート
            elif texts and re.search(r'株式会社システムサポート', texts):
                print("これはシステムサポートです")
                return 5
            # CEC
            elif tables[0][0] == ['', '①作業開始時刻', '②作業終了時刻', '③休憩時間', '④作業時間\n②-①-③', '⑤超過/控除']:
                print("これはCECです")
                return 6
            # トランコムTIS
            elif tables[0][4] == ['日', '曜', '日', '勤', '怠', '時刻', '始業', '時刻', '終業', '通常', '休憩', 
                                  '深夜', '勤務', '時間', '計', '標準', '時間', '残業', '平日', '深夜', '平日', 
                                  '休', '日', '休日', '深夜', '休日', '法定', '深夜', '法', '休', '備考']:
                print("これはトランコムTISです")
                return 7
            else:
                print("このファイルが何のファイルかわかりません")
                return -1