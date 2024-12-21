import io
import re
from google.cloud import vision
from google.api_core.exceptions import GoogleAPIError

# 日付の形式を変換する関数
def format_date_text(date_text):
    if re.match(r'^\d{2}/\d{2}$', date_text):
        return str(int(date_text.split('/')[1]))
    return date_text

# 時間の形式を変換する関数
def format_time_text(time_text):
    if re.match(r'^\d{1,2}:\d{2}$', time_text):
        hours, minutes = time_text.split(':')
        return str(int(hours)) + minutes
    return time_text

# 画像からテキストを抽出し、日付と時間のペアを返す
def detect_and_pair_date_time_text(image_path):
    try:
        # Google Vision APIのクライアントを作成
        client = vision.ImageAnnotatorClient()
        # 画像ファイルを読み込む
        with io.open(image_path, 'rb') as image_file:
            content = image_file.read()
            
        # Vision API用の画像データを準備
        image = vision.Image(content=content)
        # テキスト検出を実行
        response = client.text_detection(image=image)
        # print("以下は検出されたテキスト情報です。")
        # print(response);
        
        # 検出されたすべてのテキスト情報をリスト形式で取得。
        texts = response.text_annotations
        if texts:
            text_data = []
            # 日付形式の正規表現 (例: 05/01)
            date_pattern = r'^\d{2}/\d{2}$'
            # 時間形式の正規表現 (例: 08:45)
            time_pattern = r'^\d{1,2}:\d{2}$'

            # 各テキストの座標とそのテキストを取得
            #print("\n抽出されたテキストとその座標:") 必要に応じて表示
            for text in texts[1:]:
                vertices = text.bounding_poly.vertices
                x1, y1 = vertices[0].x, vertices[0].y # 左上
                x2, y2 = vertices[2].x, vertices[2].y # 右下
                # 検出された文字列
                detected_text = text.description

                # 日付または時間形式に合致するテキストを抽出
                if re.match(date_pattern, detected_text) or re.match(time_pattern, detected_text):
                    text_data.append({
                        "text": detected_text,
                        "x1": x1,
                        "y1": y1,
                        "x2": x2,
                        "y2": y2
                    })

            # Y座標順にソート（上から下の順）
            text_data.sort(key=lambda t: t['y1'])
            # ペアリングの許容範囲（Y座標の差）
            tolerance = 10
            paired_texts = []

           # ペアリング
            for i in range(len(text_data) - 1):
                text1 = text_data[i]
                text2 = text_data[i + 1]

                # y座標の差が許容範囲内であれば、ペアにする
                if abs(text1['y1'] - text2['y1']) <= tolerance:
                    # 日付がtext1、時間がtext2の場合にのみペアを作成
                    if re.match(date_pattern, text1['text']) and re.match(time_pattern, text2['text']):
                        paired_texts.append(
                            (format_date_text(text1['text']), format_time_text(text2['text'])))
                    # 時間がtext1、日付がtext2の場合
                    elif re.match(time_pattern, text1['text']) and re.match(date_pattern, text2['text']):
                        paired_texts.append(
                            (format_date_text(text2['text']), format_time_text(text1['text'])))
            # # ペアリング結果を出力
            # print("ペアになったテキスト:")
            # for pair in paired_texts:
            #     print(f"{pair[0]:<15} - {pair[1]:<15}")

        else:
            # テキストが検出されなかった場合のメッセージ
            print("テキストが検出されませんでした。")
            return ""
    # Google Cloud Vision APIのエラー処理
    except GoogleAPIError as e:
        print(f"Google Cloud Vision APIの呼び出しに失敗しました: {e}")
        return ""
    # ファイルが存在しない場合のエラー処理
    except FileNotFoundError:
        print(f"指定されたファイルが見つかりません: {image_path}")
        return ""
    # ペアリングされた日付と時間のリストを返す
    print(paired_texts)
    return paired_texts

# メイン処理
if __name__ == "__main__":
    # 画像のパス
    # image_path = '/Users/yuri23/ocr_project/debug_images/page_1_threshold.png'
    image_path = 'C:/Users/user/debug_images/page_1_threshold.png'

    # 抽出処理を実行
    detect_and_pair_date_time_text(image_path)