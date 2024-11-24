import io
from google.cloud import vision
from pdf2image import convert_from_path

# Google Cloud Vision APIクライアントの作成
client = vision.ImageAnnotatorClient()

#画像からテキストを抽出する関数
def extract_text_from_image_using_vision(image):
    # 画像をバイトデータに変換
    image_byte_arr = io.BytesIO()
    image.save(image_byte_arr, format='PNG')
    content = image_byte_arr.getvalue()

    # Vision APIで画像を解析
    image_vision = vision.Image(content=content)
    response = client.text_detection(image=image_vision)

    # テキストを抽出
    texts = response.text_annotations
    if texts:
        return texts[0].description
    else:
        return ""

#抽出されたテキストから会社を判別する関数
def identify_company_by_text(ocr_text):
    if "TDI" in ocr_text:
        return "TDIシステム"
    elif "株式会社システムシェアード" in ocr_text:
        return "システムシェアード"
    elif "システムサポート" in ocr_text:
        return "システムサポート"
    elif "テクノクリエイティブ" in ocr_text:
        return "テクノクリエイティブ"
    else:
        return "不明"

#PDFを画像に変換し、会社を判別する関数
def process_pdf_for_company_name(pdf_path):
    images = convert_from_path(pdf_path)  # DPIの設定を外してデフォルトに戻す
    for page_num, image in enumerate(images):
        # 画像からGoogle Cloud Vision APIでテキストを抽出
        ocr_text = extract_text_from_image_using_vision(image)

        # テキストから会社名を判別
        company = identify_company_by_text(ocr_text)
        if company != "不明":
            print(f"ページ {page_num + 1} で {company} が判別されました。")
            return company 
    return "不明" 
