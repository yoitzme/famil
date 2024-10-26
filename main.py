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

def display_notifications():
    """Display notifications dropdown."""
    conn = get_db_connection()
    if not conn:
        return
    
    # Initialize session state for notifications
    if 'last_notification_check' not in st.session_state:
        st.session_state.last_notification_check = datetime.now() - timedelta(minutes=5)
    
    # Check for new notifications every 5 minutes
    if datetime.now() - st.session_state.last_notification_check > timedelta(minutes=5):
        check_and_create_notifications(conn)
        st.session_state.last_notification_check = datetime.now()
    
    # Get unread count and highest priority
    unread_count = get_unread_count(conn, "family")
    highest_priority = 1
    if unread_count > 0:
        notifications = get_notifications(conn, "family", unread_only=True)
        if notifications:
            highest_priority = max(n['priority'] for n in notifications)
    
    # Create notification button with badge and sound
    col1, col2 = st.columns([0.1, 3.9])
    with col1:
        if unread_count > 0:
            notification_button = st.button(
                f"{get_notification_sound(highest_priority)} ({unread_count})",
                help=f"You have {unread_count} unread notifications"
            )
        else:
            notification_button = st.button("🔔", help="No new notifications")
    
    # Show notifications if button is clicked
    if notification_button:
        with st.expander("Recent Notifications", expanded=True):
            notifications = get_notifications(conn, "family", limit=10)
            
            if not notifications:
                st.info("No notifications")
            else:
                # Group notifications by date
                today = datetime.now().date()
                current_date = None
                
                for notif in notifications:
                    notif_date = notif['created_at'].date()
                    
                    # Add date header
                    if notif_date != current_date:
                        if notif_date == today:
                            st.subheader("Today")
                        elif notif_date == today - timedelta(days=1):
                            st.subheader("Yesterday")
                        else:
                            st.subheader(notif_date.strftime('%B %d, %Y'))
                        current_date = notif_date
                    
                    col1, col2 = st.columns([3, 0.5])
                    with col1:
                        st.markdown(f"""
                        <div style="
                            background-color: {get_notification_color(notif['priority'])};
                            padding: 10px;
                            border-radius: 5px;
                            margin: 5px 0;
                            opacity: {'0.7' if notif['read_status'] else '1'};
                            border-left: 5px solid {get_notification_color(notif['priority'])};
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

def main():
    # Initialize database
    init_db()
    
    # Display notifications at the top
    display_notifications()
    
    # Hero Section
    st.markdown('''
    <div class="hero" style="
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    ">
        <h1>🏠 Family Organization System</h1>
        <p class="lead">Keep your family organized and connected!</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Quick Actions Section
    st.subheader("Quick Actions")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('''
        <div class="section" style="
            background-color: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
        ">
            <h2>📋 Today's Tasks</h2>
        </div>
        ''', unsafe_allow_html=True)
        
        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT task, assigned_to 
                        FROM chores 
                        WHERE due_date = CURRENT_DATE AND completed = FALSE
                    """)
                    today_tasks = cur.fetchall()
                    if today_tasks:
                        for task in today_tasks:
                            st.markdown(f"• {task[0]} ({task[1]})")
                    else:
                        st.info("No tasks due today")
            finally:
                conn.close()
        
    with col2:
        st.markdown('''
        <div class="section" style="
            background-color: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
        ">
            <h2>🛒 Shopping List</h2>
        </div>
        ''', unsafe_allow_html=True)
        
        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT item, quantity 
                        FROM grocery_items 
                        WHERE purchased = FALSE 
                        LIMIT 5
                    """)
                    shopping_items = cur.fetchall()
                    if shopping_items:
                        for item in shopping_items:
                            st.markdown(f"• {item[0]} (x{item[1]})")
                    else:
                        st.info("Shopping list is empty")
            finally:
                conn.close()
                
    # Navigation Help
    st.markdown("""
    ## Navigate Your Family Hub
    
    Use the sidebar to access:
    - 📅 Calendar - Track family events and appointments
    - ✅ Chores - Manage household tasks
    - 🛒 Grocery List - Keep track of shopping needs
    - 🏫 School Events - Stay updated with school activities
    - 🍽️ Meal Planner - Plan your family meals
    """)

if __name__ == "__main__":
    main()
