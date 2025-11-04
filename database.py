"""
Database Module for Stress Analysis
SQLite database to store and retrieve stress analysis history
"""

import sqlite3
from datetime import datetime, timedelta
import json

class StressDatabase:
    def __init__(self, db_path='stress_history.db'):
        """Initialize database connection and create tables"""
        self.db_path = db_path
        self.create_tables()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def create_tables(self):
        """Create database tables if they don't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stress_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                face_emotion TEXT,
                face_confidence REAL,
                speech_emotion TEXT,
                speech_confidence REAL,
                stress_level TEXT,
                stress_score REAL
            )
        ''')
        
        # Create index on timestamp for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON stress_readings(timestamp)
        ''')
        
        conn.commit()
        conn.close()
    
    def save_stress_reading(self, face_emotion, face_confidence, 
                           speech_emotion, speech_confidence, 
                           stress_level, stress_score):
        """Save a stress reading to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Use explicit timestamp to avoid timezone issues
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
            INSERT INTO stress_readings 
            (timestamp, face_emotion, face_confidence, speech_emotion, speech_confidence, 
             stress_level, stress_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (current_time, face_emotion, face_confidence, speech_emotion, speech_confidence,
              stress_level, stress_score))
        
        conn.commit()
        conn.close()
    
    def get_recent_readings(self, limit=50):
        """Get the most recent stress readings"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM stress_readings 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_history(self, hours=1):
        """Get stress readings from the last N hours"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        time_threshold = (datetime.now() - timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
            SELECT * FROM stress_readings 
            WHERE timestamp >= ?
            ORDER BY timestamp ASC
        ''', (time_threshold,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_summary_stats(self, hours=24):
        """Get summary statistics for the last N hours"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        time_threshold = (datetime.now() - timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S')
        
        # Get average stress score
        cursor.execute('''
            SELECT 
                AVG(stress_score) as avg_stress,
                MAX(stress_score) as max_stress,
                MIN(stress_score) as min_stress,
                COUNT(*) as total_readings
            FROM stress_readings 
            WHERE timestamp >= ?
        ''', (time_threshold,))
        
        stats = dict(cursor.fetchone())
        
        # Get stress level distribution
        cursor.execute('''
            SELECT stress_level, COUNT(*) as count
            FROM stress_readings 
            WHERE timestamp >= ?
            GROUP BY stress_level
        ''', (time_threshold,))
        
        distribution = {row['stress_level']: row['count'] for row in cursor.fetchall()}
        stats['stress_distribution'] = distribution
        
        # Get emotion distribution
        cursor.execute('''
            SELECT face_emotion, COUNT(*) as count
            FROM stress_readings 
            WHERE timestamp >= ?
            GROUP BY face_emotion
        ''', (time_threshold,))
        
        face_emotions = {row['face_emotion']: row['count'] for row in cursor.fetchall()}
        stats['face_emotion_distribution'] = face_emotions
        
        conn.close()
        
        return stats
    
    def clear_old_data(self, days=7):
        """Clear data older than N days"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        time_threshold = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
            DELETE FROM stress_readings 
            WHERE timestamp < ?
        ''', (time_threshold,))
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted_count
