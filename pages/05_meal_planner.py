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
                    st.rerun()
        except Exception as e:
            conn.rollback()
            st.error(f"Error adding sample recipes: {str(e)}")
        finally:
            conn.close()

def add_ingredients_to_grocery_list(recipe_id):
    """Add recipe ingredients to the grocery list with improved error handling."""
    conn = get_db_connection()
    if not conn:
        st.error("Could not connect to database")
        return
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get recipe name first
            cur.execute("SELECT name FROM recipes WHERE recipe_id = %s", (recipe_id,))
            recipe = cur.fetchone()
            if not recipe:
                st.error("Recipe not found")
                return
            
            # Get recipe ingredients
            cur.execute("""
                SELECT ingredient_name, quantity, unit 
                FROM recipe_ingredients 
                WHERE recipe_id = %s
            """, (recipe_id,))
            ingredients = cur.fetchall()
            
            if not ingredients:
                st.warning("No ingredients found for this recipe")
                return
            
            # Add each ingredient to grocery list
            added_count = 0
            updated_count = 0
            
            for ingredient in ingredients:
                # Check if ingredient already exists
                cur.execute("""
                    SELECT id, quantity 
                    FROM grocery_items 
                    WHERE item = %s AND purchased = FALSE
                """, (ingredient['ingredient_name'],))
                existing = cur.fetchone()
                
                if existing:
                    # Update existing item
                    cur.execute("""
                        UPDATE grocery_items 
                        SET quantity = quantity + %s 
                        WHERE id = %s
                    """, (ingredient['quantity'], existing['id']))
                    updated_count += 1
                else:
                    # Add new item
                    cur.execute("""
                        INSERT INTO grocery_items 
                        (item, quantity, unit, category, added_by) 
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        ingredient['ingredient_name'],
                        ingredient['quantity'],
                        ingredient['unit'],
                        'From Recipe',
                        f'Recipe: {recipe["name"]}'
                    ))
                    added_count += 1
            
            conn.commit()
            
            # Show success message with details
            if added_count > 0 or updated_count > 0:
                message = []
                if added_count > 0:
                    message.append(f"Added {added_count} new items")
                if updated_count > 0:
                    message.append(f"Updated {updated_count} existing items")
                st.success(" and ".join(message))
                st.rerun()
            else:
                st.info("No changes were made to the grocery list")
                
    except Exception as e:
        conn.rollback()
        st.error(f"Error managing grocery list: {str(e)}")
    finally:
        conn.close()

def display_weekly_meal_plan(selected_date):
    """Display the weekly meal plan with improved error handling and UI."""
    conn = get_db_connection()
    if not conn:
        st.error("Could not connect to database")
        return
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Calculate week range
            start_of_week = selected_date - timedelta(days=selected_date.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            
            # Fetch meal plans
            cur.execute("""
                SELECT 
                    mp.date,
                    mp.meal_type,
                    r.name as recipe_name,
                    r.description,
                    r.servings,
                    r.prep_time
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
            
            # Display week range
            st.markdown(f"""
                ### Week of {format_date(str(start_of_week))}
                <div class="date-range" style="color: #666; margin-bottom: 20px;">
                    {format_date(str(start_of_week))} - {format_date(str(end_of_week))}
                </div>
            """, unsafe_allow_html=True)
            
            # Group meals by date
            current_date = None
            meal_icons = {
                'Breakfast': '🍳',
                'Lunch': '🥪',
                'Dinner': '🍽️'
            }
            
            for plan in meal_plans:
                if plan['date'] != current_date:
                    st.markdown(f"""
                        <div style="
                            background-color: #f8f9fa;
                            padding: 10px;
                            border-radius: 5px;
                            margin-top: 20px;
                        ">
                            <h4>{format_date(str(plan['date']))}</h4>
                        </div>
                    """, unsafe_allow_html=True)
                    current_date = plan['date']
                
                st.markdown(f"""
                    <div style="
                        background-color: white;
                        padding: 15px;
                        border-radius: 8px;
                        margin: 10px 0;
                        border-left: 4px solid #FF4B4B;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    ">
                        <div style="display: flex; align-items: center;">
                            <span style="font-size: 1.5em; margin-right: 10px;">
                                {meal_icons.get(plan['meal_type'], '🍴')}
                            </span>
                            <div>
                                <strong>{plan['meal_type']}: {plan['recipe_name']}</strong>
                                <br>
                                <small>
                                    👥 Serves: {plan['servings']} | 
                                    ⏱️ Prep: {plan['prep_time']} mins
                                </small>
                                <p style="margin: 5px 0; color: #666;">
                                    {plan['description']}
                                </p>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            if not meal_plans:
                st.info("No meals planned for this week. Add some meals to get started!")
                
    except Exception as e:
        st.error(f"Error displaying meal plan: {str(e)}")
    finally:
        conn.close()

[Rest of the code remains the same...]
