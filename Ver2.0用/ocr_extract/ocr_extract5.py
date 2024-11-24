import io
from google.cloud import vision
from pdf2image import convert_from_path
import cv2
import numpy as np
import os

# Google Cloud Vision APIクライアントの作成
client = vision.ImageAnnotatorClient()

# 出力ディレクトリの作成
output_dir = "debug_images"
os.makedirs(output_dir, exist_ok=True)

# 始点となる5月1日のY座標を取得する関数
def detect_text_using_vision_api(image_path):
    """Google Cloud Vision APIを使って画像からテキストを抽出する"""
    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()
    
    image = vision.Image(content=content)
    
    # テキスト抽出
    response = client.text_detection(image=image)
    texts = response.text_annotations
    
    y_coordinates = None 

    if texts:
        for text in texts:
            vertices = [(vertex.x, vertex.y) for vertex in text.bounding_poly.vertices]
            if text.description == "1":  # '1' を特定
                # 最初の頂点のy座標を取得
                y_coordinates = vertices[0][1]
                print(f"05/01の座標: {y_coordinates}")
                break
    else:
        print("テキストが見つかりませんでした。")

    return y_coordinates

# 画像を保存する関数
def save_debug_image(image, step_name, page_num):
    file_name = f"{output_dir}/page5_{page_num + 1}_{step_name}.png"
    cv2.imwrite(file_name, image)
    print(f"デバッグ: {file_name} に保存されました。")

# OCR精度を向上させるための画像前処理を行う関数
def preprocess_image_for_ocr(image, page_num):
    # グレースケール変換
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    save_debug_image(gray, "grayscale", page_num)

    # ノイズ除去
    denoised = cv2.fastNlMeansDenoising(gray, None, 15, 7, 21)
    save_debug_image(denoised, "denoised", page_num)

    # しきい値処理を手動で設定
    _, thresh = cv2.threshold(denoised, 150, 255, cv2.THRESH_BINARY_INV)
    save_debug_image(thresh, "threshold", page_num)

    return thresh 

# OCR精度をさらに向上させるための追加処理を行う関数
def enhance_image_for_ocr(image, page_num):
    kernel = np.array([[0, -0.5, 0], [-0.5, 4, -0.5], [0, -0.5, 0]], np.float32) 
    sharpened = cv2.filter2D(image, -1, kernel)
    save_debug_image(sharpened, "sharpened", page_num)

    return sharpened

# 画像を特定の領域でトリミングする関数
def trim_image(image, y_coordinates):
    # トリミングしたい領域の座標を指定 (x, y, width, height)
    x, y, width, height = 140, y_coordinates - 40, 2550, 4550
    trimmed_image = image[y:y + height, x:x + width]
    return trimmed_image

# 特定の領域を黒く塗りつぶす関数
def trim_and_blackout_columns(image):
    # 画像の高さと幅を取得
    height, width = image.shape[:2]
    
    # 黒く塗りつぶしたい領域の座標を指定 (x, y, width, height)
    x_start = 285
    x_end = 2000
    y_start = 0
    y_end = height
    
    # 指定した領域を黒く塗りつぶす
    image[y_start:y_end, x_start:x_end] = 0

    return image

# PDFを画像に変換して処理する関数
def process_pdf_for_table(pdf_path):
    try:
        # DPIを600に設定してPDFを画像に変換
        pages = convert_from_path(pdf_path, 600)
    except Exception as e:
        print(f"PDFのページ数を取得できませんでした: {e}")
        return
    
    if pages:
        page_image = pages[0]  # 1ページ目だけ取得
        page_num = 0

        # PIL画像をOpenCV形式に変換
        open_cv_image = np.array(page_image)
        open_cv_image = open_cv_image[:, :, ::-1].copy()

        # 画像保存
        image_path = f"{output_dir}/page5_{page_num + 1}.png"
        cv2.imwrite(image_path, open_cv_image)
        
        #テキストのY座標を取得
        y_coordinates = detect_text_using_vision_api(image_path)
        
        if y_coordinates is None:
            print("05/01が見つからなかったため、トリミングをスキップします。")
            return

        # トリミング処理
        trimmed_image = trim_image(open_cv_image, y_coordinates)
        save_debug_image(trimmed_image, "trimmed", page_num)

        # 特定の列を黒く塗りつぶす
        blacked_out_image = trim_and_blackout_columns(trimmed_image)
        save_debug_image(blacked_out_image, "blacked_out", page_num)

        # OCR前処理
        processed_image = preprocess_image_for_ocr(trimmed_image, page_num)
        
        # OCR追加処理
        enhanced_image = enhance_image_for_ocr(processed_image, page_num)

# メイン処理
def main():
    # PDFファイルのパス
    pdf_path = '/Users/yuri23/Downloads/テクノクリエイティブ.pdf'
    process_pdf_for_table(pdf_path)

if __name__ == '__main__':
    main()
