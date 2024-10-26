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
        ]),
        ("Vegetable Soup", "Hearty vegetable soup", 6, 60, [
            ("carrots", 3, "pieces"),
            ("celery", 4, "stalks"),
            ("potatoes", 2, "pieces"),
            ("vegetable broth", 2, "liters"),
            ("onion", 1, "piece")
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
                            (name, description, servings, prep_time)
                            VALUES (%s, %s, %s, %s)
                            RETURNING recipe_id
                        """, (recipe[0], recipe[1], recipe[2], recipe[3]))
                        recipe_id = cur.fetchone()[0]
                        
                        # Insert ingredients
                        for ingredient in recipe[4]:
                            cur.execute("""
                                INSERT INTO recipe_ingredients 
                                (recipe_id, ingredient_name, quantity, unit)
                                VALUES (%s, %s, %s, %s)
                            """, (recipe_id, ingredient[0], ingredient[1], ingredient[2]))
                    conn.commit()
                    st.success("Sample recipes added successfully!")
        except Exception as e:
            conn.rollback()
            st.error(f"Error adding sample recipes: {type(e).__name__}")
        finally:
            conn.close()

def add_ingredients_to_grocery_list(recipe_id):
    """Add recipe ingredients to the grocery list."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get recipe ingredients
                cur.execute(
                    "SELECT ingredient_name, quantity, unit FROM recipe_ingredients WHERE recipe_id = %s",
                    (recipe_id,)
                )
                ingredients = cur.fetchall()
                
                # Add each ingredient to grocery list
                for ingredient in ingredients:
                    # Check if ingredient exists using correct column names
                    cur.execute(
                        "SELECT id, quantity FROM grocery_items WHERE item = %s AND purchased = FALSE",
                        (ingredient['ingredient_name'],)
                    )
                    existing = cur.fetchone()
                    
                    if existing:
                        cur.execute(
                            "UPDATE grocery_items SET quantity = quantity + %s WHERE id = %s",
                            (ingredient['quantity'], existing['id'])
                        )
                    else:
                        cur.execute(
                            "INSERT INTO grocery_items (item, quantity, unit, category, added_by) VALUES (%s, %s, %s, 'From Recipe', 'Meal Planner')",
                            (ingredient['ingredient_name'], ingredient['quantity'], ingredient['unit'])
                        )
                conn.commit()
                st.success("Ingredients added to grocery list!")
        except Exception as e:
            conn.rollback()
            st.error(f"Error adding ingredients: {type(e).__name__}")
        finally:
            conn.close()

def get_recipe_details(recipe_id):
    """Get recipe details including ingredients."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get recipe info
                cur.execute("SELECT * FROM recipes WHERE recipe_id = %s", (recipe_id,))
                recipe = cur.fetchone()
                
                if recipe:
                    # Get ingredients
                    cur.execute("SELECT * FROM recipe_ingredients WHERE recipe_id = %s", (recipe_id,))
                    ingredients = cur.fetchall()
                    return recipe, ingredients
                return None, None
        except Exception as e:
            st.error(f"Error getting recipe details: {type(e).__name__}")
            return None, None
        finally:
            conn.close()
    return None, None

def display_weekly_meal_plan(conn, selected_date):
    """Display the weekly meal plan with error handling."""
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            start_of_week = selected_date - timedelta(days=selected_date.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            
            cur.execute("""
                SELECT mp.date, mp.meal_type, r.name, r.description
                FROM meal_plans mp
                JOIN recipes r ON mp.recipe_id = r.recipe_id
                WHERE mp.date BETWEEN %s AND %s
                ORDER BY mp.date, 
                    CASE mp.meal_type 
                        WHEN 'Breakfast' THEN 1 
                        WHEN 'Lunch' THEN 2 
                        WHEN 'Dinner' THEN 3 
                    END
            """, (start_of_week, end_of_week))
            
            meal_plans = cur.fetchall()
            current_date = None
            
            for plan in meal_plans:
                if plan['date'] != current_date:
                    st.write(f"### {format_date(str(plan['date']))}")
                    current_date = plan['date']
                
                st.markdown(f"""
                <div style="
                    background-color: #f0f2f6;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 10px 0;
                    border: 1px solid #e1e4e8;
                ">
                    <strong>{plan['meal_type']}:</strong> {plan['name']}
                    <br>
                    <small>{plan['description']}</small>
                </div>
                """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error displaying meal plan: {type(e).__name__}")

def main():
    st.title("Meal Planner 🍽️")
    
    # Add sample data button
    if st.sidebar.button("Add Sample Recipes"):
        add_sample_recipes()
    
    # Add new recipe form
    with st.expander("Add New Recipe"):
        with st.form("new_recipe"):
            recipe_name = st.text_input("Recipe Name")
            col1, col2 = st.columns(2)
            with col1:
                servings = st.number_input("Servings", min_value=1, value=4)
                description = st.text_area("Description")
            with col2:
                prep_time = st.number_input("Prep Time (minutes)", min_value=5, value=30)
            
            # Dynamic ingredient inputs
            st.subheader("Ingredients")
            ingredients = []
            for i in range(5):  # Start with 5 ingredient fields
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
                            with conn.cursor() as cur:
                                # Insert recipe
                                cur.execute("""
                                    INSERT INTO recipes 
                                    (name, description, servings, prep_time)
                                    VALUES (%s, %s, %s, %s)
                                    RETURNING recipe_id
                                """, (recipe_name, description, servings, prep_time))
                                recipe_id = cur.fetchone()[0]
                                
                                # Insert ingredients
                                for ing in ingredients:
                                    if ing[0]:  # if ingredient name is not empty
                                        cur.execute("""
                                            INSERT INTO recipe_ingredients 
                                            (recipe_id, ingredient_name, quantity, unit)
                                            VALUES (%s, %s, %s, %s)
                                        """, (recipe_id, ing[0], ing[1], ing[2]))
                                conn.commit()
                                st.success("Recipe added successfully!")
                        except Exception as e:
                            conn.rollback()
                            st.error(f"Error adding recipe: {type(e).__name__}")
                        finally:
                            conn.close()
    
    # Meal Planning Calendar
    st.subheader("Meal Planning Calendar")
    col1, col2 = st.columns(2)
    with col1:
        selected_date = st.date_input("Select Date")
    with col2:
        meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner"])
    
    # Get available recipes
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT recipe_id, name FROM recipes ORDER BY name")
                recipes = cur.fetchall()
                
                if recipes:
                    recipe_options = {recipe['name']: recipe['recipe_id'] for recipe in recipes}
                    selected_recipe = st.selectbox("Select Recipe", list(recipe_options.keys()))
                    recipe_id = recipe_options[selected_recipe]
                    
                    # Display recipe details
                    recipe, ingredients = get_recipe_details(recipe_id)
                    if recipe:
                        st.write(f"**Servings:** {recipe['servings']}")
                        st.write(f"**Prep Time:** {recipe['prep_time']} minutes")
                        st.write(f"**Description:** {recipe['description']}")
                        
                        st.write("**Ingredients:**")
                        for ing in ingredients:
                            st.write(f"• {ing['ingredient_name']}: {ing['quantity']} {ing['unit']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Add to Meal Plan"):
                            try:
                                with conn.cursor() as cur:
                                    # First, add to meal plans
                                    cur.execute("""
                                        INSERT INTO meal_plans 
                                        (date, meal_type, recipe_id)
                                        VALUES (%s, %s, %s)
                                    """, (selected_date, meal_type, recipe_id))
                                    
                                    # Then, add to events table
                                    cur.execute(
                                        "INSERT INTO events (title, description, start_date, end_date, event_type) VALUES (%s, %s, %s, %s, %s)",
                                        (f"{meal_type}: {selected_recipe}", recipe['description'], selected_date, selected_date, 'Meal')
                                    )
                                conn.commit()
                                st.success("Added to meal plan and calendar!")
                            except Exception as e:
                                conn.rollback()
                                st.error(f"Error adding to meal plan: {type(e).__name__}")
                    
                    with col2:
                        if st.button("Add Ingredients to Grocery List"):
                            add_ingredients_to_grocery_list(recipe_id)
                
                # Display weekly meal plan
                st.subheader("Weekly Meal Plan")
                display_weekly_meal_plan(conn, selected_date)
                
        except Exception as e:
            st.error(f"Error in meal planner: {type(e).__name__}")
        finally:
            conn.close()

if __name__ == "__main__":
    main()
