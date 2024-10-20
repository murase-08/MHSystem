import json
import tkinter as tk
from tkinter import filedialog, messagebox
from Murase import Murase
from Higuchi import Higuchi

class MHSystemGUI:
    def __init__(self, master):
        self.master = master
        master.title("MHSystem")
        master.geometry("400x300")
        self.file_path = None

        # メインフレーム
        self.main_frame = tk.Frame(master)
        self.main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Config.jsonから会社名を読み込む
        with open('Config.json', 'r') as config_file:
            config = json.load(config_file)
        companies = list(config['company_code'].keys())

        # 会社名選択用のドロップダウン
        self.company_frame = tk.LabelFrame(self.main_frame, text="会社名選択", font=("MS Gothic", 10))
        self.company_frame.pack(pady=10, fill=tk.X)
        self.company_var = tk.StringVar(value=companies[0])
        self.company_dropdown = tk.OptionMenu(self.company_frame, self.company_var, *companies)
        self.company_dropdown.pack(fill=tk.X)

        # 各社ファイル選択ボタン
        self.select_file_button = tk.Button(self.main_frame, text="各社PDFファイルを選択", command=self.select_file)
        self.select_file_button.pack(pady=10, anchor='e')

        # 実行ボタン
        self.run_button = tk.Button(self.main_frame, text="実行", command=self.run_process)
        self.run_button.pack(pady=10, anchor='e')
        # 結果表示エリア
        self.result_text = tk.Text(self.main_frame, height=10, width=50)
        self.result_text.pack(pady=10)

    # ファイル選択ボタンの処理
    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf"), ("Excel files", "*.xlsx;*.xls")])
        if file_path:
            self.file_path = file_path
            self.result_text.insert(tk.END, f"選択されたファイル: {file_path}\n")

    # 実行ボタンの処理
    def run_process(self):
        if(self.file_path == None):
            messagebox.showerror("エラー", "ファイルが選択されていません")
            return
        
        # ドロップボックスの会社名を取得
        companyName = self.company_var.get()

        # 会社判別
        companyCode = Murase.Check_Company(companyName)
        print('会社CD：'+str(companyCode))
        # 各社pdf読み込み　→　フォーマット合わせが目的
        # 戻り値 pandasデータフレーム
        #   社員名 姓
        #   社員名 名　NULL OK
        #   日付 datetime.date(yyyy,MM,dd) => yyyy-MM-dd
        #   実働時間 HH:mm
        #       （warning 樋口 HH:mm　のほうがいいと思います）=> 村瀬 OK,休憩時間も準じます
        #   開始時間 HH:mm　NULL OK
        #   終了時間 HH:mm　NULL OK
        #   休憩時間 HH:mm　NULL OK
        #   備考 string　NULL OK
        cosutomerData = Higuchi.read_file(companyCode, self.file_path)
        
        # ジョブカンファイルパスを取得
        jobkan_file_path = Murase.Call_Jobkan_Path() + cosutomerData.employee_name + ".pdf"
        # ジョブカンデータ読み込み(会社CD:4 ITCROSS)
        jobkanData = Higuchi.read_file(Murase.Call_Campany_CD("ITCROSS"), jobkan_file_path)
                        
        # 比較　完全一致比較 日ごとの実働時間で比較
        
        # ファイル名作成　（出向先_氏名_yyyyMMdd.csv）
        file_name = Murase.Create_File_Name(cosutomerData.employee_name, company_code)
        
        # 出力
        Murase.output_csv()
        # ポップアップ出力（おわったよ。差異無いよ。三日分違うよ（9/10,9/11,9/12））
        difference_days = ["9/10", "9/11", "9/12"]
        messagebox.showinfo(Murase.output_message(difference_days))


if __name__ == "__main__":
    root = tk.Tk()
    app = MHSystemGUI(root)
    root.mainloop()
