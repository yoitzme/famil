import streamlit as st
from datetime import datetime, timedelta
from utils.database import init_db, get_db_connection, ensure_tables_exist
from utils.helpers import format_date, is_mobile
from utils.notifications import (
    get_notifications, mark_notification_as_read, 
    get_unread_count, check_and_create_notifications,
    get_notification_color, get_notification_sound
)
from psycopg2.extras import RealDictCursor
from utils.styles import get_mobile_styles, get_base_styles
from utils.init_database import initialize_database
from utils.features import (
    display_todo_list,
    display_calendar_widget,
    display_shopping_view,
    render_events_view,
    display_family_view,
    display_weather_widget,
    display_family_status,
    display_quick_notes,
    display_meal_planner,
    display_task_summary
)
from utils.websocket import websocket_manager
import importlib
from utils.error_diagnostics import run_diagnostics

# Must be the first Streamlit command
st.set_page_config(
    page_title="Family Hub",
    page_icon="👨‍👩‍👧‍👦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Add this function definition after the imports and before __main__
def main():
    """Main application function."""
    # Initialize database connection
    conn = get_db_connection()
    if not conn:
        st.error("Failed to connect to database")
        return

    # Create parent tabs
    parent_tabs = st.tabs([
        "✅ Tasks",
        "📅 Calendar",
        "🛒 Shopping",
        "📋 Events",
        "👨‍👩‍👧‍👦 Family",
        "🏋️ Gym",
        "🎓 School",
        "📈 Finances",
        "📊 Goals",
        "🎉 Celebrations"
    ])
    
    # Tasks Tab
    with parent_tabs[0]:
        display_todo_list()
    
    # Calendar Tab
    with parent_tabs[1]:
        display_calendar_widget()
    
    # Shopping Tab
    with parent_tabs[2]:
        display_shopping_view()
    
    # Events Tab
    with parent_tabs[3]:
        render_events_view()
    
    # Family Tab
    with parent_tabs[4]:
        display_family_view()
    
    # Other tabs can be implemented similarly...

if __name__ == "__main__":
    # Run diagnostics first
    if not run_diagnostics():
        st.error("System checks failed. Please fix the errors above before continuing.")
        st.stop()
    
    # Continue with normal app execution
    if not initialize_database():
        st.error("Failed to initialize database. Please check your database connection.")
        st.stop()
    
    main()
