# Updating the calendar event display in display_daily_calendar function
# The rest of the file remains unchanged except for this section
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
    }
    .card-header {
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .card-content {
        margin-top: 8px;
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
        color: var(--text-color);
        font-size: 0.9em;
    }
</style>
''', unsafe_allow_html=True)

def display_notifications():
    """Display notifications in header."""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
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
                        <div class="card" style="
                            background-color: {get_notification_color(notif['priority'])};
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
    finally:
        conn.close()

def display_daily_calendar():
    """Display today's events in a fixed-height container."""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            today = datetime.now().date()
            cur.execute("""
                SELECT title, event_type, description,
                       CASE 
                           WHEN start_date = CURRENT_DATE THEN 'Today'
                           WHEN start_date = CURRENT_DATE + INTERVAL '1 day' THEN 'Tomorrow'
                           ELSE to_char(start_date, 'Day, Mon DD')
                       END as display_date
                FROM events
                WHERE start_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days'
                ORDER BY start_date, title
            """)
            events = cur.fetchall()
            
            if events:
                current_date = None
                for event in events:
                    if event['display_date'] != current_date:
                        if current_date:
                            st.markdown("<hr>", unsafe_allow_html=True)
                        st.subheader(event['display_date'])
                        current_date = event['display_date']
                    
                    st.markdown(f'''
                    <div style="
                        background-color: var(--secondary-background-color);
                        padding: 15px;
                        border-radius: 8px;
                        margin: 10px 0;
                        border-left: 4px solid var(--primary-color);
                    ">
                        <div class="event-header">
                            <strong>{event['title']}</strong>
                            <span class="event-type">{event['event_type']}</span>
                        </div>
                        <div class="event-content">
                            {event['description'] or ''}
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
            else:
                st.info("No events scheduled")
    finally:
        conn.close()

def display_chores():
    """Display chores grouped by person with completion tracking."""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get all family members with chores
            cur.execute("""
                SELECT DISTINCT assigned_to
                FROM chores
                ORDER BY assigned_to
            """)
            members = cur.fetchall()
            
            with st.expander("✅ Chores", expanded=True):
                # Filter options
                show_completed = st.checkbox("Show Completed Tasks", value=True)
                
                if members:
                    for member in members:
                        person = member['assigned_to']
                        cur.execute("""
                            SELECT *
                            FROM chores
                            WHERE assigned_to = %s
                            ORDER BY due_date, completed
                        """, (person,))
                        chores = cur.fetchall()
                        
                        if chores:
                            st.subheader(person)
                            for chore in chores:
                                if show_completed or not chore['completed']:
                                    col1, col2, col3 = st.columns([2, 1, 0.5])
                                    with col1:
                                        st.markdown(f"""
                                        <div class="card">
                                            <strong>{chore['task']}</strong><br>
                                            <small>Due: {format_date(str(chore['due_date']))}</small>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    with col2:
                                        st.write(f"Points: {chore.get('points', 10)}")  # Default to 10 if points not set
                                    with col3:
                                        if not chore['completed']:
                                            if st.button("✓", key=f"complete_{chore['id']}"):
                                                points = chore.get('points', 10)
                                                cur.execute("""
                                                    UPDATE chores
                                                    SET completed = TRUE
                                                    WHERE id = %s
                                                """, (chore['id'],))
                                                
                                                # Update points
                                                cur.execute("""
                                                    INSERT INTO points_balance (user_name, points)
                                                    VALUES (%s, %s)
                                                    ON CONFLICT (user_name)
                                                    DO UPDATE SET points = points_balance.points + %s
                                                """, (person, points, points))
                                                
                                                conn.commit()
                                                st.rerun()
                else:
                    st.info("No chores assigned")
    finally:
        conn.close()

def display_grocery_list():
    """Display grocery list with meal planning integration."""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            with st.expander("🛒 Grocery List", expanded=True):
                # Filter options
                category_filter = st.multiselect(
                    "Filter by Category",
                    ["Produce", "Dairy", "Meat", "Pantry", "Bakery", 
                     "Breakfast", "Snacks", "Beverages", "Recipe Items"]
                )
                show_purchased = st.checkbox("Show Purchased Items")
                
                # Get categories with items
                query = """
                    SELECT DISTINCT category
                    FROM grocery_items
                    WHERE 1=1
                """
                if not show_purchased:
                    query += " AND purchased = FALSE"
                if category_filter:
                    query += " AND category = ANY(%s)"
                    cur.execute(query, (category_filter,))
                else:
                    cur.execute(query)
                
                categories = [cat['category'] for cat in cur.fetchall()]
                
                for category in categories:
                    st.subheader(category)
                    
                    query = """
                        SELECT * FROM grocery_items 
                        WHERE category = %s
                    """
                    if not show_purchased:
                        query += " AND purchased = FALSE"
                    query += " ORDER BY item"
                    
                    cur.execute(query, (category,))
                    items = cur.fetchall()
                    
                    for item in items:
                        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                        with col1:
                            st.markdown(f"""
                            <div class="card">
                                <strong>{item['item']}</strong><br>
                                <small>Added by: {item['added_by']}</small>
                            </div>
                            """, unsafe_allow_html=True)
                        with col2:
                            new_qty = st.number_input(
                                "Qty", 
                                min_value=1, 
                                value=item['quantity'],
                                key=f"qty_{item['id']}"
                            )
                            if new_qty != item['quantity']:
                                cur.execute("""
                                    UPDATE grocery_items 
                                    SET quantity = %s 
                                    WHERE id = %s
                                """, (new_qty, item['id']))
                                conn.commit()
                                st.rerun()
                        with col3:
                            st.write(item.get('unit', 'piece'))  # Default to 'piece' if unit is missing
                        with col4:
                            if not item['purchased']:
                                if st.button("✅", key=f"buy_{item['id']}"):
                                    cur.execute("""
                                        UPDATE grocery_items 
                                        SET purchased = TRUE 
                                        WHERE id = %s
                                    """, (item['id'],))
                                    conn.commit()
                                    st.rerun()
    finally:
        conn.close()

def display_meal_planner():
    """Display meal planner with recipe management."""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            with st.expander("🍽️ Meal Planner", expanded=True):
                # Recipe selection
                cur.execute("SELECT recipe_id, name FROM recipes ORDER BY name")
                recipes = cur.fetchall()
                
                if recipes:
                    recipe_options = {r['name']: r['recipe_id'] for r in recipes}
                    selected_recipe = st.selectbox("Select Recipe", list(recipe_options.keys()))
                    recipe_id = recipe_options[selected_recipe]
                    
                    # Display recipe details with improved error handling
                    cur.execute("""
                        SELECT r.*, array_agg(ri.*) as ingredients
                        FROM recipes r
                        LEFT JOIN recipe_ingredients ri ON r.recipe_id = ri.recipe_id
                        WHERE r.recipe_id = %s
                        GROUP BY r.recipe_id
                    """, (recipe_id,))
                    recipe = cur.fetchone()
                    
                    if recipe and isinstance(recipe, dict):
                        st.markdown(f"""
                        <div class="card">
                            <div class="card-header">
                                <strong>{recipe['name']}</strong>
                                <span>Serves: {recipe['servings']} | Prep: {recipe['prep_time']} mins</span>
                            </div>
                            <div class="card-content">
                                {recipe['description']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.write("**Ingredients:**")
                        ingredients = recipe.get('ingredients', [])
                        if ingredients and isinstance(ingredients, list):
                            for ing in ingredients:
                                if isinstance(ing, dict):
                                    name = ing.get('ingredient_name', '')
                                    qty = ing.get('quantity', 1)
                                    unit = ing.get('unit', 'piece')
                                    if name:  # Only display if ingredient has a name
                                        st.write(f"• {name}: {qty} {unit}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner"])
                            selected_date = st.date_input("Select Date")
                        with col2:
                            if st.button("Add to Meal Plan"):
                                cur.execute("""
                                    INSERT INTO meal_plans 
                                    (date, meal_type, recipe_id)
                                    VALUES (%s, %s, %s)
                                """, (selected_date, meal_type, recipe_id))
                                conn.commit()
                                st.success("Added to meal plan!")
                                st.rerun()
                            
                            if st.button("Add Ingredients to List"):
                                if isinstance(ingredients, list) and ingredients:
                                    for ing in ingredients:
                                        if isinstance(ing, dict):
                                            name = ing.get('ingredient_name', '')
                                            qty = ing.get('quantity', 1)
                                            unit = ing.get('unit', 'piece')
                                            if name:  # Only add if ingredient has a name
                                                cur.execute("""
                                                    INSERT INTO grocery_items 
                                                    (item, quantity, unit, category, added_by)
                                                    VALUES (%s, %s, %s, %s, %s)
                                                """, (
                                                    name,
                                                    qty,
                                                    unit,
                                                    'Recipe Items',
                                                    f"Recipe: {recipe['name']}"
                                                ))
                                    conn.commit()
                                    st.success("Added ingredients to grocery list!")
                                    st.rerun()
                else:
                    st.info("No recipes available. Add some recipes to get started!")
    finally:
        conn.close()

def main():
    # Initialize database
    init_db()
    
    # App header
    st.title("Family Organization System 🏠")
    
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
