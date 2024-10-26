import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.database import init_db, get_db_connection
from utils.helpers import configure_page
from utils.notifications import (
    get_notifications, mark_notification_as_read, 
    get_unread_count, check_and_create_notifications,
    get_notification_color, get_notification_sound
)

# Configure the page
configure_page()

# Add custom styles
st.markdown('''
<style>
    .stButton button {
        width: 100%;
        border-radius: 5px;
        padding: 10px 15px;
    }
    .nav-link {
        color: #1F2937;
        text-decoration: none;
        padding: 8px 16px;
        border-radius: 5px;
        margin: 0 5px;
        transition: background-color 0.3s;
    }
    .nav-link:hover {
        background-color: #F3F4F6;
    }
    .nav-link.active {
        background-color: #FF4B4B;
        color: white;
    }
    .quick-action-card {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #FF4B4B;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .quick-action-header {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
    }
    .quick-action-header h3 {
        margin: 0;
        color: #1F2937;
    }
    .quick-action-icon {
        font-size: 1.5em;
        margin-right: 10px;
        color: #FF4B4B;
    }
</style>
''', unsafe_allow_html=True)

def display_navigation():
    """Display top navigation bar."""
    st.markdown('''
    <div style="
        display: flex;
        justify-content: center;
        padding: 10px;
        background-color: white;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    ">
        <a href="/" class="nav-link active">🏠 Home</a>
        <a href="/calendar" class="nav-link">📅 Calendar</a>
        <a href="/chores" class="nav-link">✅ Chores</a>
        <a href="/grocery_list" class="nav-link">🛒 Grocery</a>
        <a href="/school_events" class="nav-link">🏫 School</a>
        <a href="/meal_planner" class="nav-link">🍽️ Meals</a>
    </div>
    ''', unsafe_allow_html=True)

def display_calendar_preview():
    """Display upcoming events preview."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT title, start_date, event_type
                    FROM events
                    WHERE start_date >= CURRENT_DATE
                    ORDER BY start_date
                    LIMIT 5
                """)
                events = cur.fetchall()
                
                st.markdown('''
                <div class="quick-action-card">
                    <div class="quick-action-header">
                        <span class="quick-action-icon">📅</span>
                        <h3>Upcoming Events</h3>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
                
                if events:
                    for event in events:
                        st.markdown(f"""
                        <div style="padding: 5px 10px;">
                            • {event['title']} ({format_date(str(event['start_date']))})
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No upcoming events")
        finally:
            conn.close()

def display_active_chores():
    """Display active chores list."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT task, assigned_to, due_date
                    FROM chores
                    WHERE completed = FALSE
                    ORDER BY due_date
                    LIMIT 5
                """)
                chores = cur.fetchall()
                
                st.markdown('''
                <div class="quick-action-card">
                    <div class="quick-action-header">
                        <span class="quick-action-icon">✅</span>
                        <h3>Active Chores</h3>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
                
                if chores:
                    for chore in chores:
                        st.markdown(f"""
                        <div style="padding: 5px 10px;">
                            • {chore['task']} - {chore['assigned_to']} 
                            (Due: {format_date(str(chore['due_date']))})
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No active chores")
        finally:
            conn.close()

def display_grocery_preview():
    """Display grocery list preview."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT item, quantity
                    FROM grocery_items
                    WHERE purchased = FALSE
                    ORDER BY created_at DESC
                    LIMIT 5
                """)
                items = cur.fetchall()
                
                st.markdown('''
                <div class="quick-action-card">
                    <div class="quick-action-header">
                        <span class="quick-action-icon">🛒</span>
                        <h3>Shopping List</h3>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
                
                if items:
                    for item in items:
                        st.markdown(f"""
                        <div style="padding: 5px 10px;">
                            • {item['item']} (x{item['quantity']})
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Shopping list is empty")
        finally:
            conn.close()

def main():
    # Initialize database
    init_db()
    
    # Display navigation at the top
    display_navigation()
    
    # Display notifications
    display_notifications()
    
    # Hero Section (more compact)
    st.markdown('''
    <div style="
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        text-align: center;
    ">
        <h1>🏠 Family Organization System</h1>
        <p>Keep your family organized and connected!</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Display quick action sections in columns
    col1, col2 = st.columns(2)
    
    with col1:
        display_calendar_preview()
        display_active_chores()
    
    with col2:
        display_grocery_preview()

if __name__ == "__main__":
    main()
