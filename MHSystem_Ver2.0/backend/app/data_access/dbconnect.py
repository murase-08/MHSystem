import sqlite3
from app.utils.config_loader import load_settings

# 設定をロード
settings = load_settings()

def get_db_connection():
    conn = sqlite3.connect(settings["db_path"])  # SQLiteデータベースに接続
    conn.row_factory = sqlite3.Row        # 結果を辞書形式で返す
    return conn

# args:プレースホルダ（?）に挿入される値。
def execute_query(query, args=(), fetchone=False, fetchall=False):
    conn = get_db_connection()
    # SQLクエリを実行するためのカーソルオブジェクトを取得します。
    cursor = conn.cursor()
    # クエリの実行
    cursor.execute(query, args)
    # データベースへの変更（INSERT, UPDATE, DELETE など）を確定します。
    conn.commit()
    result = None
    if fetchone:
        result = cursor.fetchone()
    elif fetchall:
        result = cursor.fetchall()
    # データベース接続を閉じてリソースを解放。
    conn.close()
    return result

# === SQL ===
# false_dataにデータを追加するSQL
def add_false_data_table(check_year_month, name, company_id, file_name, false_days):
    query = "INSERT OR REPLACE INTO false_data (check_year_month, name, company_id, file_name, false_days) VALUES (?, ?, ?, ?, ?)"
    execute_query(query, args=(check_year_month, name, company_id, file_name, false_days))
    