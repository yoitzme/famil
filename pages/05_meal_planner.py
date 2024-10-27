import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.database import get_db_connection
from utils.helpers import configure_page, format_date
from psycopg2.extras import RealDictCursor

configure_page()

def add_sample_recipes():
    """Add sample recipes to the database."""
    sample_recipes = [
        ("Spaghetti Bolognese", "Classic Italian pasta dish", 4, 45,
         "1. Cook pasta\n2. Make sauce\n3. Combine and serve", [
            ("spaghetti", 500, "g"),
            ("ground beef", 400, "g"),
            ("tomato sauce", 2, "cups"),
            ("onion", 1, "piece"),
            ("garlic", 3, "cloves")
        ]),
        ("Chicken Stir Fry", "Quick and healthy dinner", 4, 30,
         "1. Cut chicken\n2. Prep vegetables\n3. Stir fry all ingredients", [
            ("chicken breast", 500, "g"),
            ("mixed vegetables", 400, "g"),
            ("soy sauce", 4, "tbsp"),
            ("rice", 2, "cups"),
            ("oil", 2, "tbsp")
        ]),
        ("Pancakes", "Fluffy breakfast favorite", 4, 20,
         "1. Mix ingredients\n2. Cook on griddle\n3. Serve with syrup", [
            ("flour", 2, "cups"),
            ("milk", 1.5, "cups"),
            ("eggs", 2, "piece"),
            ("butter", 50, "g"),
            ("maple syrup", 0.25, "cup")
        ])
    ]
    
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM recipes")
                count = cur.fetchone()[0]
                if count == 0:
                    for recipe in sample_recipes:
                        # Insert recipe
                        cur.execute("""
                            INSERT INTO recipes 
                            (name, description, servings, prep_time, instructions)
                            VALUES (%s, %s, %s, %s, %s)
                            RETURNING recipe_id
                        """, recipe[:-1])
                        recipe_id = cur.fetchone()[0]
                        
                        # Insert ingredients
                        for ingredient in recipe[-1]:
                            cur.execute("""
                                INSERT INTO recipe_ingredients
                                (recipe_id, ingredient_name, quantity, unit)
                                VALUES (%s, %s, %s, %s)
                            """, (recipe_id, ingredient[0], ingredient[1], ingredient[2]))
                    
                    conn.commit()
                    st.success("Sample recipes added successfully!")
        except Exception as e:
            st.error(f"Error adding sample recipes: {str(e)}")
        finally:
            conn.close()

def add_ingredients_to_grocery_list(recipe_id, servings_multiplier=1):
    """Add recipe ingredients to grocery list."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get recipe ingredients
                cur.execute("""
                    SELECT ingredient_name, quantity, unit
                    FROM recipe_ingredients
                    WHERE recipe_id = %s
                """, (recipe_id,))
                ingredients = cur.fetchall()
                
                # Add each ingredient to grocery list
                for ingredient in ingredients:
                    # Calculate adjusted quantity
                    qty = float(ingredient['quantity']) * servings_multiplier
                    
                    # Check if ingredient already exists
                    cur.execute("""
                        SELECT id, quantity
                        FROM grocery_items
                        WHERE item = %s AND purchased = FALSE
                    """, (ingredient['ingredient_name'],))
                    existing = cur.fetchone()
                    
                    if existing:
                        # Update quantity
                        cur.execute("""
                            UPDATE grocery_items
                            SET quantity = quantity + %s
                            WHERE id = %s
                        """, (qty, existing['id']))
                    else:
                        # Add new item
                        cur.execute("""
                            INSERT INTO grocery_items
                            (item, quantity, unit, category)
                            VALUES (%s, %s, %s, 'From Meal Plan')
                        """, (ingredient['ingredient_name'], qty, ingredient['unit']))
                
                conn.commit()
                st.success("Ingredients added to grocery list!")
        except Exception as e:
            st.error(f"Error adding ingredients: {str(e)}")
        finally:
            conn.close()

def display_recipe_details(recipe_id):
    """Display detailed recipe information."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get recipe details
                cur.execute("""
                    SELECT name, description, servings, prep_time, instructions
                    FROM recipes WHERE recipe_id = %s
                """, (recipe_id,))
                recipe = cur.fetchone()
                
                # Get ingredients
                cur.execute("""
                    SELECT ingredient_name, quantity, unit
                    FROM recipe_ingredients
                    WHERE recipe_id = %s
                """, (recipe_id,))
                ingredients = cur.fetchall()
                
                if recipe:
                    st.markdown(f"""
                    <div class="recipe-card">
                        <h3>{recipe['name']}</h3>
                        <p>{recipe['description']}</p>
                        <p><strong>Servings:</strong> {recipe['servings']}</p>
                        <p><strong>Prep Time:</strong> {recipe['prep_time']} minutes</p>
                        
                        <h4>Ingredients:</h4>
                        <ul>
                    """, unsafe_allow_html=True)
                    
                    for ing in ingredients:
                        st.markdown(f"""
                            <li>{ing['quantity']} {ing['unit']} {ing['ingredient_name']}</li>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("""</ul>""", unsafe_allow_html=True)
                    st.markdown(f"""
                        <h4>Instructions:</h4>
                        <pre>{recipe['instructions']}</pre>
                    """, unsafe_allow_html=True)
                    
                    # Add to grocery list button
                    servings = st.number_input("Servings to make:", min_value=1, value=recipe['servings'])
                    multiplier = servings / recipe['servings']
                    
                    if st.button("Add Ingredients to Grocery List"):
                        add_ingredients_to_grocery_list(recipe_id, multiplier)
        finally:
            conn.close()

def display_weekly_meal_plan(selected_date):
    """Display the weekly meal plan with recipe selection."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Calculate week range
                start_of_week = selected_date - timedelta(days=selected_date.weekday())
                end_of_week = start_of_week + timedelta(days=6)
                
                # Get all recipes for selection
                cur.execute("SELECT recipe_id, name FROM recipes ORDER BY name")
                recipes = cur.fetchall()
                recipe_options = {r['recipe_id']: r['name'] for r in recipes}
                recipe_options[0] = "Select a recipe..."
                
                # Display week range
                st.markdown(f"### Week of {format_date(str(start_of_week))}")
                
                # Create daily meal planners
                current_date = start_of_week
                while current_date <= end_of_week:
                    st.markdown(f"#### {format_date(str(current_date))}")
                    
                    # Get existing meal plans
                    cur.execute("""
                        SELECT meal_type, recipe_id, notes
                        FROM meal_plans
                        WHERE date = %s
                    """, (current_date,))
                    existing_meals = {m['meal_type']: m for m in cur.fetchall()}
                    
                    # Create columns for each meal type
                    cols = st.columns(3)
                    meal_types = ['Breakfast', 'Lunch', 'Dinner']
                    
                    for i, meal_type in enumerate(meal_types):
                        with cols[i]:
                            st.markdown(f"**{meal_type}**")
                            existing_meal = existing_meals.get(meal_type, {})
                            
                            # Recipe selector
                            current_recipe = existing_meal.get('recipe_id', 0)
                            recipe_id = st.selectbox(
                                f"Recipe for {meal_type}",
                                options=list(recipe_options.keys()),
                                format_func=lambda x: recipe_options[x],
                                key=f"{current_date}_{meal_type}",
                                index=list(recipe_options.keys()).index(current_recipe)
                            )
                            
                            # Notes field
                            notes = st.text_area(
                                "Notes",
                                value=existing_meal.get('notes', ''),
                                key=f"notes_{current_date}_{meal_type}"
                            )
                            
                            # Save button
                            if st.button("Save", key=f"save_{current_date}_{meal_type}"):
                                if recipe_id != 0:  # Only save if a recipe is selected
                                    if existing_meal:
                                        # Update existing plan
                                        cur.execute("""
                                            UPDATE meal_plans
                                            SET recipe_id = %s, notes = %s
                                            WHERE date = %s AND meal_type = %s
                                        """, (recipe_id, notes, current_date, meal_type))
                                    else:
                                        # Create new plan
                                        cur.execute("""
                                            INSERT INTO meal_plans
                                            (date, meal_type, recipe_id, notes)
                                            VALUES (%s, %s, %s, %s)
                                        """, (current_date, meal_type, recipe_id, notes))
                                    conn.commit()
                                    st.success(f"{meal_type} plan saved!")
                    
                    current_date += timedelta(days=1)
                    st.markdown("---")
                
        except Exception as e:
            st.error(f"Error managing meal plan: {str(e)}")
        finally:
            conn.close()

def main():
    st.title("Meal Planner 🍳")
    
    # Add sample data button
    if st.sidebar.button("Add Sample Recipes"):
        add_sample_recipes()
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["Weekly Meal Plan", "Recipes", "Grocery List"])
    
    with tab1:
        # Weekly meal planner
        selected_date = st.date_input(
            "Select week starting from:",
            datetime.now().date() - timedelta(days=datetime.now().weekday())
        )
        display_weekly_meal_plan(selected_date)
    
    with tab2:
        # Recipe management
        st.header("Recipes")
        
        # Add new recipe form
        with st.expander("Add New Recipe"):
            with st.form("new_recipe"):
                name = st.text_input("Recipe Name")
                description = st.text_area("Description")
                servings = st.number_input("Servings", min_value=1, value=4)
                prep_time = st.number_input("Prep Time (minutes)", min_value=1, value=30)
                instructions = st.text_area("Instructions")
                
                # Dynamic ingredient inputs
                st.subheader("Ingredients")
                num_ingredients = st.number_input("Number of ingredients", min_value=1, value=3)
                ingredients = []
                
                for i in range(num_ingredients):
                    cols = st.columns(4)
                    with cols[0]:
                        ing_name = st.text_input(f"Ingredient {i+1}", key=f"ing_name_{i}")
                    with cols[1]:
                        ing_qty = st.number_input(f"Quantity {i+1}", min_value=0.0, step=0.1, key=f"ing_qty_{i}")
                    with cols[2]:
                        ing_unit = st.selectbox(
                            f"Unit {i+1}",
                            ["g", "kg", "ml", "l", "cup", "tbsp", "tsp", "piece", "clove", "pinch"],
                            key=f"ing_unit_{i}"
                        )
                    ingredients.append((ing_name, ing_qty, ing_unit))
                
                if st.form_submit_button("Add Recipe"):
                    conn = get_db_connection()
                    if conn and name:
                        try:
                            with conn.cursor() as cur:
                                # Insert recipe
                                cur.execute("""
                                    INSERT INTO recipes 
                                    (name, description, servings, prep_time, instructions)
                                    VALUES (%s, %s, %s, %s, %s)
                                    RETURNING recipe_id
                                """, (name, description, servings, prep_time, instructions))
                                recipe_id = cur.fetchone()[0]
                                
                                # Insert ingredients
                                for ing in ingredients:
                                    if ing[0]:  # Only insert if ingredient name is provided
                                        cur.execute("""
                                            INSERT INTO recipe_ingredients
                                            (recipe_id, ingredient_name, quantity, unit)
                                            VALUES (%s, %s, %s, %s)
                                        """, (recipe_id, ing[0], ing[1], ing[2]))
                                
                                conn.commit()
                                st.success("Recipe added successfully!")
                        except Exception as e:
                            st.error(f"Error adding recipe: {str(e)}")
                        finally:
                            conn.close()
        
        # Display recipes
        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("SELECT recipe_id, name FROM recipes ORDER BY name")
                    recipes = cur.fetchall()
                    
                    # Recipe selector
                    selected_recipe = st.selectbox(
                        "Select a recipe to view details:",
                        options=[r['recipe_id'] for r in recipes],
                        format_func=lambda x: next(r['name'] for r in recipes if r['recipe_id'] == x)
                    )
                    
                    if selected_recipe:
                        display_recipe_details(selected_recipe)
                    
            finally:
                conn.close()
    
    with tab3:
        # Grocery list management
        st.header("Grocery List")
        
        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Add new item form
                    with st.expander("Add New Item"):
                        with st.form("new_item"):
                            item = st.text_input("Item Name")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                quantity = st.number_input("Quantity", min_value=0.1, step=0.1, value=1.0)
                            with col2:
                                unit = st.selectbox(
                                    "Unit",
                                    ["g", "kg", "ml", "l", "cup", "tbsp", "tsp", "piece", "clove", "pinch"]
                                )
                            with col3:
                                category = st.selectbox(
                                    "Category",
                                    ["Produce", "Dairy", "Meat", "Pantry", "Other"]
                                )
                            
                            if st.form_submit_button("Add Item"):
                                if item:
                                    cur.execute("""
                                        INSERT INTO grocery_items
                                        (item, quantity, unit, category)
                                        VALUES (%s, %s, %s, %s)
                                    """, (item, quantity, unit, category))
                                    conn.commit()
                                    st.success("Item added to grocery list!")
                    
                    # Display current list
                    cur.execute("""
                        SELECT id, item, quantity, unit, category, purchased
                        FROM grocery_items
                        ORDER BY category, item
                    """)
                    items = cur.fetchall()
                    
                    if items:
                        # Group by category
                        categories = {}
                        for item in items:
                            if not item['purchased']:
                                cat = item['category'] or 'Uncategorized'
                                if cat not in categories:
                                    categories[cat] = []
                                categories[cat].append(item)
                        
                        # Display items by category
                        for category, cat_items in categories.items():
                            st.subheader(category)
                            for item in cat_items:
                                cols = st.columns([3, 1, 1, 1])
                                with cols[0]:
                                    st.write(item['item'])
                                with cols[1]:
                                    st.write(f"{item['quantity']} {item['unit']}")
                                with cols[2]:
                                    if st.button("✅", key=f"buy_{item['id']}"):
                                        cur.execute("""
                                            UPDATE grocery_items
                                            SET purchased = TRUE
                                            WHERE id = %s
                                        """, (item['id'],))
                                        conn.commit()
                                        st.rerun()
                    else:
                        st.info("Your grocery list is empty!")
                    
            finally:
                conn.close()

if __name__ == "__main__":
    main()
