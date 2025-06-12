import sqlite3

DB_FILE = 'data/subscribers.db'

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE)
        self.cur = self.conn.cursor()
        self.cur.execute('''CREATE TABLE IF NOT EXISTS subscribers (user_id INTEGER PRIMARY KEY, username TEXT, full_name TEXT)''')
        self.conn.commit()
        # conn.close()

    def get_saved_subscribers(self):
        self.cur.execute("SELECT user_id, username, full_name FROM subscribers")
        result = {row[0]: {"username": row[1], "full_name": row[2]} for row in self.cur.fetchall()}
        return result

    def save_subscriber(self, user_id, username, full_name):
        self.cur.execute(
            "INSERT OR REPLACE INTO subscribers (user_id, username, full_name) VALUES (?, ?, ?)",
            (user_id, username, full_name)
        )
        self.conn.commit()

    def delete_subscriber(self, user_id):
        self.cur.execute("DELETE FROM subscribers WHERE user_id = ?", (user_id,))
        self.conn.commit()