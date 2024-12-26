import pythoncom
import win32com.client as win32

# ExcelをPDFに変換する関数
def create_pdf_from_excel(input_path, output_path):
    
    try:
        # # 意図的に例外を発生させる
        # raise Exception("テスト用に意図的なエラーを投げます。")
    
        # COMライブラリの初期化
        pythoncom.CoInitialize()
        
        # Excelアプリケーションを起動
        excel = win32.Dispatch("Excel.Application")
        excel.Visible = False
        
        # 指定したExcelファイルを開く
        wb = excel.Workbooks.Open(input_path)
        
        # PDFとして保存
        wb.ExportAsFixedFormat(0, output_path)
        
        wb.Close(False)  # ファイルを閉じる
        excel.Quit()     # Excelアプリケーションを終了
        print(output_path+"をPDF化しました")
        
    except Exception as e:
        print(f"ExcelからPDFが生成できませんでした。 {e}")
        
    finally:
        # COMライブラリの終了
        pythoncom.CoUninitialize()