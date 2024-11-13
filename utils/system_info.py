import platform
import streamlit as st
from datetime import datetime
from utils.database import get_db_connection
import os

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

def get_system_info():
    """Get system information."""
    info = {
        'app_version': '1.0.0',  # Update this with your app version
        'python_version': platform.python_version(),
        'streamlit_version': st.__version__,
        'db_size': get_db_size(),
        'record_count': get_record_count(),
        'last_backup': get_last_backup_date(),
        'system': {
            'os': platform.system(),
            'memory': get_memory_usage() if HAS_PSUTIL else "N/A",
            'cpu': get_cpu_usage() if HAS_PSUTIL else "N/A"
        }
    }
    return info

def get_db_size():
    """Get database size."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT pg_size_pretty(pg_database_size(current_database()))
                """)
                return cur.fetchone()[0]
        finally:
            conn.close()
    return "Unknown"

def get_record_count():
    """Get total record count from main tables."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                tables = ['todo_items', 'events', 'meal_plans']
                total = 0
                for table in tables:
                    cur.execute(f"SELECT COUNT(*) FROM {table}")
                    total += cur.fetchone()[0]
                return total
        finally:
            conn.close()
    return 0

def get_last_backup_date():
    """Get date of last backup."""
    backup_dir = "backups"
    if not os.path.exists(backup_dir):
        return "Never"
    
    files = os.listdir(backup_dir)
    if not files:
        return "Never"
    
    latest = max(
        files,
        key=lambda f: os.path.getmtime(os.path.join(backup_dir, f))
    )
    timestamp = os.path.getmtime(os.path.join(backup_dir, latest))
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

def get_memory_usage():
    """Get current memory usage."""
    if not HAS_PSUTIL:
        return "N/A"
    process = psutil.Process(os.getpid())
    return f"{process.memory_info().rss / 1024 / 1024:.2f} MB"

def get_cpu_usage():
    """Get current CPU usage."""
    if not HAS_PSUTIL:
        return "N/A"
    return f"{psutil.cpu_percent()}%"