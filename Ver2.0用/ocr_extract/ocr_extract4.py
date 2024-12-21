import io
from google.cloud import vision
from pdf2image import convert_from_path
import cv2
import numpy as np
import os

# Google Cloud Vision APIクライアントの作成
client = vision.ImageAnnotatorClient()

# 出力ディレクトリの作成（デバッグ用）
output_dir = "debug_images"
os.makedirs(output_dir, exist_ok=True)

# 始点となる5月1日のY座標を取得する関数
def detect_text_using_vision_api(image_path):
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
            if text.description == "曜日":  # '5/1' を特定
                # 最初の頂点のy座標を取得
                y_coordinates = vertices[0][1]
                print("以下はシステムサポートのy_cordinatesの値です。")
                print(f"05/01の座標: {y_coordinates}")
                break 
    else:
        print("テキストが見つかりませんでした。")

    return y_coordinates

# 画像を保存
def save_debug_image(image, step_name, page_num):
    file_name = f"{output_dir}/page4_{page_num + 1}_{step_name}.png"
    cv2.imwrite(file_name, image)
    print(f"デバッグ: {file_name} に保存されました。")

# OCR精度を上げるための前処理
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

# OCR精度を上げるための追加処理
def enhance_image_for_ocr(image, page_num):
    # シャープ化処理
    kernel = np.array([[0, -0.5, 0], [-0.5, 4, -0.5], [0, -0.5, 0]], np.float32) 
    sharpened = cv2.filter2D(image, -1, kernel)
    save_debug_image(sharpened, "sharpened", page_num)

    return sharpened

# 画像をトリミングする関数
def trim_image(image,y_coordinates):
    # トリミングしたい領域の座標を指定 (x, y, width, height)
    x, y, width, height = 140, y_coordinates+105, 2000, 4080 

    trimmed_image = image[y:y + height, x:x + width]
    return trimmed_image

# 特定の領域を黒く塗りつぶす関数
def trim_and_blackout_columns(image):
    # 画像の高さと幅を取得
    height, width = image.shape[:2]
    
    # 黒く塗りつぶしたい領域の座標を指定 (x, y, width, height)
    x_start = 340
    x_end = 1660
    y_start = 0
    y_end = height
    
    # 指定した領域を黒く塗りつぶす
    image[y_start:y_end, x_start:x_end] = 0  # 0は黒 (BGRフォーマットなので全て0)

    return image

# PDFを画像に変換する関数
def process_pdf_for_table(pdf_path):
    try:
        # DPIを600に設定してPDFを画像に変換
        pages = convert_from_path(pdf_path, 600)  # 高解像度で変換
    except Exception as e:
        print(f"PDFのページ数を取得できませんでした: {e}")
        return
    
    if pages:
        page_image = pages[0]  # 1ページ目だけ取得
        page_num = 0  # ページ番号は0で固定

        # PIL画像をOpenCV形式に変換
        open_cv_image = np.array(page_image)
        open_cv_image = open_cv_image[:, :, ::-1].copy()  # RGBからBGRへ

        # 画像保存
        image_path = f"{output_dir}/page4_{page_num + 1}.png"
        cv2.imwrite(image_path, open_cv_image)
        
        #テキストのY座標を取得
        y_coordinates = detect_text_using_vision_api(image_path)
        
        if y_coordinates is None:
            print("05/01が見つからなかったため、トリミングをスキップします。")

        # トリミング処理
        trimmed_image = trim_image(open_cv_image, y_coordinates)
        save_debug_image(trimmed_image, "trimmed", page_num)  # トリミングされた画像を保存

        # 特定の列を黒く塗りつぶす
        blacked_out_image = trim_and_blackout_columns(trimmed_image)
        save_debug_image(blacked_out_image, "blacked_out", page_num)  # 黒く塗りつぶした画像を保存

        # OCR前処理
        processed_image = preprocess_image_for_ocr(trimmed_image, page_num)
        
        # OCR追加処理
        enhanced_image = enhance_image_for_ocr(processed_image, page_num)

# メイン処理
def main():
    # PDFファイルのパス
    pdf_path = 'C:/Users/user/Desktop/work_data/木佐貫大地_システムサポート.pdf'
    process_pdf_for_table(pdf_path)

if __name__ == '__main__':
    main()
