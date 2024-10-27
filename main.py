# Main application file with updated CSS styles
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
        color: #FFFFFF;  /* Make text white for better contrast */
    }
    .card-header {
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .card-content {
        margin-top: 8px;
        color: #FFFFFF;  /* Make text white for better contrast */
    }
    .fixed-height-container {
        height: 300px;
        overflow-y: auto;
        padding: 10px;
        border: 1px solid var(--secondary-background-color);
        border-radius: 8px;
    }
    .event-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    .event-content {
        color: #FFFFFF;  /* Make event description text white */
        font-size: 0.9em;
    }
    .meal-card {
        background-color: var(--secondary-background-color);
        color: #FFFFFF;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid var(--primary-color);
    }
    .meal-title {
        color: #FFFFFF;
        font-size: 1.2em;
        font-weight: bold;
    }
    .meal-description {
        color: #E0E0E0;
        font-size: 0.9em;
        margin-top: 5px;
    }
    @media (max-width: 768px) {
        .stColumn {
            flex: 0 1 100% !important;
            width: 100% !important;
        }
        .meal-card {
            margin: 8px 0;
        }
    }
</style>
''', unsafe_allow_html=True)

def display_notifications():
    """Display notifications in the main interface."""
    conn = get_db_connection()
    if conn:
        try:
            notifications = get_notifications(conn, "family", limit=5)
            if notifications:
                st.subheader("📬 Recent Notifications")
                for notif in notifications:
                    st.markdown(f'''
                    <div class="card">
                        <div class="card-header">
                            {get_notification_sound(notif['priority'])} {notif['message']}
                        </div>
                        <div class="card-content">
                            <small>{notif['created_at'].strftime('%B %d, %Y %I:%M %p')}</small>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
        finally:
            conn.close()

def get_todays_meals():
    """Fetch today's meals from the database."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute('''
                    SELECT mp.meal_type, r.name, r.description
                    FROM meal_plans mp
                    JOIN recipes r ON mp.recipe_id = r.recipe_id
                    WHERE mp.date = CURRENT_DATE
                    ORDER BY CASE mp.meal_type 
                        WHEN 'Breakfast' THEN 1 
                        WHEN 'Lunch' THEN 2 
                        WHEN 'Dinner' THEN 3 
                    END
                ''')
                return cur.fetchall()
        finally:
            conn.close()
    return []

def display_daily_calendar():
    """Display today's calendar events."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT title, description, start_date, event_type
                    FROM events
                    WHERE start_date = CURRENT_DATE
                    ORDER BY start_date
                """)
                events = cur.fetchall()
                
                for event in events:
                    st.markdown(f'''
                    <div class="card">
                        <div class="card-header">
                            <strong>{event['title']}</strong>
                            <span class="event-type">{event['event_type']}</span>
                        </div>
                        <div class="card-content">
                            <p>{format_date(str(event['start_date']))}</p>
                            <p>{event['description']}</p>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
                
                if not events:
                    st.info("No events scheduled for today")
        finally:
            conn.close()

def display_chores():
    """Display today's chores."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT task, assigned_to, completed
                    FROM chores
                    WHERE due_date = CURRENT_DATE
                    ORDER BY completed, task
                """)
                chores = cur.fetchall()
                
                st.markdown("""
                    <div class="card">
                        <div class="card-header">
                            <strong>Today's Chores</strong>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                for chore in chores:
                    status = "✅" if chore['completed'] else "⏳"
                    st.markdown(f"""
                        <div class="card">
                            <div class="card-content">
                                {status} {chore['task']} ({chore['assigned_to']})
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
        finally:
            conn.close()

def display_grocery_list():
    """Display current grocery list."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT item, quantity, unit, category
                    FROM grocery_items
                    WHERE purchased = FALSE
                    ORDER BY category, item
                """)
                items = cur.fetchall()
                
                st.markdown("""
                    <div class="card">
                        <div class="card-header">
                            <strong>Grocery List</strong>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                for item in items:
                    st.markdown(f"""
                        <div class="card">
                            <div class="card-content">
                                • {item['quantity']} {item['unit']} {item['item']}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
        finally:
            conn.close()

def display_meal_planner():
    """Display meal planner summary."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get today's meals
                cur.execute("""
                    SELECT mp.meal_type, r.name
                    FROM meal_plans mp
                    JOIN recipes r ON mp.recipe_id = r.recipe_id
                    WHERE mp.date = CURRENT_DATE
                    ORDER BY CASE mp.meal_type 
                        WHEN 'Breakfast' THEN 1 
                        WHEN 'Lunch' THEN 2 
                        WHEN 'Dinner' THEN 3 
                    END
                """)
                meals = cur.fetchall()
                
                st.markdown("""
                    <div class="card">
                        <div class="card-header">
                            <strong>Today's Meals</strong>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                for meal in meals:
                    st.markdown(f"""
                        <div class="card">
                            <div class="card-content">
                                {meal['meal_type']}: {meal['name']}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
        finally:
            conn.close()

def main():
    st.title("Family Organization System 🏠")
    
    # Daily meals section
    st.header("Today's Meals")
    col1, col2, col3 = st.columns(3)
    
    # Fetch today's meals
    todays_meals = get_todays_meals()
    meals_by_type = {meal['meal_type']: meal for meal in todays_meals}
    
    # Display meals in cards
    with col1:
        meal = meals_by_type.get('Breakfast')
        st.markdown(f'''
        <div class="meal-card">
            <h3>🌅 Breakfast</h3>
            {f"""
            <div class="meal-title">{meal['name']}</div>
            <div class="meal-description">{meal['description']}</div>
            """ if meal else "No meal planned"}
        </div>
        ''', unsafe_allow_html=True)
        
    with col2:
        meal = meals_by_type.get('Lunch')
        st.markdown(f'''
        <div class="meal-card">
            <h3>☀️ Lunch</h3>
            {f"""
            <div class="meal-title">{meal['name']}</div>
            <div class="meal-description">{meal['description']}</div>
            """ if meal else "No meal planned"}
        </div>
        ''', unsafe_allow_html=True)
        
    with col3:
        meal = meals_by_type.get('Dinner')
        st.markdown(f'''
        <div class="meal-card">
            <h3>🌙 Dinner</h3>
            {f"""
            <div class="meal-title">{meal['name']}</div>
            <div class="meal-description">{meal['description']}</div>
            """ if meal else "No meal planned"}
        </div>
        ''', unsafe_allow_html=True)
    
    # Initialize database
    init_db()
    
    # Display notifications
    display_notifications()
    
    # Calendar section
    st.subheader("Today's Schedule")
    with st.container():
        calendar_container = st.empty()
        with calendar_container:
            display_daily_calendar()
    
    # Quick action sections below
    col1, col2, col3 = st.columns(3)
    with col1:
        display_chores()
    with col2:
        display_grocery_list()
    with col3:
        display_meal_planner()

if __name__ == "__main__":
    main()
