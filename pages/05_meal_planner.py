import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.database import get_db_connection
from utils.helpers import configure_page, format_date
from psycopg2.extras import RealDictCursor

configure_page()

def validate_ingredient(name, quantity, unit):
    """Validate ingredient input."""
    if not name or not name.strip():
        return False, "Ingredient name is required"
    if quantity <= 0:
        return False, "Quantity must be greater than 0"
    if not unit:
        return False, "Unit is required"
    return True, ""

def add_ingredients_to_grocery_list(recipe_id, servings_multiplier=1):
    """Add recipe ingredients to grocery list with improved error handling."""
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
                        # Update quantity with proper error handling
                        try:
                            cur.execute("""
                                UPDATE grocery_items
                                SET quantity = quantity + %s
                                WHERE id = %s
                            """, (qty, existing['id']))
                        except Exception as e:
                            st.error(f"Error updating quantity for {ingredient['ingredient_name']}: {str(e)}")
                            continue
                    else:
                        # Add new item with proper error handling
                        try:
                            cur.execute("""
                                INSERT INTO grocery_items
                                (item, quantity, unit, category)
                                VALUES (%s, %s, %s, 'From Meal Plan')
                            """, (ingredient['ingredient_name'], qty, ingredient['unit']))
                        except Exception as e:
                            st.error(f"Error adding {ingredient['ingredient_name']}: {str(e)}")
                            continue
                
                conn.commit()
                st.success("Ingredients added to grocery list!")
        except Exception as e:
            st.error(f"Error managing ingredients: {str(e)}")
        finally:
            conn.close()

def main():
    st.title("Meal Planner 🍳")
    
    # Add new recipe form with improved validation
    with st.expander("Add New Recipe"):
        with st.form("new_recipe"):
            name = st.text_input("Recipe Name")
            description = st.text_area("Description")
            servings = st.number_input("Servings", min_value=1, value=4)
            prep_time = st.number_input("Prep Time (minutes)", min_value=1, value=30)
            instructions = st.text_area("Instructions")
            
            st.subheader("Ingredients")
            num_ingredients = st.number_input("Number of ingredients", min_value=1, value=3)
            ingredients = []
            
            for i in range(num_ingredients):
                st.markdown(f"""
                <div class="ingredient-form">
                    <div class="ingredient-header">Ingredient {i+1}</div>
                </div>
                """, unsafe_allow_html=True)
                
                cols = st.columns(4)
                with cols[0]:
                    ing_name = st.text_input("Name", key=f"ing_name_{i}")
                with cols[1]:
                    ing_qty = st.number_input("Quantity", min_value=0.0, step=0.1, key=f"ing_qty_{i}")
                with cols[2]:
                    ing_unit = st.selectbox(
                        "Unit",
                        ["g", "kg", "ml", "l", "cup", "tbsp", "tsp", "piece", "clove", "pinch"],
                        key=f"ing_unit_{i}"
                    )
                
                # Validate ingredient input
                valid, error_msg = validate_ingredient(ing_name, ing_qty, ing_unit)
                if not valid:
                    st.warning(error_msg)
                else:
                    ingredients.append((ing_name, ing_qty, ing_unit))
            
            if st.form_submit_button("Add Recipe"):
                if not name:
                    st.error("Recipe name is required")
                elif not ingredients:
                    st.error("At least one valid ingredient is required")
                else:
                    conn = get_db_connection()
                    if conn:
                        try:
                            with conn.cursor() as cur:
                                # Start transaction
                                cur.execute("BEGIN")
                                try:
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
                                    
                                    # Commit transaction
                                    conn.commit()
                                    st.success("Recipe added successfully!")
                                except Exception as e:
                                    # Rollback transaction on error
                                    conn.rollback()
                                    st.error(f"Error adding recipe: {str(e)}")
                        finally:
                            conn.close()
    
    # Rest of the meal planner functionality...
    # (Previous code for displaying recipes and meal plan remains the same)

if __name__ == "__main__":
    main()
