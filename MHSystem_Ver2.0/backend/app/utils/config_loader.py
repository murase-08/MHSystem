import json
import os
# settings.jsonを使うための設定
def load_settings():
    base_dir = os.path.dirname(os.path.abspath(__file__))  # 現在のファイルの絶対ディレクトリ
    config_path = os.path.join(base_dir, "..", "..","config", "settings.json")  # 相対パスで設定ファイルを指定
    with open(config_path, "r", encoding="utf-8") as file:
        settings = json.load(file)
    return settings