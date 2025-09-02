# create_favorites_table.py
import sqlite3

def create_favorites_table():
    try:
        conn = sqlite3.connect('planner.db')
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            city TEXT NOT NULL,
            days INTEGER,
            interests TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        conn.commit()
        conn.close()
        print("✅ Favorites table created!")
    except sqlite3.Error as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_favorites_table()