from google_vision_ocr import google_vision_ocr1
from google_vision_ocr import google_vision_ocr2
from google_vision_ocr import google_vision_ocr3
from google_vision_ocr import google_vision_ocr4
from google_vision_ocr import google_vision_ocr5

def compare_paired_texts(paired_texts1, paired_texts2):
    """2つのペアリストを比較し、違いを返す関数"""
    total_pairs = len(paired_texts1)

    if total_pairs != len(paired_texts2):
        print("ペアリストの長さが異なります。")

    differences = []

    for i, (pair1, pair2) in enumerate(zip(paired_texts1, paired_texts2)):
        if pair1 != pair2:
            differences.append((i, pair1, pair2))

    if differences:
        print(f"違いが見つかりました: {len(differences)} 件")
        for diff in differences:
            _, p1, p2 = diff
            print(f"{p1[0]}日： {p1[1]} != {p2[1]}")
    else:
        print(f"合計 {total_pairs} 件全て一致しています。")

    return differences


if __name__ == "__main__":
    # 正しい画像パスを設定
    paired_texts1 = google_vision_ocr1.detect_and_pair_date_time_text(
        '/Users/yuri23/ocr_project/debug_images/page_1_threshold.png')
    paired_texts2 = google_vision_ocr2.detect_and_pair_date_time_text(
        '/Users/yuri23/ocr_project/debug_images/page2_1_threshold.png')
    paired_texts3 = google_vision_ocr3.detect_and_pair_date_time_text(
        '/Users/yuri23/ocr_project/debug_images/page3_1_threshold.png')
    paired_texts4 = google_vision_ocr4.detect_and_pair_date_time_text(
        '/Users/yuri23/ocr_project/debug_images/page4_1_threshold.png')
    paired_texts5 = google_vision_ocr5.detect_and_pair_date_time_text(
        '/Users/yuri23/ocr_project/debug_images/page5_1_threshold.png')

    # ペアリストを比較
    compare_paired_texts(paired_texts1, paired_texts2)
