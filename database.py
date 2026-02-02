import sqlite3
from datetime import datetime
from typing import List, Tuple, Optional

class Database:
    def __init__(self, db_path: str = 'plants.db'):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS plants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    watering_frequency_days INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS watering_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plant_id INTEGER NOT NULL,
                    watered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (plant_id) REFERENCES plants (id) ON DELETE CASCADE
                )
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_plants_user_id 
                ON plants(user_id)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_watering_log_plant_id 
                ON watering_log(plant_id)
            ''')
            
            conn.commit()
    
    def add_plant(self, user_id: int, name: str, watering_frequency_days: int) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO plants (user_id, name, watering_frequency_days) VALUES (?, ?, ?)',
                (user_id, name, watering_frequency_days)
            )
            conn.commit()
            return cursor.lastrowid
    
    def get_user_plants(self, user_id: int) -> List[Tuple]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    p.id, 
                    p.name, 
                    p.watering_frequency_days,
                    (SELECT watered_at FROM watering_log 
                     WHERE plant_id = p.id 
                     ORDER BY watered_at DESC LIMIT 1) as last_watered
                FROM plants p
                WHERE p.user_id = ?
                ORDER BY p.name
            ''', (user_id,))
            return cursor.fetchall()
    
    def get_plant_by_name(self, user_id: int, name: str) -> Optional[Tuple]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, watering_frequency_days
                FROM plants
                WHERE user_id = ? AND name = ?
            ''', (user_id, name))
            return cursor.fetchone()
    
    def record_watering(self, plant_id: int) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO watering_log (plant_id, watered_at) VALUES (?, ?)',
                (plant_id, datetime.now().isoformat())
            )
            conn.commit()
            return cursor.lastrowid
    
    def get_watering_history(self, user_id: int, limit: int = 20) -> List[Tuple]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.name, w.watered_at
                FROM watering_log w
                JOIN plants p ON w.plant_id = p.id
                WHERE p.user_id = ?
                ORDER BY w.watered_at DESC
                LIMIT ?
            ''', (user_id, limit))
            return cursor.fetchall()
    
    def delete_plant(self, plant_id: int):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM watering_log WHERE plant_id = ?', (plant_id,))
            cursor.execute('DELETE FROM plants WHERE id = ?', (plant_id,))
            conn.commit()
    
    def get_plants_needing_water(self, user_id: int) -> List[Tuple]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    p.id,
                    p.name,
                    p.watering_frequency_days,
                    (SELECT watered_at FROM watering_log 
                     WHERE plant_id = p.id 
                     ORDER BY watered_at DESC LIMIT 1) as last_watered
                FROM plants p
                WHERE p.user_id = ?
            ''', (user_id,))
            return cursor.fetchall()
