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

# Add custom styles for dark theme
st.markdown('''
<style>
    .stButton button {
        width: 100%;
        border-radius: 5px;
        padding: 8px 12px;
    }
    .card {
        background-color: var(--secondary-background-color);
        padding: 15px;
        border-radius: 8px;
        margin: 8px 0;
        border-left: 4px solid var(--primary-color);
        color: #FFFFFF;
    }
    .card-header {
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .card-content {
        margin-top: 8px;
        color: #FFFFFF;
    }
    .meal-card {
        background-color: var(--secondary-background-color);
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid var(--primary-color);
    }
</style>
''', unsafe_allow_html=True)

def display_meal(meal_type):
    """Display a specific meal from today's meal plan."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT r.name, r.description
                    FROM meal_plans mp
                    JOIN recipes r ON mp.recipe_id = r.recipe_id
                    WHERE mp.date = CURRENT_DATE AND mp.meal_type = %s
                """, (meal_type,))
                meal = cur.fetchone()
                
                if meal:
                    st.markdown(f'''
                    <div class="meal-card">
                        <div class="meal-title">{meal['name']}</div>
                        <div class="meal-description">{meal['description']}</div>
                    </div>
                    ''', unsafe_allow_html=True)
                else:
                    st.info(f"No {meal_type} planned for today")
        finally:
            conn.close()

def display_todays_events():
    """Display today's calendar events."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT title, description, event_type
                    FROM events
                    WHERE start_date = CURRENT_DATE
                    ORDER BY start_date
                """)
                events = cur.fetchall()
                
                if events:
                    for event in events:
                        st.markdown(f'''
                        <div class="card">
                            <div class="card-header">
                                <strong>{event['title']}</strong>
                                <span>{event['event_type']}</span>
                            </div>
                            <div class="card-content">
                                {event['description']}
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)
                else:
                    st.info("No events scheduled for today")
        finally:
            conn.close()

def display_active_chores():
    """Display active chores."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT task, assigned_to
                    FROM chores
                    WHERE due_date = CURRENT_DATE AND completed = FALSE
                    ORDER BY task
                """)
                chores = cur.fetchall()
                
                st.markdown("### 📋 Today's Chores")
                if chores:
                    for chore in chores:
                        st.markdown(f'''
                        <div class="card">
                            <div class="card-content">
                                {chore['task']} (Assigned to: {chore['assigned_to']})
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)
                else:
                    st.info("No chores due today")
        finally:
            conn.close()

def display_grocery_list():
    """Display current grocery list summary."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT COUNT(*) as count
                    FROM grocery_items
                    WHERE purchased = FALSE
                """)
                count = cur.fetchone()['count']
                
                st.markdown("### 🛒 Shopping List")
                st.markdown(f'''
                <div class="card">
                    <div class="card-content">
                        {count} items needed
                    </div>
                </div>
                ''', unsafe_allow_html=True)
        finally:
            conn.close()

def display_notifications():
    """Display recent notifications."""
    conn = get_db_connection()
    if conn:
        try:
            notifications = get_notifications(conn, "family", limit=3)
            
            st.markdown("### 🔔 Recent Notifications")
            if notifications:
                for notif in notifications:
                    st.markdown(f'''
                    <div class="card">
                        <div class="card-content">
                            {get_notification_sound(notif['priority'])} {notif['message']}
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
            else:
                st.info("No new notifications")
        finally:
            conn.close()

def main():
    st.title("Family Organization System 🏠")
    
    # Today's Overview
    st.header("Today's Overview")
    
    # Three-column layout for meals
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("🌅 Breakfast")
        display_meal("Breakfast")
    with col2:
        st.subheader("☀️ Lunch")
        display_meal("Lunch")
    with col3:
        st.subheader("🌙 Dinner")
        display_meal("Dinner")
    
    # Calendar Events
    st.subheader("Today's Schedule")
    display_todays_events()
    
    # Quick Actions
    st.header("Quick Actions")
    action_col1, action_col2, action_col3 = st.columns(3)
    with action_col1:
        display_active_chores()
    with action_col2:
        display_grocery_list()
    with action_col3:
        display_notifications()

if __name__ == "__main__":
    init_db()
    main()
