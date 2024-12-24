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
# setting.jsonから定数データを取り出す
FILTER_STRENGTH         = settings["ocr_preprocess"]["FILTER_STRENGTH"]
TEMPLATE_WINDOW_SIZE    = settings["ocr_preprocess"]["TEMPLATE_WINDOW_SIZE"]
SEARCH_WINDOW_SIZE      = settings["ocr_preprocess"]["SEARCH_WINDOW_SIZE"]
CLIP_LIMIT              = settings["ocr_preprocess"]["CLIP_LIMIT"]
TILE_GRID_SIZE_WIDTH    = settings["ocr_preprocess"]["TILE_GRID_SIZE_WIDTH"]
TILE_GRID_SIZE_HEIGHT   = settings["ocr_preprocess"]["TILE_GRID_SIZE_HEIGHT"]
BLACK                   = settings["ocr_preprocess"]["BLACK"]
WHITE                   = settings["ocr_preprocess"]["WHITE"]
Y_TOLERANCE             = settings["create_table_and_grid"]["Y_TOLERANCE"]
X_TOLERANCE             = settings["create_table_and_grid"]["X_TOLERANCE"]
FONT_SIZE               = settings["create_table_and_grid"]["FONT_SIZE"]
ROW_HEIGHT              = settings["create_table_and_grid"]["ROW_HEIGHT"]
TOP_MARGIN              = settings["create_table_and_grid"]["TOP_MARGIN"]
COLUMN_WIDTH            = settings["create_table_and_grid"]["COLUMN_WIDTH"]
LEFT_MARGIN             = settings["create_table_and_grid"]["LEFT_MARGIN"]
CELL_WIDTH              = settings["create_table_and_grid"]["CELL_WIDTH"]
CELL_HEIGHT             = settings["create_table_and_grid"]["CELL_HEIGHT"]
BORDER_LINE             = settings["create_table_and_grid"]["BORDER_LINE"]

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
    DPI=settings["ocr_preprocess"]["DPI"]
    pages = convert_from_path(pdf_path, dpi=DPI)
    processed_images = []
    for page_num, page in enumerate(pages):
        # PDF画像をOpenCV形式の画像に変換
        open_cv_image = np.array(page)
        bgr_image = open_cv_image[:, :, ::-1]
        
        # === OCR精度向上の前処理 ===
        # 1. グレースケール変換
        gray = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)

        # 2. ノイズ除去
        denoised = cv2.fastNlMeansDenoising(gray, h=FILTER_STRENGTH, templateWindowSize=TEMPLATE_WINDOW_SIZE, searchWindowSize=SEARCH_WINDOW_SIZE)
        
        # 3. コントラスト調整（CLAHE）（こいつのおかげで１日とか２日の配置が崩れなくなる）
        clahe = cv2.createCLAHE(clipLimit=CLIP_LIMIT, tileGridSize=(TILE_GRID_SIZE_WIDTH, TILE_GRID_SIZE_HEIGHT))
        enhanced = clahe.apply(denoised)
        
        # 4. しきい値処理（二値化）
        _, binary = cv2.threshold(enhanced, BLACK, WHITE, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

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
            cleaned_array = [item for item in inner_array if item not in ['', None]]  # 空文字列 '' を削除
            if cleaned_array:  # クリーンアップ後に空になった配列も除外
                filtered_table_data.append(cleaned_array)
    return filtered_table_data

# OCR結果を元の画像上に描画してPDFを再生成（テーブル構造に基づく）
def create_pdf_with_table_structure_and_grid(text_data, processed_images,customer_file_path, specific_customer_file_path):
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
    pdf.set_font("NotoSans", size=FONT_SIZE)
    
    for page_num, (_, original_image) in enumerate(processed_images):
        pdf.add_page()
        # 現在のページのデータをフィルタリング
        page_text_data = [item for item in text_data if item["page"] == page_num + 1]
        # テーブル構造を推定
        table_data = reconstruct_table_from_ocr(page_text_data, Y_TOLERANCE, X_TOLERANCE)
        # テーブルをPDFに描画
        for row_index, row in enumerate(table_data):
            y_pos = row_index * ROW_HEIGHT + TOP_MARGIN  # 行の位置を調整
            for col_index, cell_text in enumerate(row):
                x_pos = col_index * COLUMN_WIDTH + LEFT_MARGIN  # 列の位置を調整
                pdf.set_xy(x_pos, y_pos)
                pdf.cell(w=CELL_WIDTH, h=CELL_HEIGHT, txt=cell_text, border=BORDER_LINE)  # セル枠付きで描画
                
    # 新しいPDFを出力
    pdf.output(output_pdf_path)
    print(f" {output_pdf_path}というPDFが生成されました")
    