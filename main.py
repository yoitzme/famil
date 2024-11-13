import streamlit as st
from datetime import datetime, timedelta
from utils.database import get_db_connection
from utils.helpers import format_date, is_mobile
from utils.notifications import (
    get_notifications, mark_notification_as_read, 
    get_unread_count, check_and_create_notifications,
    get_notification_color, get_notification_sound
)
from psycopg2.extras import RealDictCursor
from utils.styles import get_mobile_styles, get_base_styles
from utils.init_database import initialize_database
from utils.websocket import websocket_manager
from utils.logger import log_info, log_error
from pages.calendar import main as calendar_viewc
from pages.grocery_list import main as display_shopping_view
from pages.events import main as render_events_view
from pages.home import main as home_view
from pages.todolist import main as display_todo_list

# Must be the first Streamlit command
st.set_page_config(
    page_title="Family Hub",
    page_icon="👨‍👩‍👧‍👦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def main():
    """Main application function."""
    try:
        # Initialize database
        initialize_database()
        
        # Add base styles and header
        st.markdown("""
            <style>
                /* Header container */
                .dashboard-header {
                    text-align: center;
                    padding: 2rem;
                    background: linear-gradient(90deg, rgba(255,75,75,0.1) 0%, rgba(255,143,0,0.1) 100%);
                    border-radius: 10px;
                    margin: 1rem 0 3rem 0;
                    position: relative;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                    border: 1px solid rgba(255,255,255,0.1);
                    clear: both;
                    display: block;
                    width: 100%;
                }
                
                /* Title styling */
                .main-title {
                    font-size: 2.5rem;
                    font-weight: bold;
                    background: linear-gradient(45deg, #FF4B4B, #FF8F00);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    margin-bottom: 1rem;
                    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
                    line-height: 1.4;
                    display: block;
                }
                
                /* Subtitle styling */
                .subtitle {
                    font-size: 1.2rem;
                    color: #9CA3AF;
                    animation: fadeInOut 4s infinite;
                    display: block;
                    margin-top: 0.5rem;
                    clear: both;
                }
            </style>
            
            <div class="dashboard-header">
                <h1 class="main-title">🏠 Family Hub Dashboard</h1>
                <p class="subtitle">Organizing Family Life Together</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Create tabs
        tabs = st.tabs([
            "🏠 Home", "✅ Tasks", "📅 Calendar", "🛒 Shopping",
            "📋 Events", "👨‍👩‍👧‍👦 Family", "🏋️ Gym", "🎓 School",
            "📈 Finances", "📊 Goals", "🎉 Celebrations"
        ])
        
        # Tab content
        with tabs[0]: home_view()
        with tabs[1]: display_todo_list()
        with tabs[2]: calendar_viewc()
        with tabs[3]: display_shopping_view()
        with tabs[4]: render_events_view()
        
        # Placeholder tabs
        for i in range(5, 11):
            with tabs[i]:
                st.info("This feature is coming soon!")
                
    except Exception as e:
        log_error(f"Application error: {str(e)}")
        st.error("An error occurred. Please check the logs.")

if __name__ == "__main__":
    main()
