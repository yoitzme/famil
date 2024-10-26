import os
import psycopg2
from psycopg2.extras import RealDictCursor
import streamlit as st

def get_db_connection():
    """Create a database connection using environment variables."""
    try:
        conn = psycopg2.connect(
            host=os.environ['PGHOST'],
            database=os.environ['PGDATABASE'],
            user=os.environ['PGUSER'],
            password=os.environ['PGPASSWORD'],
            port=os.environ['PGPORT']
        )
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {type(e).__name__}")
        return None

def init_db():
    """Initialize database tables if they don't exist."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                with open('schema.sql', 'r') as file:
                    cur.execute(file.read())
            conn.commit()
        except Exception as e:
            st.error(f"Database initialization failed: {type(e).__name__}")
        finally:
            conn.close()

@st.cache_data(ttl=300)
def fetch_all_events():
    """Fetch all calendar events."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM events ORDER BY start_date;")
                return cur.fetchall()
        finally:
            conn.close()
    return []
