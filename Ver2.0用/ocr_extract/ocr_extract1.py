import io
from google.cloud import vision
from pdf2image import convert_from_path
import cv2
import numpy as np
import os

# 環境変数を直接指定
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\user\Downloads\mhsystem-9787827c319a.json"

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
            if text.description == "05/01":
                y_coordinates = vertices[0][1]
                print("以下はジョブカンのy_cordinatesの値です。")
                print(f"05/01の座標: {y_coordinates}")
                break
    else:
        print("テキストが見つかりませんでした。")
    return y_coordinates

# 画像を保存
def save_debug_image(image, step_name, page_num):
    file_name = f"{output_dir}/page_{page_num + 1}_{step_name}.png"
    cv2.imwrite(file_name, image)
    print(f"デバッグ: {file_name} に保存されました。")

# OCR精度を上げるための前処理
def preprocess_image_for_ocr(image, page_num):
    # グレースケール変換
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    save_debug_image(gray, "grayscale", page_num)

     # ノイズ除去
    denoised = cv2.fastNlMeansDenoising(gray, None, 30, 7, 21)
    save_debug_image(denoised, "denoised", page_num)

     # しきい値処理で文字のコントラストを高める（背景は白、文字は黒）
    _, thresh = cv2.threshold(denoised, 128, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    save_debug_image(thresh, "threshold", page_num)

    return thresh

# OCR精度を上げるための追加処理
def enhance_image_for_ocr(image, page_num):
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], np.float32)
    sharpened = cv2.filter2D(image, -1, kernel)
    save_debug_image(sharpened, "sharpened", page_num)

    return sharpened

#画像をトリミングする関数
def trim_image(image,y_coordinates):
    # トリミングする領域の座標を指定 (x, y, width, height)
    # x: トリミングする領域の左上角の x 座標。300
    # y: トリミングする領域の左上角の y 座標。
    # width: トリミングする領域の幅。
    # height: トリミングする領域の高さ。
    x, y, width, height = 300, y_coordinates-20, 6650, 2900

    trimmed_image = image[y:y + height, x:x + width]
    return trimmed_image

#特定の領域を黒く塗りつぶす関数
def trim_and_blackout_columns(image):
    # image.shape は画像の形状（高さ、幅、色チャンネル数）を返します。
    # [:2] を使用することで、高さと幅だけを取得します（色チャンネルは無視します）。
    height, width = image.shape[:2]
    
    # 黒く塗りつぶしたい領域の座標を指定 (x, y, width, height)
    x_start1 = 350
    x_end1 = 3050
    y_start1 = 0
    y_end1 = height
    
    image[y_start1:y_end1, x_start1:x_end1] = 0  # 0は黒 (BGRフォーマットなので全て0)

    x_start2 = 3370
    x_end2 = 8000
    y_start2 = 0
    y_end2 = height
    
    image[y_start2:y_end2, x_start2:x_end2] = 0
    return image

#PDFを画像に変換する関数
# PDFを画像に変換→画像の形式を変換→トリミング→黒く塗りつぶす→グレースケール変換→ノイズ除去→コントラスト高める→保存
def process_pdf_for_table(pdf_path):
    try:
        # PDFをページごとに画像に変換 (DPIを600に設定して高解像度で生成)
        pages = convert_from_path(pdf_path, 600)
    except Exception as e:
        # 例外処理: PDFのページ数を取得できなかった場合のエラーメッセージ
        print(f"PDFのページ数を取得できませんでした: {e}")
        return
    # page_numは現在のページ番号 page_imageは現在のページ画像
    # ページごとに処理を行う
    for page_num, page_image in enumerate(pages):
        # PIL画像をOpenCV形式（NumPy配列）に変換
        open_cv_image = np.array(page_image)
        # OpenCVはBGR色空間を使用するため、RGBからBGRに変換
        open_cv_image = open_cv_image[:, :, ::-1].copy()
        # 処理した画像を保存 (デバッグ用)
        image_path = f"{output_dir}/page_{page_num + 1}.png"
        cv2.imwrite(image_path, open_cv_image)
        
        # Google Vision APIを使って特定のテキストのY座標を取得
        y_coordinates = detect_text_using_vision_api(image_path)
        
        if y_coordinates is None:
            # 必要なテキストが見つからない場合、トリミングをスキップ
            print("05/01が見つからなかったため、トリミングをスキップします。")
            continue

        # 必要な範囲をトリミング
        trimmed_image = trim_image(open_cv_image, y_coordinates)
        # トリミング後の画像を保存 (デバッグ用)
        save_debug_image(trimmed_image, "trimmed", page_num)

        # 特定の領域を黒く塗りつぶす (不要な情報を非表示)
        blacked_out_image = trim_and_blackout_columns(trimmed_image)
        # 黒塗り後の画像を保存 (デバッグ用)
        save_debug_image(blacked_out_image, "blacked_out", page_num)
        
        # OCR前処理 (ノイズ除去やしきい値処理で文字認識を最適化)
        # 下のコードで'C:/Users/user/debug_images/page2_1_threshold.png'のようなファイルが生成
        processed_image = preprocess_image_for_ocr(trimmed_image, page_num)
        
        # OCR追加処理 (画像をシャープ化して認識精度を向上)
        enhanced_image = enhance_image_for_ocr(processed_image, page_num)

# メイン処理
def main():
    # PDFファイルのパス
    # pdf_path = '/Users/yuri23/Downloads/佐々木麻緒(000058) 2024年05月度.pdf'
    pdf_path = 'C:/Users/user/Desktop/work_data/jobkan_file\佐々木麻緒(000058) 2024年05月度.pdf'
    process_pdf_for_table(pdf_path)

if __name__ == '__main__':
    main()