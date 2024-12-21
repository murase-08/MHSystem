from flask import Flask
from flask_cors import CORS
import json 

# Flaskアプリケーションの初期化
def create_app():
    app = Flask(__name__)
    CORS(app)  # フロントエンドと通信するためのCORS対応

    # 設定ファイルの読み込み
    app.config.from_file("../config/settings.json", load=json.load)
    
    # routes.py で定義されたルート（エンドポイント）を登録。
    # Blueprintの登録（コントローラー層のルートを登録）
    from app.controller.routes import bp as controller_bp
    app.register_blueprint(controller_bp)

    return app
