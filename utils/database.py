import os
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
import streamlit as st

def init_connection_pool():
    """Initialize database connection pool."""
    if 'db_pool' not in st.session_state:
        try:
            st.session_state.db_pool = SimpleConnectionPool(
                minconn=1,
                maxconn=20,
                host=os.environ['PGHOST'],
                database=os.environ['PGDATABASE'],
                user=os.environ['PGUSER'],
                password=os.environ['PGPASSWORD'],
                port=os.environ['PGPORT']
            )
        except Exception as e:
            st.error(f"Failed to initialize connection pool: {str(e)}")
            return False
    return True

def get_db_connection():
    """Get connection from pool with automatic cleanup."""
    if not init_connection_pool():
        return None
    
    try:
        # Check if there are available connections
        if st.session_state.db_pool.closed:
            # Reinitialize pool if closed
            init_connection_pool()
        
        conn = st.session_state.db_pool.getconn()
        return conn
    except Exception as e:
        st.error(f"Failed to get database connection: {str(e)}")
        # Try to reinitialize pool
        if 'db_pool' in st.session_state:
            del st.session_state.db_pool
        init_connection_pool()
        return None

def release_connection(conn):
    """Release connection back to pool."""
    if conn and hasattr(st.session_state, 'db_pool'):
        try:
            st.session_state.db_pool.putconn(conn)
        except Exception as e:
            # If putting connection back fails, close it
            try:
                conn.close()
            except:
                pass
            # Reinitialize pool
            if 'db_pool' in st.session_state:
                del st.session_state.db_pool

def cleanup_connections():
    """Clean up all connections in the pool."""
    if 'db_pool' in st.session_state and st.session_state.db_pool:
        try:
            st.session_state.db_pool.closeall()
        except:
            pass
        del st.session_state.db_pool

def init_db():
    """Initialize database tables."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                # Create todo_items table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS todo_items (
                        id SERIAL PRIMARY KEY,
                        task TEXT NOT NULL,
                        priority VARCHAR(20) DEFAULT 'normal',
                        due_date DATE,
                        completed BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

                    -- Create grocery_items table if it doesn't exist
                    CREATE TABLE IF NOT EXISTS grocery_items (
                        id SERIAL PRIMARY KEY,
                        item TEXT NOT NULL,
                        quantity INTEGER DEFAULT 1,
                        unit VARCHAR(50) DEFAULT 'piece',
                        category VARCHAR(50),
                        purchased BOOLEAN DEFAULT FALSE,
                        is_togo BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

                    -- Create events table if it doesn't exist
                    CREATE TABLE IF NOT EXISTS events (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(255) NOT NULL,
                        description TEXT,
                        start_date DATE NOT NULL,
                        end_date DATE,
                        event_type VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

                    -- Create meal_plans table if it doesn't exist
                    CREATE TABLE IF NOT EXISTS meal_plans (
                        id SERIAL PRIMARY KEY,
                        date DATE NOT NULL,
                        meal_type VARCHAR(50),
                        recipe_id INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

                    -- Create recipes table if it doesn't exist
                    CREATE TABLE IF NOT EXISTS recipes (
                        recipe_id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        description TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                conn.commit()
                print("Database tables initialized successfully!")
        except Exception as e:
            st.error(f"Database initialization failed: {str(e)}")
            print(f"Error initializing database: {str(e)}")
        finally:
            release_connection(conn)

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
            release_connection(conn)
    return []

def check_table_exists(table_name):
    """Check if a table exists in the database."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = %s
                    );
                """, (table_name,))
                return cur.fetchone()[0]
        except Exception as e:
            print(f"Error checking table existence: {str(e)}")
            return False
        finally:
            release_connection(conn)
    return False

def ensure_tables_exist():
    """Ensure all required tables exist."""
    required_tables = ['todo_items', 'grocery_items', 'events', 'meal_plans', 'recipes']
    missing_tables = [table for table in required_tables if not check_table_exists(table)]
    
    if missing_tables:
        print(f"Missing tables: {missing_tables}")
        init_db()
