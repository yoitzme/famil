import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.database import get_db_connection
from utils.helpers import configure_page, format_date
from psycopg2.extras import RealDictCursor

configure_page()

[Previous functions remain unchanged]

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
            
            # Fetch meal plans with recipe details
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
            st.markdown(f"### Week of {format_date(str(start_of_week))}")
            
            # Display each meal plan
            for plan in meal_plans:
                if isinstance(plan, dict):  # Add type check
                    st.markdown(f'''
                        <div style="
                            background-color: var(--secondary-background-color);
                            color: #FFFFFF;  /* Ensure text is white */
                            padding: 15px;
                            border-radius: 8px;
                            margin: 10px 0;
                            border-left: 4px solid var(--primary-color);
                        ">
                            <strong>{plan.get('meal_type', '')}: {plan.get('recipe_name', '')}</strong>
                            <br>
                            <small>{plan.get('description', '')}</small>
                        </div>
                    ''', unsafe_allow_html=True)
            
            if not meal_plans:
                st.info("No meals planned for this week")
                
    except Exception as e:
        st.error(f"Error displaying meal plan: {str(e)}")
    finally:
        conn.close()

def display_recipe_ingredients(recipe):
    """Display recipe ingredients with improved error handling."""
    if recipe and isinstance(recipe, dict):
        ingredients = recipe.get('ingredients', [])
        if ingredients and isinstance(ingredients[0], dict):
            for ing in ingredients[0]:  # Access first element of ingredients array
                name = ing.get('ingredient_name', '')
                qty = ing.get('quantity', 1)
                unit = ing.get('unit', 'piece')
                if name:
                    st.write(f"• {name}: {qty} {unit}")

[Rest of the meal planner code remains unchanged]
