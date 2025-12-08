import sqlite3
import os

DB_PATH = os.environ.get('PROJECT_DB_PATH', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'PROJECT_DB.sqlite'))

def migrate_db():
    print(f"Migrating DB at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Check existing columns
    cur.execute("PRAGMA table_info(accounts)")
    columns = [info[1] for info in cur.fetchall()]
    
    new_columns = ['facebook', 'youtube', 'twitch', 'reddit']
    
    for col in new_columns:
        if col not in columns:
            print(f"Adding column: {col}")
            try:
                cur.execute(f"ALTER TABLE accounts ADD COLUMN {col} TEXT")
            except sqlite3.OperationalError as e:
                print(f"Error adding {col}: {e}")
        else:
            print(f"Column {col} already exists.")
            
    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == '__main__':
    migrate_db()
