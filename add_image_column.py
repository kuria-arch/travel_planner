import sqlite3

def add_image_column():
    try:
        conn = sqlite3.connect('planner.db')
        cursor = conn.cursor()
        cursor.execute("ALTER TABLE activities ADD COLUMN image_url TEXT")
        conn.commit()
        conn.close()
        print("✅ Added image_url column to activities table!")
    except sqlite3.Error as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    add_image_column()