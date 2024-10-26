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
        border-left: 4px solid #FF4B4B;
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

def display_calendar_events():
    """Display calendar events in a card view."""
    conn = get_db_connection()
    if not conn:
        return
    
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
            
            with st.expander("📅 Upcoming Events", expanded=True):
                if events:
                    for event in events:
                        st.markdown(f"""
                        <div class="card">
                            <div class="card-header">
                                <strong>{event['title']}</strong>
                                <span>{format_date(str(event['start_date']))}</span>
                            </div>
                            <div class="card-content">
                                Type: {event['event_type']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No upcoming events")
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
                                        st.write(f"Points: {chore['points']}")
                                    with col3:
                                        if not chore['completed']:
                                            if st.button("✓", key=f"complete_{chore['id']}"):
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
                                                """, (person, chore['points'], chore['points']))
                                                
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
                    
                    # Display recipe details
                    cur.execute("""
                        SELECT r.*, array_agg(ri.*) as ingredients
                        FROM recipes r
                        LEFT JOIN recipe_ingredients ri ON r.recipe_id = ri.recipe_id
                        WHERE r.recipe_id = %s
                        GROUP BY r.recipe_id
                    """, (recipe_id,))
                    recipe = cur.fetchone()
                    
                    if recipe and 'ingredients' in recipe:
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
                        ingredients = recipe['ingredients']
                        if ingredients and isinstance(ingredients[0], dict):
                            for ing in ingredients:
                                st.write(f"• {ing.get('ingredient_name')}: {ing.get('quantity')} {ing.get('unit')}")
                        
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
                                # Add recipe ingredients to grocery list
                                for ing in ingredients:
                                    if isinstance(ing, dict):
                                        cur.execute("""
                                            INSERT INTO grocery_items 
                                            (item, quantity, unit, category, added_by)
                                            VALUES (%s, %s, %s, %s, %s)
                                        """, (
                                            ing.get('ingredient_name'),
                                            ing.get('quantity'),
                                            ing.get('unit', 'piece'),
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
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Home/Calendar",
        "Chores",
        "Grocery & Meal Planning",
        "School Events"
    ])
    
    with tab1:
        col1, col2, col3 = st.columns(3)
        with col1:
            display_calendar_events()
        with col2:
            # Add other home widgets
            pass
        with col3:
            # Add more home widgets
            pass
    
    with tab2:
        display_chores()
    
    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            display_grocery_list()
        with col2:
            display_meal_planner()
    
    with tab4:
        # School events section
        st.info("School events section will be implemented next")

if __name__ == "__main__":
    main()
