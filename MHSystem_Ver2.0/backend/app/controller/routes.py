import os
from app.business import detect_company_difference
from flask import Blueprint, jsonify, request

bp = Blueprint("controller", __name__)

# 差異検出コントローラ
@bp.route('/api/detect', methods=['POST'])
def detect_difference():
    difference_Data = detect_company_difference.detect_difference()
    try:
        data = request.get_json()
        year_month = data.get('yearMonth', '')
        
        # ファイルを1つずつ取り出して処理
        return jsonify({
            "status": "success",
            "message": f"差異検出完了: {year_month}",
            "differences": [difference_Data]
        })
        
    except Exception as e:
        print(f"エラー: {e}")
        return jsonify({
            "status": "error",
            "message": "エラーが発生しました"
        }), 500