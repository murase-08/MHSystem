import os
from flask import Blueprint, jsonify, request
from app.utils.config_loader import load_settings
from app.business.extract_company_work_data import jobkan
from app.business.extract_company_work_data import systemshared
from app.business.extract_company_work_data import tecnocreative
from app.business.extract_company_work_data import tdisystemsurvice
from app.business.extract_company_work_data import totec
from app.business.extract_company_work_data import systemsupport
from app.business.extract_company_work_data import cec
from app.business.extract_company_work_data import trancomtis
from app.business.extract_company_work_data import ntpsystem
from app.business import excel_to_pdf
from app.business import ocr_to_pdf
from app.business import identify_company
from app.business import compare_work_data
from app.business import create_message
from app.business import util
from app.data_access import dbconnect

# 設定をロード
settings = load_settings()

def detect_difference():
    # ルート勤怠ファイルパス（固定パス）
    root_path = settings["root_path"]
    try:
        data = request.get_json()
        year_month = data.get('yearMonth', '')
        print(f"デバッグ用：リクエストされた年月: {year_month}")
        
        # ファイルパスを適切に結合
        customer_file_path = os.path.join(root_path, year_month, "customer_file")
        jobkan_file_path = os.path.join(root_path, year_month, "jobkan_file")
        
        #顧客ファイル内の全てのファイルを取得
        customer_files = [f for f in os.listdir(customer_file_path) if f.endswith(('.pdf', '.xlsx', '.xls'))]
        print("customer_files" + str(customer_files))
        
        # Excel形式のものをPDFに変換して保存
        for customer_file in customer_files:
            if customer_file.endswith(('.xlsx', '.xls')):  # Excelファイルのみ対象
                input_path = os.path.join(customer_file_path, customer_file)
                output_path = os.path.splitext(input_path)[0] + '.pdf'  # 拡張子を '.pdf' に変更
                excel_to_pdf.create_pdf_from_excel(input_path, output_path)
                
        # PDFのみにフィルタリング
        customer_files = [f for f in os.listdir(customer_file_path) if f.endswith(('.pdf'))]
        
        # PDFファイルからスキャンPDFをフィルタリングして新しいPDFを再生成(plumberをつかえるようにするため)
        for customer_file in customer_files:
            specific_customer_file_path = os.path.join(root_path, year_month,"customer_file",customer_file)
            ocr_to_pdf.ocr_to_pdf(customer_file_path,specific_customer_file_path)
        
        # plumberで使えるPDFだけを取得する。
        plumber_can_read_pdf_files_path = []
        for customer_file in customer_files:
            specific_customer_file_path = os.path.join(root_path, year_month,"customer_file",customer_file)
            plumber_can_read_pdf_file = util.get_plumber_can_read_files(specific_customer_file_path)
            plumber_can_read_pdf_files_path.append(plumber_can_read_pdf_file)
            plumber_can_read_pdf_files_path = [x for x in plumber_can_read_pdf_files_path if x is not None]
        print("以下のファイルををplumberで勤怠抽出します"+str(plumber_can_read_pdf_files_path))
        
        # 各会社ごとの処理を辞書にまとめる
        company_functions = {
            1: systemshared.read_systemshared_file,
            2: tecnocreative.read_tecnocreative_file,
            3: tdisystemsurvice.read_tdisystem_file,
            4: totec.read_totec_file,
            5: systemsupport.read_systemsupport_file,
            6: cec.read_cec_file,
            7: trancomtis.read_trancomTIS_file,
            8: ntpsystem.read_ntpsystem_file
        }
        # gapDataの配列を格納するためのgapList定義する
        gapList = []
        # 顧客勤怠とジョブカン勤怠を比べて差異があるものだけ保存
        for plumber_can_read_pdf_file_path in plumber_can_read_pdf_files_path:
            company_code = identify_company.return_company_code(plumber_can_read_pdf_file_path)
            print(company_code)
            process_function = company_functions.get(company_code)

            if process_function:
                # デバッグ用データ
                # customer_work_data = {'name': '佐々木麻緒', 'work_days': [{'day': '2024-05-01', 'worktime': '08:15', 'starttime': '08:45', 'endtime': '18:00', 'resttime': '01:00', 'note': ''}]}
                # jobkan_work_data = {'name': '佐々木麻緒', 'work_days': [{'day': '2024-05-01', 'worktime': '08:15', 'starttime': '08:45', 'endtime': '18:00', 'resttime': '01:00', 'note': None}, {'day': '2024-05-02', 'worktime': '08:15', 'starttime': '08:45', 'endtime': '18:00', 'resttime': '01:00', 'note': None}]}
                
                customer_work_data = process_function(plumber_can_read_pdf_file_path)
                specific_jobkan_file_path = util.find_file_with_name(jobkan_file_path, customer_work_data['name'])
                jobkan_work_data = jobkan.read_jobkan_file(specific_jobkan_file_path)
                
                
                gap_days = compare_work_data.compare_work_time(customer_work_data['work_days'], jobkan_work_data['work_days'])
                customer_file_name = os.path.basename(plumber_can_read_pdf_file_path)
                gapData = {'name': customer_work_data['name'], 'customer_file_name': customer_file_name, 'gap_days': gap_days}
                print("plumber_can_read_pdf_file_path"+plumber_can_read_pdf_file_path)
                print("specific_jobkan_file_path"+specific_jobkan_file_path)
                print(gapData)
                # 勤怠日に差異がある場合は gapList に追加
                if gapData['gap_days']:
                    gapList.append(gapData)
                    false_days_str = ",".join(map(str, gapData['gap_days']))
                    # false_dataテーブルにデータを保存
                    dbconnect.add_false_data_table(year_month,
                                             customer_work_data['name'],
                                             company_code,
                                             customer_file_name,
                                             false_days_str)
        # 勤怠差異情報を文字列にして返す
        return create_message.generate_difference_report(gapList)
        
    except Exception as e:
        print(f"エラー: {e}")
        return jsonify({
            "status": "error",
            "message": "エラーが発生しました"
        }), 500