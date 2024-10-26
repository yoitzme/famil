import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.database import init_db, get_db_connection
from utils.helpers import configure_page, format_date
from utils.notifications import (
    get_notifications, mark_notification_as_read, 
    get_unread_count, check_and_create_notifications,
    get_notification_color, get_notification_sound
)
from psycopg2.extras import RealDictCursor

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
    .nav-item {
        padding: 8px 16px;
        border-radius: 5px;
        margin: 0 5px;
        transition: background-color 0.3s;
    }
    .nav-item:hover {
        background-color: #F3F4F6;
    }
    .nav-item.active {
        background-color: #FF4B4B;
        color: white !important;
    }
    .quick-action-card {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #FF4B4B;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
''', unsafe_allow_html=True)

def display_navigation():
    """Display top navigation using Streamlit components."""
    st.markdown("### Navigation")
    cols = st.columns(6)
    
    # Create navigation items using Streamlit components
    with cols[0]:
        if st.button("🏠 Home", use_container_width=True):
            st.switch_page("main.py")
    with cols[1]:
        if st.button("📅 Calendar", use_container_width=True):
            st.switch_page("pages/01_calendar.py")
    with cols[2]:
        if st.button("✅ Chores", use_container_width=True):
            st.switch_page("pages/02_chores.py")
    with cols[3]:
        if st.button("🛒 Grocery", use_container_width=True):
            st.switch_page("pages/03_grocery_list.py")
    with cols[4]:
        if st.button("🏫 School", use_container_width=True):
            st.switch_page("pages/04_school_events.py")
    with cols[5]:
        if st.button("🍽️ Meals", use_container_width=True):
            st.switch_page("pages/05_meal_planner.py")

def display_notifications():
    """Display notifications in header."""
    conn = get_db_connection()
    if not conn:
        return
    
    # Check for new notifications
    check_and_create_notifications(conn)
    
    # Get unread notifications
    unread_count = get_unread_count(conn, "family")
    
    # Create notifications dropdown
    with st.expander(f"🔔 Notifications ({unread_count} unread)"):
        notifications = get_notifications(conn, "family", limit=10)
        if not notifications:
            st.info("No notifications")
        else:
            for notif in notifications:
                col1, col2 = st.columns([3, 0.5])
                with col1:
                    st.markdown(f"""
                    <div style="
                        background-color: {get_notification_color(notif['priority'])};
                        padding: 10px;
                        border-radius: 5px;
                        margin: 5px 0;
                        opacity: {'0.7' if notif['read_status'] else '1'};
                    ">
                        {get_notification_sound(notif['priority'])} {notif['message']}
                        <br>
                        <small>{notif['created_at'].strftime('%H:%M')}</small>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    if not notif['read_status']:
                        if st.button("✓", key=f"mark_read_{notif['id']}"):
                            mark_notification_as_read(conn, notif['id'])
                            st.rerun()

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
                        <h3>📅 Upcoming Events</h3>
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

def display_points_summary():
    """Display family points summary."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT user_name, points 
                    FROM points_balance 
                    ORDER BY points DESC
                """)
                points = cur.fetchall()
                
                st.markdown('''
                <div class="quick-action-card">
                    <div class="quick-action-header">
                        <h3>🌟 Family Points</h3>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
                
                if points:
                    for user in points:
                        st.markdown(f"""
                        <div style="padding: 5px 10px;">
                            • {user['user_name']}: {user['points']} points
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No points earned yet")
        finally:
            conn.close()

def main():
    # Initialize database
    init_db()
    
    # Display navigation and notifications
    display_navigation()
    display_notifications()
    
    # Hero Section
    st.markdown('''
    <div style="
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
    ">
        <h1>🏠 Family Organization System</h1>
        <p>Keep your family organized and connected!</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Quick action sections
    col1, col2 = st.columns(2)
    with col1:
        display_calendar_preview()
        display_points_summary()
    
    with col2:
        # Sample data and settings in dropdown
        with st.expander("⚙️ Settings & Sample Data"):
            if st.button("Add Sample Calendar Events"):
                st.session_state['add_sample_calendar'] = True
            if st.button("Add Sample Chores"):
                st.session_state['add_sample_chores'] = True
            if st.button("Add Sample Groceries"):
                st.session_state['add_sample_groceries'] = True
            if st.button("Clear All Sample Data"):
                st.session_state['clear_sample_data'] = True

if __name__ == "__main__":
    main()
