import datetime
import json

# 処理完了メッセージ
def Output_Message(difference_days):
    if not difference_days:  # 空のリストを判定
            output_message = f"差異0件"
    else:
            output_message = f"差異{len(difference_days)}件\n{difference_days}"
    return output_message

# 時間を15分単位で切り捨てる
def Sanitize_Time(time_str):
    # 時刻を丸める（8:51　→　9:00）
    hour = int(time_str.split(':')[0])
    minute = int(time_str.split(':')[1])
    #15分単位で丸める
    if minute >= 45:
        minute = 45
    elif minute >= 30:
        minute = 30
    elif minute >= 15:
        minute = 15
    elif minute >= 0:
        minute = 0
    return f"{hour}:{minute}"

def Check_Company(companyName):
    return Call_Campany_CD(companyName)

# 会社コードを取得
def Call_Campany_CD(company_name):
    with open('Config.json', 'r') as config_file:
        config = json.load(config_file)
    company_codes = config['company_code']
    return company_codes[company_name]

# 会社名を取得
def Call_Company_Name(company_code):
    with open('Config.json', 'r') as config_file:
        config = json.load(config_file)
    company_codes = config['company_code']
    for name, code in company_codes.items():
        if code == company_code:
            return name
    return None  # Return None if the company name is not found

# ジョブカンファイルのパスを取得
def Call_Jobkan_Path():
    with open('Config.json', 'r') as config_file:
        config = json.load(config_file)
    jobkan_file_path = config['jobkan_file_path']
    return jobkan_file_path

# ファイル名を作成
def Create_File_Name(name,companyCode):
    # 出向先_氏名_yyyyMMdd.pdf
    company_name = Call_Company_Name(companyCode)
    current_date = datetime.datetime.now().strftime("%Y%m%d")
    return f"{company_name}_{name}_{current_date}.csv"
