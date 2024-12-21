import io
import re
from google.cloud import vision
from google.api_core.exceptions import GoogleAPIError

# 時間の形式を変換する関数
def format_time_text(time_text):
    if re.match(r'^\d{1,2}:\d{2}$', time_text):
        hours, minutes = time_text.split(':')
        return str(int(hours)) + minutes  
    return time_text

# 時間を加算する関数（テクノクリエイティブに限る）
def add_times(time1, time2):
    h1, m1 = map(int, time1.split(':'))
    h2, m2 = map(int, time2.split(':'))
    total_minutes = (h1 * 60 + m1) + (h2 * 60 + m2)
    new_hours = total_minutes // 60
    new_minutes = total_minutes % 60
    return f"{new_hours}:{new_minutes:02d}"

# 画像からテキストを抽出し、座標を確認する関数
def detect_and_pair_date_time_text(image_path):
    try:
        client = vision.ImageAnnotatorClient()

        with io.open(image_path, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)
        response = client.text_detection(image=image)

        # テキスト抽出結果があるか確認
        texts = response.text_annotations
        if texts:
            text_data = []
            date_pattern = r'^\d{1,2}$'  
            time_pattern = r'^\d{1,2}:\d{2}$' 

            # 各テキストの座標とそのテキストを取得
            for text in texts[1:]:
                vertices = text.bounding_poly.vertices
                x1, y1 = vertices[0].x, vertices[0].y
                x2, y2 = vertices[2].x, vertices[2].y
                detected_text = text.description

                # 日付または時間形式に合致するテキストのみを抽出
                if re.match(date_pattern, detected_text) or re.match(time_pattern, detected_text):
                    text_data.append({
                        "text": detected_text,
                        "x1": x1,
                        "y1": y1,
                        "x2": x2,
                        "y2": y2
                    })
                    #print(f"テキスト: '{detected_text}', 座標: 左上({x1}, {y1}), 右下({x2}, {y2})")

            # 高さ順にテキストをソート
            text_data.sort(key=lambda t: t['y1'])
            tolerance = 10  
            paired_texts = []
            updated_times = []

            # ペアリング
            for i in range(len(text_data) - 1):
                text1 = text_data[i]
                text2 = text_data[i + 1]

                if abs(text1['y1'] - text2['y1']) <= tolerance:
                    if re.match(time_pattern, text1['text']) and re.match(time_pattern, text2['text']):
                        # 2つの時間を合計
                        hours1, minutes1 = map(int, text1['text'].split(':'))
                        hours2, minutes2 = map(int, text2['text'].split(':'))
                        total_minutes = (hours1 * 60 + minutes1) + (hours2 * 60 + minutes2)
                        new_hours = total_minutes // 60
                        new_minutes = total_minutes % 60
                        new_time = f"{new_hours}:{new_minutes:02d}"
                        
                        new_time = format_time_text(new_time)

                        # 新しい時間をtext1の座標でペアリングリストに追加
                        updated_times.append({"text": new_time, "y1": text1['y1'], "x1": text1['x1']})
                        #print(f"ペア作成成功: {text1['text']} と {text2['text']} -> {new_time}")
            # 日付と新しい時間のペアリング
            for date_text in text_data:
                if re.match(date_pattern, date_text['text']):
                    for time_text in updated_times:
                        if abs(date_text['y1'] - time_text['y1']) <= tolerance:
                            paired_texts.append((date_text['text'], time_text['text']))
                            #print(f"ペア作成成功: {date_text['text']} と {time_text['text']}")

            # # ペアを表示
            # print("\nペアになったテキスト:")
            # for pair in paired_texts:
            #     print(f"{pair[0]:<15} - {pair[1]:<15}")
        else:
            print("テキストが検出されませんでした。")
            return ""

    except GoogleAPIError as e:
        print(f"Google Cloud Vision APIの呼び出しに失敗しました: {e}")
        return ""
    except FileNotFoundError:
        print(f"指定されたファイルが見つかりません: {image_path}")
        return ""
    print(paired_texts)
    return paired_texts  

# メイン処理
if __name__ == "__main__":
    # 画像のパス
    image_path = '/Users/yuri23/ocr_project/debug_images/page5_1_threshold.png'
    image_path = 'C:/Users/user/debug_images/page5_1_threshold.png'
    # 抽出処理を実行
    detect_and_pair_date_time_text(image_path)
