import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
from google_vision_ocr import google_vision_ocr1
from google_vision_ocr import google_vision_ocr2
from google_vision_ocr import google_vision_ocr3
from google_vision_ocr import google_vision_ocr4
from google_vision_ocr import google_vision_ocr5
from ocr_extract import ocr_extract1
from ocr_extract import ocr_extract2
from ocr_extract import ocr_extract3
from ocr_extract import ocr_extract4
from ocr_extract import ocr_extract5
import Compare
from Company_identifier import process_pdf_for_company_name

#GUIクラス
class OCR_GUI:
    def __init__(self, master):
        self.master = master
        master.title("OCR System")
        master.geometry("800x500")
        self.file_paths = [None, None]
        self.company_number = None
        # メインフレーム
        self.main_frame = tk.Frame(master)
        self.main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # ファイル1（ジョブカン）ドラッグアンドドロップエリア
        self.drop_area_frame = tk.Frame(self.main_frame)
        self.drop_area_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.drop_area1 = tk.LabelFrame(self.drop_area_frame, text="ファイル1（ジョブカン）をドラッグ＆ドロップ", width=200, height=150, relief=tk.RIDGE)
        self.drop_area1.pack_propagate(False)
        self.drop_area1.pack(side=tk.LEFT, padx=10, pady=10)
        self.drop_area1.drop_target_register(DND_FILES)
        self.drop_area1.dnd_bind('<<Drop>>', lambda event: self.on_drop(event, 0))
        self.drop_area1_label = tk.Label(self.drop_area1, text="ここにファイルをドロップ", wraplength=180, justify='left')
        self.drop_area1_label.pack()

        # ファイル2（客先）ドラッグアンドドロップエリア
        self.drop_area2 = tk.LabelFrame(self.drop_area_frame, text="ファイル2（客先）をドラッグ＆ドロップ", width=200, height=150, relief=tk.RIDGE)
        self.drop_area2.pack_propagate(False)
        self.drop_area2.pack(side=tk.RIGHT, padx=10, pady=10)
        self.drop_area2.drop_target_register(DND_FILES)
        self.drop_area2.dnd_bind('<<Drop>>', lambda event: self.on_drop(event, 1))
        self.drop_area2_label = tk.Label(self.drop_area2, text="ここにファイルをドロップ", wraplength=180, justify='left')
        self.drop_area2_label.pack()

        # 実行ボタン
        self.run_button = tk.Button(
            self.main_frame, text="OCR実行", command=self.run_ocr_process)
        self.run_button.pack(pady=10, anchor='e')

        # 結果表示エリア
        self.result_text = tk.Text(self.main_frame, height=10, width=70)
        self.result_text.pack(pady=10)

    # ドラッグアンドドロップの処理
    def on_drop(self, event, file_index):
        file_path = event.data.strip('{}')
        if file_path:
            self.file_paths[file_index] = file_path
            if file_index == 0:
                self.drop_area1_label.config(text=file_path, wraplength=180)
                self.result_text.insert(tk.END, f"ファイル1がドロップされました: {file_path}\n")
            else:
                self.drop_area2_label.config(text=file_path, wraplength=180)
                self.result_text.insert(tk.END, f"ファイル2がドロップされました: {file_path}\n")
                # ドロップされたファイルから会社名をOCRで判別
                company_name2 = process_pdf_for_company_name(file_path)
                self.result_text.insert(tk.END, f"ファイル2は {company_name2} の勤怠表です\n")
                self.company_number = self.assign_company_number(company_name2)

    # 実行ボタンが押されたときの処理
    def run_ocr_process(self):
        # ファイル1（ジョブカン）のOCR処理
        try:
            self.result_text.insert(tk.END, f"ファイル1に対してOCR前処理を実行中...\n")
            #PDFを画像に変換する関数を呼び出す
            ocr_extract1.process_pdf_for_table(self.file_paths[0])
            # 前処理済み画像に対してOCR処理を実行し、テキストを抽出
            result1 = google_vision_ocr1.detect_and_pair_date_time_text('C:/Users/user/debug_images/page_1_threshold.png')
            # 処理完了のメッセージを表示
            self.result_text.insert(tk.END, "ファイル1のOCR処理が完了しました。\n")
        except Exception as e:
            # エラー発生時のメッセージを表示
            self.result_text.insert(tk.END, f"ファイル1のOCR処理でエラーが発生しました: {e}\n")
            return
        
        # ファイル2（客先）のOCR処理（会社番号に応じた処理）
        if self.company_number is None:
            # 会社番号が設定されていない場合のエラーメッセージ
            self.result_text.insert(tk.END, "ファイル2が選択されていません。\n")
            return

        try:
            if self.company_number == 1:
                self.result_text.insert(tk.END, f"ファイル2に対してジョブカン用OCR処理を実行中...\n")
                # ファイル2をジョブカン向けに処理
                ocr_extract1.process_pdf_for_table(self.file_paths[1])
                # result2 = google_vision_ocr1.detect_and_pair_date_time_text('/Users/yuri23/ocr_project/debug_images/page1_1_threshold.png')
                # result2 = google_vision_ocr1.detect_and_pair_date_time_text('C:/Users/user/debug_images/page_1_threshold.png')

            elif self.company_number == 2:
                self.result_text.insert(tk.END, f"ファイル2に対してTDIシステム用OCR処理を実行中...\n")
                # ファイル2をTDIシステム向けに処理
                ocr_extract2.process_pdf_for_table(self.file_paths[1])
                result2 = google_vision_ocr2.detect_and_pair_date_time_text('C:/Users/user/debug_images/page2_1_threshold.png')

            elif self.company_number == 3:
                self.result_text.insert(tk.END, f"ファイル2に対してシステムシェアード用OCR処理を実行中...\n")
                # ファイル2をシステムシェアード向けに処理
                ocr_extract3.process_pdf_for_table(self.file_paths[1])
                result2 = google_vision_ocr3.detect_and_pair_date_time_text('C:/Users/user/debug_images/page3_1_threshold.png')

            elif self.company_number == 4:
                self.result_text.insert(tk.END, f"ファイル2に対してシステムサポート用OCR処理を実行中...\n")
                # ファイル2をシステムサポート向けに処理
                ocr_extract4.process_pdf_for_table(self.file_paths[1])
                result2 = google_vision_ocr4.detect_and_pair_date_time_text('C:/Users/user/debug_images/page4_1_threshold.png')

            elif self.company_number == 5:
                self.result_text.insert(tk.END, f"ファイル2に対してテクノクリエイティブ用OCR処理を実行中...\n")
                # ファイル2をテクノクリエイティブ向けに処理
                ocr_extract5.process_pdf_for_table(self.file_paths[1])
                result2 = google_vision_ocr5.detect_and_pair_date_time_text('C:/Users/user/debug_images/page5_1_threshold.png')
            else:
                # 会社番号が不明な場合のエラーメッセージ
                self.result_text.insert(tk.END, "ファイル2の会社名が不明です。\n")
                return
            self.result_text.insert(tk.END, "ファイル2のOCR処理が完了しました。\n")
            # ２つのファイルのOCR結果の比較処理
            try:
                self.result_text.insert(tk.END, "OCR結果の比較を実行中...\n")
                # ペアリストの長さが異なる場合、エラーを発生
                total_pairs = len(result1)
                if total_pairs != len(result2):
                    print("ペアリストの長さが異なります。")
                    raise ValueError("ペアリストの長さが異なります。処理を中止します。")
                
                print("以下は樋口のデバッグ用の出力です。")
                print("result1を表示します")
                print(result1);
                print("result2を表示します")
                print(result2);
                
                # 比較処理を実行し、差異を検出
                differences = Compare.compare_paired_texts(result1, result2)
                if differences:
                    # 差異がある場合、詳細を表示
                    self.result_text.insert(tk.END, f"違いが見つかりました: {len(differences)} 件\n")
                    for diff in differences:
                        _, p1, p2 = diff
                        self.result_text.insert(tk.END, f"{p1[0]}日： {p1[1]} != {p2[1]}\n")
                else:
                    # 差異がない場合
                    self.result_text.insert(tk.END, "ファイル1とファイル2の結果は一致しています。\n")

            except ValueError as ve:
                self.result_text.insert(tk.END, f"エラー: {ve}\n")
        
            except Exception as e:
                # 比較処理中に発生したエラーのメッセージ
                self.result_text.insert(tk.END, f"OCR結果の比較中にエラーが発生しました: {e}\n")
        except Exception as e:
            # ファイル2のOCR処理中に発生したエラーのメッセージ
            self.result_text.insert(tk.END, f"ファイル2のOCR処理でエラーが発生しました: {e}\n")

    # 会社名に対応する番号を割り振る関数
    def assign_company_number(self, company_name):
        if company_name == "ジョブカン":
            return 1
        elif company_name == "TDIシステム":
            return 2
        elif company_name == "システムシェアード":
            return 3
        elif company_name == "システムサポート":
            return 4
        elif company_name == "テクノクリエイティブ":
            return 5
        return 0

#メイン処理
if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = OCR_GUI(root)
    root.mainloop()