import tkinter as tk
from tkinter import filedialog, messagebox

from Higuchi import Higuchi
from Murase import Murase


class MHSystemGUI:
    def __init__(self, master):
        self.master = master
        master.title("MHSystem")
        master.geometry("400x300")
        self.file_path = None

        # メインフレーム
        self.main_frame = tk.Frame(master)
        self.main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # ファイル選択ボタン
        self.select_file_button = tk.Button(self.main_frame, text="PDFファイルを選択", command=self.select_file)
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
        company_code = 1 #ITCROSS

        # 各社　pdf読み込み　→　フォーマット合わせが目的
        Higuchi.read_pdf(company_code, self.file_path)
        # ジョブカンデータ読み込み
        # 二次元配列→クラスへ
        # 最終サニタイズ　→　時刻を丸める（８;５１　→　９：００）
        # 比較　完全一致比較
        # ファイル名作成　（出向先_氏名_yyyyMMdd.csv）
        # クラス→二次元配列
        # 出力
        
        # ポップアップ出力（おわったよ。差異無いよ。三日分違うよ（9/10,9/11,9/12））
        difference_days = ["9/10", "9/11", "9/12"]
        messagebox.showinfo(Murase.output_message(difference_days))


if __name__ == "__main__":
    root = tk.Tk()
    app = MHSystemGUI(root)
    root.mainloop()
