import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.database import init_db, get_db_connection
from utils.helpers import configure_page
from utils.notifications import (
    get_notifications, mark_notification_as_read, 
    get_unread_count, check_and_create_notifications,
    get_notification_color
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
    
    # Get unread count
    unread_count = get_unread_count(conn, "family")
    
    # Create notification button with badge
    col1, col2 = st.columns([0.1, 3.9])
    with col1:
        if unread_count > 0:
            notification_button = st.button(
                f"🔔 ({unread_count})",
                help="Click to view notifications"
            )
        else:
            notification_button = st.button("🔔", help="Click to view notifications")
    
    # Show notifications if button is clicked
    if notification_button:
        with st.expander("Recent Notifications", expanded=True):
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
                            opacity: {'0.7' if notif['read_status'] else '1'}
                        ">
                            {notif['message']}
                            <br>
                            <small>{notif['created_at'].strftime('%Y-%m-%d %H:%M')}</small>
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
    
    st.title("Family Organization System")
    
    # Welcome message
    st.markdown("""
    ## Welcome to Your Family Dashboard! 👋
    
    Navigate through the different sections using the sidebar:
    - 📅 Calendar - Track family events and appointments
    - ✅ Chores - Manage household tasks
    - 🛒 Grocery List - Keep track of shopping needs
    - 🏫 School Events - Stay updated with school activities
    """)
    
    # Quick Actions Section
    st.subheader("Quick Actions")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("📋 Today's Tasks")
        # Display today's tasks from database
        
    with col2:
        st.info("🛒 Shopping List")
        # Display current shopping list items

if __name__ == "__main__":
    main()
