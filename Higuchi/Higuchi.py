from Higuchi.ReturnFormat import Jobkan,SystemShared,TecnoCreative,TdiSystemSurvice,Totec,SystemSupport,Cec

#会社コード(CD)に応じたFormat関数を呼び出します
def read_file(file_path,companyCode):
    # ジョブカン
    if companyCode == 0:
        return Jobkan.read_jobkan_file(file_path)
    # システムシェアード
    elif companyCode == 1:
        return SystemShared.read_systemshared_file(file_path)
    # テクノクリエイティブ
    elif companyCode == 2:
        return TecnoCreative.read_tecnocreative_file(file_path)
    # TDIシステムサービス
    elif companyCode == 3:
        return TdiSystemSurvice.read_tdisystem_file(file_path)
    # トーテック
    elif companyCode == 4:
        return Totec.read_totec_file(file_path)
    # システムサポート
    elif companyCode == 5:
        return SystemSupport.read_systemsupport_file(file_path)
    # CEC
    elif companyCode == 6:
        return Cec.read_cec_file(file_path)
    else:
        print("存在しない会社です。")
        
# work_data(名前と勤怠データを合わせたフォーマットにして返す
def format_to_work_data(full_name, dict_list):
    # work_dataフォーマットに変換
    work_data = {
        "name": full_name,
        "work_days": dict_list
    }
    return work_data