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
            print(f"Error releasing connection: {str(e)}")
