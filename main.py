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
