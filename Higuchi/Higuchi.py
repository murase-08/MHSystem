import pdfplumber
import pandas as pd
from datetime import datetime, timedelta
# 各会社の勤怠情報を読み込み、リストとして出力する関数
def read_file(company_code, file_path):
    if company_code == 1:
        read_systemshared_file(file_path)
    elif company_code == 2:
        read_tdisystem_file(file_path)
    elif company_code == 3:
        read_systemsupport_file(file_path)
    elif company_code == 4:
        read_itcross_file(file_path)
    elif company_code == 5:
        read_tecnocreative_file(file_path)
    elif company_code == 6:
        read_kokyosystem_file(file_path)
    elif company_code == 7:
        read_matuicompany_file(file_path)
    elif company_code == 8:
        read_akaicompany_file(file_path)
    else:
        print("未対応の会社コードです。")
# 株式会社システムシェアードのPDF読み込み関数
def read_systemshared_file(file_path):
    data = []
    with pdfplumber.open(file_path) as pdf:
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
    result_df = pdf_df[['日付', '労働時間', '開始', '終了', '休憩時間', 'メモ']]
    # カラム名を変更
    result_df = result_df.rename(columns={
        '開始': '開始時間',
        '終了': '終了時間',
        'メモ': '備考'
    })
    print(result_df)

# TDIシステムサービス株式会社のPDF読み込み関数
def read_tdisystem_file(file_path):
    data = []
    with pdfplumber.open(file_path) as pdf:
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
    result_df = pdf_df[['日付', '実働時間','業務内容']]
    # 空のカラムを追加（フォーマットを合わせるため）
    result_df['開始時間'] = None
    result_df['終了時間'] = None
    result_df['休憩時間'] = None

    # カラムの順番を調整
    result_df = result_df[['日付','実働時間', '開始時間', '終了時間', '休憩時間', '業務内容']]
    # カラム名を変更
    result_df = result_df.rename(columns={
        '業務内容': '備考'
    })
    print(result_df)

# 株式会社システムサポートのPDF読み込み関数
def read_systemsupport_file(file_path):
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
    result_df = pdf_df[['日', '作業時間','開始','終了','休憩',"作業内容"]]
    # カラム名を変更
    result_df = result_df.rename(columns={
        '日': '日付',
        '作業時間': '実働時間',
        '開始': '開始時間',
        '終了': '終了時間',
        '休憩': '休憩時間',
        '作業内容': '備考',
    })
    print(result_df)

# 株式会社アイティークロスのPDF読み込み関数
#未完成(完成していたが動かなくなった　原因不明)
def read_itcross_file(file_path):
    data = []
    with pdfplumber.open(file_path) as pdf:
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
def read_tecnocreative_file(file_path):
    data = []
    with pdfplumber.open(file_path) as pdf:
        page = pdf.pages[0]
        tables = page.extract_tables()
        for table in tables:
            for row in table[2:]:
                 data.append(
                    {
                        "日付": row[0],
                        "開始": row[3],
                        "終了": row[4],
                        "休憩": row[5],
                        "定時": row[8],
                        "残業": row[9],
                        "深夜": row[10],
                        "休出": row[11],
                        "届出": row[12],
                        "備考": row[13],
                    }
                )
    pdf_df = pd.DataFrame(data)
    print(pdf_df)

# 公共ｼｽﾃﾑ事業部 第1ｼｽﾃﾑ部 第7ｸﾞﾙｰﾌﾟのPDF読み込み関数
def read_kokyosystem_file(file_path):
    data = []
    with pdfplumber.open(file_path) as pdf:
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

# 松井の会社のExcel読み込み関数
# 勤怠情報をExcelから読み込み、必要なカラムを抽出する関数
def read_matuicompany_file(file_path):
    df = pd.read_excel(file_path, sheet_name="作業時間報告", engine='openpyxl', header=5)
    # 必要なカラムを抽出
    attendance_data = df[['Unnamed: 1', '①作業開始時刻', '②作業終了時刻', '③休憩時間', '④作業時間\n②-①-③', '⑤超過/控除']]
    attendance_data = attendance_data.rename(columns={'Unnamed: 1': '日付'})
    
    # 日付列のデータを数値型に変換。数値に変換できないデータは NaN として扱う
    attendance_data['日付'] = pd.to_numeric(attendance_data['日付'], errors='coerce')
    # 45413形式のシリアル値を日付形式に変換
    base_date = datetime(1899, 12, 30)  # Excelの日付シリアルの基準日
    attendance_data['日付'] = attendance_data['日付'].apply(lambda x: base_date + timedelta(days=x) if pd.notnull(x) else None)
    
   # 開始時刻・終了時刻・休憩時間のフォーマットを変更（'09:00:00' → '09:00'）
    time_columns = ['①作業開始時刻', '②作業終了時刻', '③休憩時間', '④作業時間\n②-①-③']
    for col in time_columns:
        attendance_data[col] = attendance_data[col].apply(lambda x: f"{int(x.total_seconds() // 3600):02}:{int((x.total_seconds() % 3600) // 60):02}" if isinstance(x, pd.Timedelta) else x)
    # データを表示
    print(attendance_data)
    
# 赤井の会社のExcel読み込み関数
def read_akaicompany_file(file_path):
    current_month = int(datetime.now().strftime("%m"))
    if current_month == 1:
        check_month = 12
    else:
        check_month = current_month - 1
    # 月のフォーマットをゼロ埋めする（例: 01月, 02月）
    sheet_name = f"{check_month:02}月"
    
    # Excelファイルを読み込み、必要なヘッダー行を指定
    df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl', header=4)
    
    print("Excelファイルの列名:", df.columns)
    # 必要なカラムを抽出
    attendance_data = df[['日付', '始業', '終業', '休憩', '時間', '備考']]
    # データを表示
    print(attendance_data)