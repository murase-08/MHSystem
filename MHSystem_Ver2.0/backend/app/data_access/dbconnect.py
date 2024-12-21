import sqlite3
from app.utils.config_loader import load_settings

def connect_to_database(db_path):
    try:
        # SQLiteデータベースに接続
        connection = sqlite3.connect(db_path)
        print(f"成功: データベース '{db_path}' に接続できました。")
    except sqlite3.Error as e:
        print(f"エラー: データベースへの接続に失敗しました。{e}")
    finally:
        # 接続を閉じる
        if 'connection' in locals():
            connection.close()
            print("接続を閉じました。")