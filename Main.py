import json
import tkinter as tk
from tkinter import filedialog, messagebox
from Murase import Murase
from Higuchi import DistinctCompany, Higuchi
from Hayakawa import Hayakawa
import os
import re
import pandas as pd

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

        # # 会社名選択用のドロップダウン
        # self.company_frame = tk.LabelFrame(self.main_frame, text="会社名選択", font=("MS Gothic", 10))
        # self.company_frame.pack(pady=10, fill=tk.X)
        self.company_var = tk.StringVar(value=companies[0])
        # self.company_dropdown = tk.OptionMenu(self.company_frame, self.company_var, *companies)
        # self.company_dropdown.pack(fill=tk.X)

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
        
        # 会社判別
        companyCode = DistinctCompany.return_company_code(self.file_path)
        
        print('会社CD：',companyCode)
        # # 各社pdf読み込み　→　フォーマット合わせが目的
        companyFormatList =Higuchi.read_file(self.file_path,companyCode)
        print(companyFormatList)
        
        # 下のファイルパスはパソコンに依存します
        directory_path = "C:\\Users\\user\\Desktop\\work_data\\jobkan_file\\"
        # 佐々木麻緒
        name_to_search = companyFormatList['name']
        # 正規表現パターンを作成
        pattern = re.compile(rf"{name_to_search}.*\.pdf")
        # 指定された名前を含むファイルを検索
        matching_files = []
        for filename in os.listdir(directory_path):
            if pattern.search(filename):
                matching_files.append(filename)
        # 結果の表示
        if matching_files:
            print("該当するファイル:")
            for file in matching_files:
                print(file)
        # 正規表現パターンを作成
        pattern = re.compile(rf"{name_to_search}.*\.pdf")
        # ジョブカンファイルパスを取得
        jobkan_file_path = Murase.Call_Jobkan_Path() + file
        # ジョブカンファイル読み込み
        jobkanFormatList =Higuchi.read_file(jobkan_file_path,0)
        print(jobkanFormatList)
        
        conpany_workdays = companyFormatList['work_days']
        jobkan_workdays = jobkanFormatList['work_days']
        # データフレームに変換
        # (warning 辞書リストにしたのにわざわざデータフレームに変換している)
        company_data = pd.DataFrame(conpany_workdays)
        company_data = company_data.fillna("")
        jobkan_data = pd.DataFrame(jobkan_workdays)
        print(company_data)
        print(jobkan_data)
        # 比較　完全一致比較 日ごとの実働時間で比較
        difference_days = Hayakawa.compare_working_hours(company_data, jobkan_data)
        print("差異のある日付を出力")
        print(difference_days)
        
        # ファイル名作成　（出向先_氏名_yyyyMMdd.csv）
        file_name = Murase.Create_File_Name(companyFormatList['name'], companyCode)
        
        # 出力
        Murase.output_csv()
        # ポップアップ出力（おわったよ。差異無いよ。三日分違うよ（9/10,9/11,9/12））
        messagebox.showinfo(Murase.output_message(difference_days))


if __name__ == "__main__":
    # Tkinterのメインウィンドウを作成
    root = tk.Tk()
    app = MHSystemGUI(root)
    # GUIアプリケーションが終了するまで継続し、ボタンのクリックなどのイベントを待機
    root.mainloop()
