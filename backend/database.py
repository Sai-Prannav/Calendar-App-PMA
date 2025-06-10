import sqlite3
from sqlite3 import Error
from datetime import datetime
import os

DATABASE_PATH = "weather.db"

def create_connection():
    """Create a database connection to SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        return conn
    except Error as e:
        print(f"Error connecting to database: {e}")
    return conn

def init_db():
    """Initialize the database with required tables"""
    create_weather_queries_table = """
    CREATE TABLE IF NOT EXISTS weather_queries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        location TEXT NOT NULL,
        location_type TEXT NOT NULL,
        date_range_start DATE NOT NULL,
        date_range_end DATE NOT NULL,
        temperature REAL,
        weather_conditions TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    conn = create_connection()
    if conn is not None:
        try:
            c = conn.cursor()
            c.execute(create_weather_queries_table)
            conn.commit()
        except Error as e:
            print(f"Error creating table: {e}")
        finally:
            conn.close()
    else:
        print("Error: Could not establish database connection")

def get_all_queries():
    """Retrieve all weather queries from the database"""
    conn = create_connection()
    queries = []
    if conn is not None:
        try:
            c = conn.cursor()
            c.execute("SELECT * FROM weather_queries ORDER BY created_at DESC")
            queries = c.fetchall()
        except Error as e:
            print(f"Error retrieving queries: {e}")
        finally:
            conn.close()
    return queries

def insert_query(location, location_type, date_range_start, date_range_end, temperature=None, weather_conditions=None):
    """Insert a new weather query into the database"""
    conn = create_connection()
    if conn is not None:
        try:
            sql = """INSERT INTO weather_queries(location, location_type, date_range_start, 
                     date_range_end, temperature, weather_conditions)
                     VALUES(?,?,?,?,?,?)"""
            c = conn.cursor()
            c.execute(sql, (location, location_type, date_range_start, date_range_end, 
                          temperature, weather_conditions))
            conn.commit()
            return c.lastrowid
        except Error as e:
            print(f"Error inserting query: {e}")
            return None
        finally:
            conn.close()
    return None

def update_query(id, temperature=None, weather_conditions=None):
    """Update an existing weather query"""
    conn = create_connection()
    if conn is not None:
        try:
            sql = """UPDATE weather_queries
                     SET temperature = COALESCE(?, temperature),
                         weather_conditions = COALESCE(?, weather_conditions),
                         updated_at = CURRENT_TIMESTAMP
                     WHERE id = ?"""
            c = conn.cursor()
            c.execute(sql, (temperature, weather_conditions, id))
            conn.commit()
            return c.rowcount > 0
        except Error as e:
            print(f"Error updating query: {e}")
            return False
        finally:
            conn.close()
    return False

def delete_query(id):
    """Delete a weather query from the database"""
    conn = create_connection()
    if conn is not None:
        try:
            sql = "DELETE FROM weather_queries WHERE id = ?"
            c = conn.cursor()
            c.execute(sql, (id,))
            conn.commit()
            return c.rowcount > 0
        except Error as e:
            print(f"Error deleting query: {e}")
            return False
        finally:
            conn.close()
    return False