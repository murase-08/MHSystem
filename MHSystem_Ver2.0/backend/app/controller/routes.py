import os
from app.business import detect_company_difference, difference_list
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

# 差異履歴コントローラ
@bp.route('/api/false-data', methods=['GET'])
def get_false_data():
    differences = difference_list.get_false_data()
    try:
        # ファイルを1つずつ取り出して処理
        return jsonify({
            "status": "success",
            "message": f"差異取得完了",
            "differences": differences
        })
        
    except Exception as e:
        print(f"エラー: {e}")
        return jsonify({
            "status": "error",
            "message": "エラーが発生しました"
        }), 500
    