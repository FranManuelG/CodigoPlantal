import sqlite3
import os
from datetime import datetime
from typing import List, Tuple, Optional
from urllib.parse import urlparse

class Database:
    def __init__(self, db_path: str = 'plants.db'):
        self.database_url = os.getenv('DATABASE_URL')
        self.use_postgres = bool(self.database_url)
        
        if self.use_postgres:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            self.psycopg2 = psycopg2
            self.RealDictCursor = RealDictCursor
        else:
            self.db_path = db_path
        
        self._init_db()
    
    def _get_connection(self):
        if self.use_postgres:
            return self.psycopg2.connect(self.database_url)
        else:
            return sqlite3.connect(self.db_path)
    
    def _init_db(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if self.use_postgres:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS plants (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    name TEXT NOT NULL,
                    watering_frequency_days INTEGER NOT NULL,
                    group_id INTEGER,
                    photo_file_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS watering_log (
                    id SERIAL PRIMARY KEY,
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
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS plant_photos (
                    id SERIAL PRIMARY KEY,
                    plant_id INTEGER NOT NULL,
                    file_id TEXT NOT NULL,
                    caption TEXT,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (plant_id) REFERENCES plants (id) ON DELETE CASCADE
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS plant_groups (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_settings (
                    user_id BIGINT PRIMARY KEY,
                    notifications_enabled INTEGER DEFAULT 1,
                    notification_time TEXT DEFAULT '09:00',
                    timezone TEXT DEFAULT 'UTC'
                )
            ''')
        else:
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
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS plant_photos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plant_id INTEGER NOT NULL,
                    file_id TEXT NOT NULL,
                    caption TEXT,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (plant_id) REFERENCES plants (id) ON DELETE CASCADE
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS plant_groups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_settings (
                    user_id INTEGER PRIMARY KEY,
                    notifications_enabled INTEGER DEFAULT 1,
                    notification_time TEXT DEFAULT '09:00',
                    timezone TEXT DEFAULT 'UTC'
                )
            ''')
            
            try:
                cursor.execute('ALTER TABLE plants ADD COLUMN group_id INTEGER')
            except sqlite3.OperationalError:
                pass
            
            try:
                cursor.execute('ALTER TABLE plants ADD COLUMN photo_file_id TEXT')
            except sqlite3.OperationalError:
                pass
        
        conn.commit()
        conn.close()
    
    def add_plant(self, user_id: int, name: str, watering_frequency_days: int) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if self.use_postgres:
            cursor.execute(
                'INSERT INTO plants (user_id, name, watering_frequency_days) VALUES (%s, %s, %s) RETURNING id',
                (user_id, name, watering_frequency_days)
            )
            plant_id = cursor.fetchone()[0]
        else:
            cursor.execute(
                'INSERT INTO plants (user_id, name, watering_frequency_days) VALUES (?, ?, ?)',
                (user_id, name, watering_frequency_days)
            )
            plant_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return plant_id
    
    def get_user_plants(self, user_id: int) -> List[Tuple]:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        placeholder = '%s' if self.use_postgres else '?'
        cursor.execute(f'''
            SELECT 
                p.id, 
                p.name, 
                p.watering_frequency_days,
                (SELECT watered_at FROM watering_log 
                 WHERE plant_id = p.id 
                 ORDER BY watered_at DESC LIMIT 1) as last_watered
            FROM plants p
            WHERE p.user_id = {placeholder}
            ORDER BY p.name
        ''', (user_id,))
        
        result = cursor.fetchall()
        conn.close()
        return result
    
    def get_plant_by_name(self, user_id: int, name: str) -> Optional[Tuple]:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        placeholder = '%s' if self.use_postgres else '?'
        cursor.execute(f'''
            SELECT id, name, watering_frequency_days
            FROM plants
            WHERE user_id = {placeholder} AND name = {placeholder}
        ''', (user_id, name))
        
        result = cursor.fetchone()
        conn.close()
        return result
    
    def record_watering(self, plant_id: int) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if self.use_postgres:
            cursor.execute(
                'INSERT INTO watering_log (plant_id, watered_at) VALUES (%s, %s) RETURNING id',
                (plant_id, datetime.now())
            )
            watering_id = cursor.fetchone()[0]
        else:
            cursor.execute(
                'INSERT INTO watering_log (plant_id, watered_at) VALUES (?, ?)',
                (plant_id, datetime.now().isoformat())
            )
            watering_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return watering_id
    
    def get_watering_history(self, user_id: int, limit: int = 20) -> List[Tuple]:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        placeholder = '%s' if self.use_postgres else '?'
        cursor.execute(f'''
            SELECT p.name, w.watered_at
            FROM watering_log w
            JOIN plants p ON w.plant_id = p.id
            WHERE p.user_id = {placeholder}
            ORDER BY w.watered_at DESC
            LIMIT {placeholder}
        ''', (user_id, limit))
        
        result = cursor.fetchall()
        conn.close()
        return result
    
    def delete_plant(self, plant_id: int):
        conn = self._get_connection()
        cursor = conn.cursor()
        
        placeholder = '%s' if self.use_postgres else '?'
        cursor.execute(f'DELETE FROM watering_log WHERE plant_id = {placeholder}', (plant_id,))
        cursor.execute(f'DELETE FROM plants WHERE id = {placeholder}', (plant_id,))
        
        conn.commit()
        conn.close()
    
    def get_plants_needing_water(self, user_id: int) -> List[Tuple]:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        placeholder = '%s' if self.use_postgres else '?'
        cursor.execute(f'''
            SELECT 
                p.id,
                p.name,
                p.watering_frequency_days,
                (SELECT watered_at FROM watering_log 
                 WHERE plant_id = p.id 
                 ORDER BY watered_at DESC LIMIT 1) as last_watered
            FROM plants p
            WHERE p.user_id = {placeholder}
        ''', (user_id,))
        
        result = cursor.fetchall()
        conn.close()
        return result
    
    def add_plant_photo(self, plant_id: int, file_id: str, caption: str = None) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if self.use_postgres:
            cursor.execute(
                'INSERT INTO plant_photos (plant_id, file_id, caption) VALUES (%s, %s, %s) RETURNING id',
                (plant_id, file_id, caption)
            )
            photo_id = cursor.fetchone()[0]
            cursor.execute(
                'UPDATE plants SET photo_file_id = %s WHERE id = %s',
                (file_id, plant_id)
            )
        else:
            cursor.execute(
                'INSERT INTO plant_photos (plant_id, file_id, caption) VALUES (?, ?, ?)',
                (plant_id, file_id, caption)
            )
            photo_id = cursor.lastrowid
            cursor.execute(
                'UPDATE plants SET photo_file_id = ? WHERE id = ?',
                (file_id, plant_id)
            )
        
        conn.commit()
        conn.close()
        return photo_id
    
    def get_plant_photos(self, plant_id: int) -> List[Tuple]:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        placeholder = '%s' if self.use_postgres else '?'
        cursor.execute(f'''
            SELECT id, file_id, caption, uploaded_at
            FROM plant_photos
            WHERE plant_id = {placeholder}
            ORDER BY uploaded_at DESC
        ''', (plant_id,))
        
        result = cursor.fetchall()
        conn.close()
        return result
    
    def create_group(self, user_id: int, name: str) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if self.use_postgres:
            cursor.execute(
                'INSERT INTO plant_groups (user_id, name) VALUES (%s, %s) RETURNING id',
                (user_id, name)
            )
            group_id = cursor.fetchone()[0]
        else:
            cursor.execute(
                'INSERT INTO plant_groups (user_id, name) VALUES (?, ?)',
                (user_id, name)
            )
            group_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return group_id
    
    def get_user_groups(self, user_id: int) -> List[Tuple]:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        placeholder = '%s' if self.use_postgres else '?'
        cursor.execute(f'''
            SELECT id, name, 
                (SELECT COUNT(*) FROM plants WHERE group_id = plant_groups.id) as plant_count
            FROM plant_groups
            WHERE user_id = {placeholder}
            ORDER BY name
        ''', (user_id,))
        
        result = cursor.fetchall()
        conn.close()
        return result
    
    def assign_plant_to_group(self, plant_id: int, group_id: int):
        conn = self._get_connection()
        cursor = conn.cursor()
        
        placeholder = '%s' if self.use_postgres else '?'
        cursor.execute(
            f'UPDATE plants SET group_id = {placeholder} WHERE id = {placeholder}',
            (group_id, plant_id)
        )
        
        conn.commit()
        conn.close()
    
    def get_plants_by_group(self, group_id: int) -> List[Tuple]:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        placeholder = '%s' if self.use_postgres else '?'
        cursor.execute(f'''
            SELECT id, name, watering_frequency_days
            FROM plants
            WHERE group_id = {placeholder}
            ORDER BY name
        ''', (group_id,))
        
        result = cursor.fetchall()
        conn.close()
        return result
    
    def get_user_settings(self, user_id: int) -> Optional[Tuple]:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        placeholder = '%s' if self.use_postgres else '?'
        cursor.execute(
            f'SELECT notifications_enabled, notification_time FROM user_settings WHERE user_id = {placeholder}',
            (user_id,)
        )
        
        result = cursor.fetchone()
        conn.close()
        return result
    
    def update_notification_settings(self, user_id: int, enabled: bool, time: str = None):
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if self.use_postgres:
            cursor.execute('''
                INSERT INTO user_settings (user_id, notifications_enabled, notification_time) 
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id) 
                DO UPDATE SET notifications_enabled = %s, notification_time = %s
            ''', (user_id, 1 if enabled else 0, time or '09:00', 1 if enabled else 0, time or '09:00'))
        else:
            cursor.execute(
                'INSERT OR REPLACE INTO user_settings (user_id, notifications_enabled, notification_time) VALUES (?, ?, ?)',
                (user_id, 1 if enabled else 0, time or '09:00')
            )
        
        conn.commit()
        conn.close()
    
    def get_all_users_for_notifications(self) -> List[int]:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT user_id 
            FROM user_settings 
            WHERE notifications_enabled = 1
        ''')
        
        result = [row[0] for row in cursor.fetchall()]
        conn.close()
        return result
    
    def get_watering_stats(self, user_id: int) -> dict:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        placeholder = '%s' if self.use_postgres else '?'
        
        cursor.execute(
            f'SELECT COUNT(*) FROM watering_log w JOIN plants p ON w.plant_id = p.id WHERE p.user_id = {placeholder}',
            (user_id,)
        )
        total_waterings = cursor.fetchone()[0]
        
        cursor.execute(
            f'SELECT COUNT(*) FROM plants WHERE user_id = {placeholder}',
            (user_id,)
        )
        total_plants = cursor.fetchone()[0]
        
        cursor.execute(f'''
            SELECT p.name, COUNT(w.id) as count
            FROM plants p
            LEFT JOIN watering_log w ON p.id = w.plant_id
            WHERE p.user_id = {placeholder}
            GROUP BY p.id, p.name
            ORDER BY count DESC
            LIMIT 1
        ''', (user_id,))
        most_watered = cursor.fetchone()
        
        cursor.execute(f'''
            SELECT COUNT(DISTINCT DATE(watered_at))
            FROM watering_log w
            JOIN plants p ON w.plant_id = p.id
            WHERE p.user_id = {placeholder}
        ''', (user_id,))
        days_active = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_waterings': total_waterings,
            'total_plants': total_plants,
            'most_watered': most_watered,
            'days_active': days_active
        }
