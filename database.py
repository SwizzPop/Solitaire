import sqlite3
from datetime import datetime
import os
from kivy.utils import platform

class GameDatabase:
    def __init__(self):
        # Get the appropriate storage path
        if platform == 'android':
            from android.storage import app_storage_path
            db_dir = app_storage_path()
            db_path = os.path.join(db_dir, 'game_stats.db')
        else:
            db_path = 'game_stats.db'  # Fallback for non-Android platforms
        
        print(f"Database path: {db_path}")  # Debug print
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        print("\n=== Creating Tables Debug ===")
        cursor = self.conn.cursor()
        try:
            # Only create the table if it doesn't exist
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                is_autoplay BOOLEAN,
                cards_remaining INTEGER,
                duration_seconds INTEGER,
                status TEXT
            )
            ''')
            self.conn.commit()
            print("Table verified/created successfully")
            
            # Check table schema
            cursor.execute("PRAGMA table_info(game_results)")
            columns = cursor.fetchall()
            print("Table schema:", columns)
        except Exception as e:
            print(f"Error creating table: {e}")
            raise e

    def save_game_result(self, is_autoplay, cards_remaining, duration_seconds, status):
        print("\n=== Database Save Debug ===")
        print(f"Saving: autoplay={is_autoplay}, cards={cards_remaining}, duration={duration_seconds}, status={status}")
        
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO game_results 
            (is_autoplay, cards_remaining, duration_seconds, status)
            VALUES (?, ?, ?, ?)
            ''', (is_autoplay, cards_remaining, duration_seconds, status))
            self.conn.commit()
            print("Database insert successful")
            
            # Verify the save
            cursor.execute('SELECT * FROM game_results ORDER BY id DESC LIMIT 1')
            last_record = cursor.fetchone()
            print(f"Last record in database: {last_record}")
        except Exception as e:
            print(f"Database error: {e}")
            raise e

    def get_stats(self):
        print("\n=== Getting Stats Debug ===")
        cursor = self.conn.cursor()
        
        # First, let's see what's in the table
        cursor.execute('SELECT * FROM game_results')
        all_records = cursor.fetchall()
        print(f"Total records in database: {len(all_records)}")
        print("All records:", all_records)
        
        try:
            cursor.execute('''
            SELECT 
                is_autoplay,
                COUNT(*) as games_played,
                AVG(CAST(cards_remaining AS FLOAT)) as avg_cards_remaining,
                MIN(cards_remaining) as best_result,
                SUM(CASE WHEN status = 'won' THEN 1 ELSE 0 END) as wins
            FROM game_results
            GROUP BY is_autoplay
            ''')
            results = cursor.fetchall()
            print("Stats query results:", results)
            return results
        except Exception as e:
            print(f"Error getting stats: {e}")
            return []
