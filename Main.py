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
        self.file_name = None
        self.jobkan_file_path = None
        self.employee_name = None

        # メインフレーム
        self.main_frame = tk.Frame(master)
        self.main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Config.jsonから会社名を読み込む
        with open('Config.json', 'r') as config_file:
            config = json.load(config_file)
        companies = list(config['company_name'].values())

        # 会社名選択用のドロップダウン
        self.company_frame = tk.LabelFrame(self.main_frame, text="会社名選択")
        self.company_frame.pack(pady=10, fill=tk.X)

        self.company_var = tk.StringVar(value=companies[0])
        self.company_dropdown = tk.OptionMenu(self.company_frame, self.company_var, *companies)
        self.company_dropdown.pack(fill=tk.X)

        # 社員名入力フィールド
        self.name_frame = tk.Frame(self.main_frame)

        self.name_frame.pack(pady=10, fill=tk.X)
        tk.Label(self.name_frame, text="社員名:").pack(side=tk.LEFT)
        self.name_entry = tk.Entry(self.name_frame)
        self.name_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

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
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            self.file_path = file_path
            self.result_text.insert(tk.END, f"選択されたファイル: {file_path}\n")

    # 実行ボタンの処理
    def run_process(self):
        if(self.file_path == None):
            messagebox.showerror("エラー", "ファイルが選択されていません")
            return
        
        # 会社判別
        company_code = Murase.Check_Company(self.file_name)

        # 各社　pdf読み込み　→　フォーマット合わせが目的
        Higuchi.read_pdf(1, self.file_path)
        

        # ジョブカンファイルを取得
        self.jobkan_file_path = Murase.Call_Jobkan_Path() + self.employee_name + ".pdf"
        # ジョブカンデータ読み込み(会社CD:0)
        Higuchi.read_pdf(Murase.Call_Campany_CD("ITCROSS"), self.jobkan_file_path)
        
        # 二次元配列→クラスへ
        
        # 最終サニタイズ　→　時刻を丸める（８;５１　→　９：００）
        
        # 比較　完全一致比較
        
        # ファイル名作成　（出向先_氏名_yyyyMMdd.csv）
        file_name = Murase.Create_File_Name(self.employee_name, company_code)
        # クラス→二次元配列
        
        # 出力
        Murase.output_csv()
        # ポップアップ出力（おわったよ。差異無いよ。三日分違うよ（9/10,9/11,9/12））
        difference_days = ["9/10", "9/11", "9/12"]
        messagebox.showinfo(Murase.output_message(difference_days))


if __name__ == "__main__":
    root = tk.Tk()
    app = MHSystemGUI(root)
    root.mainloop()
