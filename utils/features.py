import streamlit as st
from datetime import datetime, timedelta
from utils.database import get_db_connection
import requests
from psycopg2.extras import RealDictCursor
import importlib

def display_calendar_widget():
    """Interactive calendar widget with event preview."""
    st.markdown("""
        <div class="calendar-widget card">
            <h3>📅 Calendar</h3>
            <div class="calendar-content">
    """, unsafe_allow_html=True)
    
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT title, description, start_date, event_type
                    FROM events
                    WHERE start_date >= CURRENT_DATE
                    ORDER BY start_date
                    LIMIT 5
                """)
                events = cur.fetchall()
                
                if events:
                    for event in events:
                        event_date = event['start_date']
                        date_str = "Today" if event_date == datetime.now().date() else event_date.strftime("%b %d")
                        
                        st.markdown(f"""
                            <div class="calendar-event">
                                <div class="event-date">{date_str}</div>
                                <div class="event-details">
                                    <div class="event-title">{event['title']}</div>
                                    <div class="event-type">{event['event_type']}</div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No upcoming events")
        finally:
            conn.close()
    
    st.markdown("</div></div>", unsafe_allow_html=True)

def display_weather_widget():
    """Weather information and forecasts."""
    st.markdown("""
        <div class="weather-widget card">
            <h3>🌤️ Weather</h3>
            <div class="weather-content">
                <div class="weather-current">
                    <div class="temp">72°F</div>
                    <div class="condition">Partly Cloudy</div>
                </div>
                <div class="weather-forecast">
                    <div class="forecast-item">
                        <div>Tomorrow</div>
                        <div>75°F</div>
                    </div>
                    <div class="forecast-item">
                        <div>Tuesday</div>
                        <div>70°F</div>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def display_family_status():
    """Family members' status and location."""
    st.markdown("""
        <div class="family-status card">
            <h3>👨‍👩‍👧‍👦 Family Status</h3>
            <div class="status-list">
                <div class="status-item">
                    <span class="status-name">Mom</span>
                    <span class="status-badge success">Home</span>
                </div>
                <div class="status-item">
                    <span class="status-name">Dad</span>
                    <span class="status-badge warning">Work</span>
                </div>
                <div class="status-item">
                    <span class="status-name">Emma</span>
                    <span class="status-badge">School</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def display_quick_notes():
    """Shared family notes and reminders."""
    st.markdown("""
        <div class="quick-notes card">
            <h3>📝 Quick Notes</h3>
            <div class="notes-list">
                <div class="note-item">
                    <div class="note-text">Pick up dry cleaning</div>
                    <div class="note-meta">Added by Mom</div>
                </div>
                <div class="note-item">
                    <div class="note-text">Soccer practice at 4 PM</div>
                    <div class="note-meta">Added by Dad</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def display_meal_planner():
    """Interactive meal planning calendar."""
    st.markdown("""
        <div class="meal-planner card">
            <h3>🍽️ Today's Meals</h3>
            <div class="meals-list">
    """, unsafe_allow_html=True)
    
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT mp.meal_type, r.name, r.description
                    FROM meal_plans mp
                    JOIN recipes r ON mp.recipe_id = r.recipe_id
                    WHERE mp.date = CURRENT_DATE
                    ORDER BY 
                        CASE mp.meal_type 
                            WHEN 'Breakfast' THEN 1
                            WHEN 'Lunch' THEN 2
                            WHEN 'Dinner' THEN 3
                        END
                """)
                meals = cur.fetchall()
                
                if meals:
                    for meal in meals:
                        st.markdown(f"""
                            <div class="meal-item">
                                <div class="meal-type">{meal['meal_type']}</div>
                                <div class="meal-name">{meal['name']}</div>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No meals planned for today")
        finally:
            conn.close()
    
    st.markdown("</div></div>", unsafe_allow_html=True)

def display_task_summary():
    """Overview of tasks and deadlines."""
    st.markdown("""
        <div class="task-summary card">
            <h3>✅ Task Summary</h3>
            <div class="tasks-overview">
    """, unsafe_allow_html=True)
    
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        COUNT(*) FILTER (WHERE priority = 'high') as high_priority,
                        COUNT(*) FILTER (WHERE priority = 'normal') as normal_priority,
                        COUNT(*) FILTER (WHERE priority = 'low') as low_priority
                    FROM todo_items
                    WHERE completed = FALSE
                """)
                task_counts = cur.fetchone()
                
                st.markdown(f"""
                    <div class="task-stats">
                        <div class="stat-item priority-high">
                            <div class="stat-value">{task_counts['high_priority']}</div>
                            <div class="stat-label">High Priority</div>
                        </div>
                        <div class="stat-item priority-normal">
                            <div class="stat-value">{task_counts['normal_priority']}</div>
                            <div class="stat-label">Normal Priority</div>
                        </div>
                        <div class="stat-item priority-low">
                            <div class="stat-value">{task_counts['low_priority']}</div>
                            <div class="stat-label">Low Priority</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        finally:
            conn.close()
    
    st.markdown("</div></div>", unsafe_allow_html=True)

def display_todo_list():
    """Display the todo list."""
    todo_list = importlib.import_module("pages.06_todo_list")
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, task, priority, due_date, created_at
                    FROM todo_items
                    WHERE completed = FALSE
                    ORDER BY 
                        CASE priority 
                            WHEN 'high' THEN 1 
                            WHEN 'normal' THEN 2 
                            WHEN 'low' THEN 3 
                        END,
                        due_date NULLS LAST,
                        created_at DESC
                """)
                todos = cur.fetchall()
                
                if todos:
                    st.markdown('<div class="todo-list">', unsafe_allow_html=True)
                    for todo in todos:
                        todo_list.display_todo_item(todo)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.info("No active tasks")
        finally:
            conn.close()

def display_shopping_view():
    """Display the shopping view."""
    st.subheader("Shopping List")
    # Add grocery list content here
    st.write("Shopping list content will go here")

def render_events_view():
    """Display the events view with school events as a sub-section."""
    st.subheader("Events")
    
    event_tabs = st.tabs(["General Events", "School Events"])
    
    with event_tabs[0]:
        display_calendar_widget()  # Assuming this function is defined in the same file
    
    with event_tabs[1]:
        school_events = importlib.import_module("pages.04_school_events")
        school_events.main()  # Ensure this is the correct way to call the main function of the school events page

def display_family_view():
    """Display the family view."""
    st.subheader("Family")
    col1, col2 = st.columns(2)
    with col1:
        display_family_status()  # Assuming this function is defined in the same file
    with col2:
        display_weather_widget()  # Assuming this function is defined in the same file
