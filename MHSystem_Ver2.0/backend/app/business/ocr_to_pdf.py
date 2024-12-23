import pdfplumber
from pdf2image import convert_from_path
import cv2
import os
from google.cloud import vision
from fpdf import FPDF
import numpy as np
from app.utils.config_loader import load_settings

# 設定をロード
settings = load_settings()
# 環境変数を直接指定
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings["vision_path"]

# スキャナーPDFをplumberが使えるPDFに再生成
def ocr_to_pdf(customer_file_path,specific_customer_file_path):
    # 再生成したPDFをpdfplumberで読み込む
    with pdfplumber.open(specific_customer_file_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            if not tables:
                print(specific_customer_file_path + "をOCR処理します")
                # PDFを画像に変換
                processed_images = convert_pdf_to_images(specific_customer_file_path)
                # OCR解析で文字と座標を取得
                text_data = ocr_with_google_vision(processed_images)
                # OCR結果を元に新たなPDFを作成
                create_pdf_with_table_structure_and_grid(text_data[1:], processed_images,customer_file_path, specific_customer_file_path)

# PDFを画像に変換し、OCR精度向上のための前処理を行う関数。
def convert_pdf_to_images(pdf_path):
    # PDFを画像に変換
    dpi=600
    pages = convert_from_path(pdf_path, dpi=dpi)
    processed_images = []
    for page_num, page in enumerate(pages):
        # PDF画像をOpenCV形式の画像に変換
        open_cv_image = np.array(page)
        bgr_image = open_cv_image[:, :, ::-1]
        
        # === OCR精度向上の前処理 ===
        # 1. グレースケール変換
        gray = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)

        # 2. ノイズ除去
        # h=30: フィルタ強度（大きいほどノイズを除去）。
        # templateWindowSize=7: ノイズを評価するテンプレートサイズ。
        # searchWindowSize=21: 周囲の探索ウィンドウサイズ。
        denoised = cv2.fastNlMeansDenoising(gray, h=30, templateWindowSize=7, searchWindowSize=21)
        
        # 3. コントラスト調整（CLAHE）（こいつのおかげで１日とか２日の配置が崩れなくなる）
        # clipLimit=2.0: コントラストの限界値（高いほど明るい領域が強調される）
        # tileGridSize=(8, 8): グリッドサイズ。
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        # 0:しきい値。0を指定すると、cv2.THRESH_OTSUが自動的に適切なしきい値を計算します。
        # 255:最大値。しきい値を超えるピクセルの値を255（白）に設定します。
        # cv2.THRESH_BINARY: 二値化モード（0か255に分ける）。
        # cv2.THRESH_OTSU: 大津の方法（Otsu's method）を使って、最適なしきい値を自動的に計算します。
        # _:計算されたしきい値が格納されます（このコードでは使用されていません）。
        # binary:二値化された画像。元の画像に基づいて、各ピクセルが0（黒）または255（白）のいずれかに変換された画像です。
        # 4. しきい値処理（二値化）
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # 前処理後の画像と元画像を保存
        processed_images.append((binary, bgr_image))
    return processed_images

# OCR解析
# オブジェクトと座標とページを取得
def ocr_with_google_vision(processed_images):
    client = vision.ImageAnnotatorClient()
    full_text_data = []
    for page_num, (processed_image, original_image) in enumerate(processed_images):
        _, encoded_image = cv2.imencode('.png', processed_image)
        content = encoded_image.tobytes()
        image = vision.Image(content=content)
        response = client.text_detection(image=image)
        
        # テキストが認識されている場合にのみ処理を進める。
        if response.text_annotations:
            for annotation in response.text_annotations:
                # テキストを囲む 四角形の座標（頂点）
                vertices = annotation.bounding_poly.vertices
                # 頂点が四つの場合
                if len(vertices) == 4:
                    # text = annotation.description.replace("\n", "").replace("☐", "[ ]").replace("|", "").replace("''", "")
                    text = annotation.description.replace("\n", "").replace("|", "").replace("''", "")
                    x_min = min(v.x for v in vertices)
                    y_min = min(v.y for v in vertices)
                    x_max = max(v.x for v in vertices)
                    y_max = max(v.y for v in vertices)
                    full_text_data.append({
                        "text": text,
                        "coords": (x_min, y_min, x_max, y_max),
                        "page": page_num + 1,
                    })
    return full_text_data

# テーブル構造を推定する関数
def reconstruct_table_from_ocr(text_data, y_tolerance, x_tolerance):
    # text_data = [
    # {"coords": (10, 20, 50, 40), "text": "A"},  # y_min = 20
    # {"coords": (60, 22, 100, 42), "text": "B"},  # y_min = 22
    # {"coords": (10, 100, 50, 120), "text": "C"},  # y_min = 100
    # ]
    
    # 1. Y座標でソートして初期データ構造を作成
    sorted_data = sorted(text_data, key=lambda item: item["coords"][1])  # y_minでソート
    rows = []
    current_row = []
    current_y = None
    for item in sorted_data:
        x_min, y_min, x_max, y_max = item["coords"]
        # 現在の行と近ければ同じ行に追加
        if current_y is None or abs(y_min - current_y) <= y_tolerance:
            current_row.append(item)
            current_y = y_min  # 行基準のy座標を更新
        else:
            # 新しい行を開始
            rows.append(current_row)
            current_row = [item]
            current_y = y_min
    if current_row:  # 最後の行を追加
        rows.append(current_row)
    # 2. X座標でソート(列データを整理)
    table_data = []
    for row in rows:
        sorted_row = sorted(row, key=lambda item: item["coords"][0])  # x_minでソート
        table_data.append([cell["text"] for cell in sorted_row])
    # 3. フィルタリング処理
    filtered_table_data = []  # 新しいリストを作成
    for inner_array in table_data:
        if inner_array:  # 空の配列 [] を除外
            cleaned_array = [item for item in inner_array if item not in ['', None]]  # 空文字列 '', ':' を削除
            if cleaned_array:  # クリーンアップ後に空になった配列も除外
                filtered_table_data.append(cleaned_array)
    return filtered_table_data

# OCR結果を元の画像上に描画してPDFを再生成（テーブル構造に基づく）
def create_pdf_with_table_structure_and_grid(text_data, processed_images,customer_file_path, specific_customer_file_path):
    y_tolerance=50
    x_tolerance=25
    # 出力ディレクトリを指定
    output_dir = customer_file_path

    # 元ファイル名から新しいファイル名を生成
    base_name = os.path.basename(specific_customer_file_path)
    file_name, file_extension = os.path.splitext(base_name)
    new_file_name = f"{file_name}_ocr_processed{file_extension}"
    output_pdf_path = os.path.join(output_dir, new_file_name)

    # PDFの初期設定
    pdf = FPDF(unit="pt", format=[processed_images[0][1].shape[1], processed_images[0][1].shape[0]])
    font_path = settings["font_path"]
    pdf.add_font("NotoSans", "", font_path)
    # pdf.set_font("NotoSans", size=12)
    pdf.set_font("NotoSans", size=15)
    for page_num, (_, original_image) in enumerate(processed_images):
        pdf.add_page()
        # 現在のページのデータをフィルタリング
        page_text_data = [item for item in text_data if item["page"] == page_num + 1]
        # テーブル構造を推定
        table_data = reconstruct_table_from_ocr(page_text_data, y_tolerance, x_tolerance)
        # テーブルをPDFに描画
        for row_index, row in enumerate(table_data):
            # 最初の行を50pt下に表示
            # 各行の高さを20ポイント
            y_pos = row_index * 20 + 50  # 行の位置を調整
            for col_index, cell_text in enumerate(row):
                # 最初の列を50ポイント右に配置
                # 各列の幅を100ポイント
                x_pos = col_index * 100 + 50  # 列の位置を調整
                pdf.set_xy(x_pos, y_pos)
                # w=100: セルの幅を100ポイントに設定。
                # h=20: セルの高さを20ポイントに設定。
                pdf.cell(w=100, h=20, txt=cell_text, border=1)  # セル枠付きで描画
                
    # 新しいPDFを出力
    pdf.output(output_pdf_path)
    print(f" {output_pdf_path}というPDFが生成されました")
    