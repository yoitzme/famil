import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.database import get_db_connection
from utils.helpers import configure_page, format_date
from psycopg2.extras import RealDictCursor

configure_page()

def add_sample_groceries():
    """Add sample grocery items to the database."""
    sample_items = [
        ("Milk", 2, "Dairy", "liter", "Mom", False),
        ("Bread", 1, "Bakery", "loaf", "Dad", False),
        ("Apples", 6, "Produce", "pieces", "Mom", False),
        ("Chicken", 1, "Meat", "kg", "Dad", False),
        ("Cereal", 2, "Breakfast", "boxes", "Emma", False),
        ("Eggs", 1, "Dairy", "dozen", "Mom", False),
        ("Pasta", 2, "Pantry", "packs", "Sarah", False),
        ("Tomatoes", 4, "Produce", "pieces", "James", False),
    ]
    
    conn = get_db_connection()
    if not conn:
        st.error("Database connection failed")
        return

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT COUNT(*) as count FROM grocery_items")
            result = cur.fetchone()
            if result and result['count'] == 0:
                for item in sample_items:
                    cur.execute("""
                        INSERT INTO grocery_items 
                        (item, quantity, category, unit, added_by, purchased)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, item)
                conn.commit()
                st.success("Sample grocery items added successfully!")
                st.rerun()
    except Exception as e:
        conn.rollback()
        st.error(f"Error adding sample items: {str(e)}")
    finally:
        conn.close()

def add_sample_recipes():
    """Add sample recipes to the database."""
    sample_recipes = [
        ("Spaghetti Bolognese", "Classic Italian pasta dish", 4, 45, [
            ("spaghetti", 500, "grams"),
            ("ground beef", 400, "grams"),
            ("tomato sauce", 2, "cans"),
            ("onion", 1, "piece"),
            ("garlic", 3, "cloves")
        ]),
        ("Chicken Stir Fry", "Quick and healthy stir fry", 3, 30, [
            ("chicken breast", 500, "grams"),
            ("mixed vegetables", 400, "grams"),
            ("soy sauce", 60, "ml"),
            ("rice", 300, "grams"),
            ("ginger", 1, "piece")
        ])
    ]
    
    conn = get_db_connection()
    if not conn:
        st.error("Database connection failed")
        return

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT COUNT(*) as count FROM recipes")
            result = cur.fetchone()
            if result and result['count'] == 0:
                for recipe in sample_recipes:
                    # Insert recipe
                    cur.execute("""
                        INSERT INTO recipes 
                        (name, description, servings, prep_time)
                        VALUES (%s, %s, %s, %s)
                        RETURNING recipe_id
                    """, (recipe[0], recipe[1], recipe[2], recipe[3]))
                    result = cur.fetchone()
                    if not result:
                        raise Exception("Failed to insert recipe")
                    recipe_id = result['recipe_id']
                    
                    # Insert ingredients
                    for ingredient in recipe[4]:
                        cur.execute("""
                            INSERT INTO recipe_ingredients 
                            (recipe_id, ingredient_name, quantity, unit)
                            VALUES (%s, %s, %s, %s)
                        """, (recipe_id, ingredient[0], ingredient[1], ingredient[2]))
                conn.commit()
                st.success("Sample recipes added successfully!")
                st.rerun()
    except Exception as e:
        conn.rollback()
        st.error(f"Error adding sample recipes: {str(e)}")
    finally:
        conn.close()

def add_ingredients_to_grocery_list(recipe_id):
    """Add recipe ingredients to the grocery list."""
    conn = get_db_connection()
    if not conn:
        st.error("Database connection failed")
        return
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get recipe details
            cur.execute("""
                SELECT r.name, ri.* 
                FROM recipes r
                JOIN recipe_ingredients ri ON r.recipe_id = ri.recipe_id
                WHERE r.recipe_id = %s
            """, (recipe_id,))
            ingredients = cur.fetchall()
            
            if not ingredients:
                st.warning("No ingredients found for this recipe")
                return
            
            added = 0
            updated = 0
            for ing in ingredients:
                # Check if ingredient exists
                cur.execute("""
                    SELECT id, quantity, unit
                    FROM grocery_items 
                    WHERE item = %s AND purchased = FALSE
                """, (ing['ingredient_name'],))
                existing = cur.fetchone()
                
                if existing:
                    # Update quantity if units match
                    if existing['unit'] == ing['unit']:
                        cur.execute("""
                            UPDATE grocery_items 
                            SET quantity = quantity + %s 
                            WHERE id = %s
                        """, (ing['quantity'], existing['id']))
                        updated += 1
                    else:
                        # Add as new item if units don't match
                        cur.execute("""
                            INSERT INTO grocery_items 
                            (item, quantity, unit, category, added_by)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (
                            ing['ingredient_name'],
                            ing['quantity'],
                            ing['unit'],
                            'Recipe Items',
                            f"Recipe: {ing['name']}"
                        ))
                        added += 1
                else:
                    # Add new item
                    cur.execute("""
                        INSERT INTO grocery_items 
                        (item, quantity, unit, category, added_by)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        ing['ingredient_name'],
                        ing['quantity'],
                        ing['unit'],
                        'Recipe Items',
                        f"Recipe: {ing['name']}"
                    ))
                    added += 1
            
            conn.commit()
            if added or updated:
                st.success(f"Added {added} new items and updated {updated} existing items")
                st.rerun()
    except Exception as e:
        conn.rollback()
        st.error(f"Error updating grocery list: {str(e)}")
    finally:
        conn.close()

def display_weekly_meal_plan():
    """Display the weekly meal plan."""
    conn = get_db_connection()
    if not conn:
        st.error("Database connection failed")
        return
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            today = datetime.now().date()
            week_start = today - timedelta(days=today.weekday())
            week_end = week_start + timedelta(days=6)
            
            cur.execute("""
                SELECT mp.date, mp.meal_type, r.name as recipe_name,
                       r.description, r.servings, r.prep_time
                FROM meal_plans mp
                JOIN recipes r ON mp.recipe_id = r.recipe_id
                WHERE mp.date BETWEEN %s AND %s
                ORDER BY mp.date, 
                    CASE mp.meal_type 
                        WHEN 'Breakfast' THEN 1 
                        WHEN 'Lunch' THEN 2 
                        WHEN 'Dinner' THEN 3 
                    END
            """, (week_start, week_end))
            
            meals = cur.fetchall()
            
            if meals:
                current_date = None
                for meal in meals:
                    if meal['date'] != current_date:
                        st.write(f"### {format_date(str(meal['date']))}")
                        current_date = meal['date']
                    
                    st.markdown(f"""
                    <div style="
                        background-color: var(--secondary-background-color);
                        padding: 10px;
                        border-radius: 5px;
                        margin: 5px 0;
                    ">
                        <strong>{meal['meal_type']}</strong>: {meal['recipe_name']}
                        <br>
                        <small>
                            Serves: {meal['servings']} | 
                            Prep time: {meal['prep_time']} mins
                        </small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No meals planned for this week")
    except Exception as e:
        st.error(f"Error displaying meal plan: {str(e)}")
    finally:
        conn.close()

def main():
    st.title("Grocery & Meal Planning 🛒")
    
    # Add sample data options in header
    with st.expander("📚 Sample Data Options"):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Add Sample Groceries"):
                add_sample_groceries()
        with col2:
            if st.button("Add Sample Recipes"):
                add_sample_recipes()
    
    # Tabs for different sections
    tab1, tab2, tab3 = st.tabs(["📋 Grocery List", "🍽️ Meal Planner", "📅 Weekly Plan"])
    
    # Grocery List Tab
    with tab1:
        with st.expander("Add New Items"):
            with st.form("new_items"):
                items_input = st.text_area(
                    "Add Multiple Items (one per line)",
                    placeholder="Milk\nBread\nEggs"
                )
                col1, col2, col3 = st.columns(3)
                with col1:
                    category = st.selectbox("Category", 
                        ["Produce", "Dairy", "Meat", "Pantry", "Bakery", 
                         "Breakfast", "Snacks", "Beverages"])
                with col2:
                    unit = st.selectbox("Unit",
                        ["pieces", "kg", "grams", "liters", "ml", "packs", "cans"])
                with col3:
                    added_by = st.selectbox("Added By", 
                        ["Mom", "Dad", "Emma", "James", "Sarah"])
                
                if st.form_submit_button("Add Items"):
                    items_list = [item.strip() for item in items_input.split("\n") if item.strip()]
                    if items_list:
                        conn = get_db_connection()
                        if conn:
                            try:
                                with conn.cursor() as cur:
                                    for item in items_list:
                                        cur.execute("""
                                            INSERT INTO grocery_items 
                                            (item, quantity, unit, category, added_by)
                                            VALUES (%s, %s, %s, %s, %s)
                                        """, (item, 1, unit, category, added_by))
                                conn.commit()
                                st.success("Items added successfully!")
                                st.rerun()
                            except Exception as e:
                                conn.rollback()
                                st.error(f"Error adding items: {str(e)}")
                            finally:
                                conn.close()
        
        # Filter options in collapsible section
        with st.expander("🔍 Filter Options"):
            category_filter = st.multiselect(
                "Filter by Category",
                ["Produce", "Dairy", "Meat", "Pantry", "Bakery", 
                 "Breakfast", "Snacks", "Beverages", "Recipe Items"]
            )
            show_purchased = st.checkbox("Show Purchased Items")
        
        # Display grocery list
        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
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
                        
                        # Get items in category
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
                                st.write(f"• {item['item']}")
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
                                st.write(item['unit'])
                            with col4:
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
    
    # Meal Planner Tab
    with tab2:
        with st.expander("Add New Recipe"):
            with st.form("new_recipe"):
                recipe_name = st.text_input("Recipe Name")
                col1, col2 = st.columns(2)
                with col1:
                    servings = st.number_input("Servings", min_value=1, value=4)
                    description = st.text_area("Description")
                with col2:
                    prep_time = st.number_input("Prep Time (minutes)", min_value=5, value=30)
                
                st.subheader("Ingredients")
                ingredients = []
                for i in range(5):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        ingredient = st.text_input(f"Ingredient {i+1}", key=f"ing_{i}")
                    with col2:
                        quantity = st.number_input(f"Quantity {i+1}", min_value=0.0, key=f"qty_{i}")
                    with col3:
                        unit = st.selectbox(f"Unit {i+1}", 
                            ["grams", "ml", "pieces", "cups", "tablespoons", "teaspoons"],
                            key=f"unit_{i}")
                    if ingredient:
                        ingredients.append((ingredient, quantity, unit))
                
                if st.form_submit_button("Add Recipe"):
                    if recipe_name and ingredients:
                        conn = get_db_connection()
                        if conn:
                            try:
                                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                                    cur.execute("""
                                        INSERT INTO recipes 
                                        (name, description, servings, prep_time)
                                        VALUES (%s, %s, %s, %s)
                                        RETURNING recipe_id
                                    """, (recipe_name, description, servings, prep_time))
                                    
                                    result = cur.fetchone()
                                    if not result:
                                        raise Exception("Failed to insert recipe")
                                    recipe_id = result['recipe_id']
                                    
                                    for ing in ingredients:
                                        if ing[0]:  # if ingredient name is not empty
                                            cur.execute("""
                                                INSERT INTO recipe_ingredients 
                                                (recipe_id, ingredient_name, quantity, unit)
                                                VALUES (%s, %s, %s, %s)
                                            """, (recipe_id, ing[0], ing[1], ing[2]))
                                    conn.commit()
                                    st.success("Recipe added successfully!")
                                    st.rerun()
                            except Exception as e:
                                conn.rollback()
                                st.error(f"Error adding recipe: {str(e)}")
                            finally:
                                conn.close()
        
        # Plan meals
        st.subheader("Plan Meals")
        col1, col2 = st.columns(2)
        with col1:
            selected_date = st.date_input("Select Date")
        with col2:
            meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner"])
        
        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT recipe_id, name 
                        FROM recipes 
                        ORDER BY name
                    """)
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
                        
                        if recipe:
                            st.write(f"**Servings:** {recipe['servings']}")
                            st.write(f"**Prep Time:** {recipe['prep_time']} minutes")
                            st.write(f"**Description:** {recipe['description']}")
                            
                            st.write("**Ingredients:**")
                            ingredients = recipe['ingredients']
                            if ingredients and ingredients[0] is not None:
                                for ing in ingredients:
                                    st.write(f"• {ing['ingredient_name']}: {ing['quantity']} {ing['unit']}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Add to Meal Plan"):
                                try:
                                    cur.execute("""
                                        INSERT INTO meal_plans 
                                        (date, meal_type, recipe_id)
                                        VALUES (%s, %s, %s)
                                    """, (selected_date, meal_type, recipe_id))
                                    conn.commit()
                                    st.success("Added to meal plan!")
                                    st.rerun()
                                except Exception as e:
                                    conn.rollback()
                                    st.error(f"Error adding to meal plan: {str(e)}")
                        
                        with col2:
                            if st.button("Add Ingredients to Grocery List"):
                                add_ingredients_to_grocery_list(recipe_id)
            finally:
                conn.close()
    
    # Weekly Plan Tab
    with tab3:
        display_weekly_meal_plan()

if __name__ == "__main__":
    main()
