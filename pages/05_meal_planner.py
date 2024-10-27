import streamlit as st
from datetime import datetime, timedelta
from utils.database import get_db_connection
from utils.helpers import configure_page, format_date
from psycopg2.extras import RealDictCursor

configure_page()

def get_existing_meal(date, meal_type):
    """Get existing meal plan for a specific date and meal type."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT recipe_id, notes
                    FROM meal_plans
                    WHERE date = %s AND meal_type = %s
                """, (date, meal_type))
                return cur.fetchone() or {}
        finally:
            conn.close()
    return {}

def save_meal_plan(date, meal_type, recipe_id, notes):
    """Save or update a meal plan."""
    if recipe_id == 0:
        st.warning("Please select a recipe first")
        return
        
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                existing = get_existing_meal(date, meal_type)
                if existing:
                    cur.execute("""
                        UPDATE meal_plans
                        SET recipe_id = %s, notes = %s
                        WHERE date = %s AND meal_type = %s
                    """, (recipe_id, notes, date, meal_type))
                else:
                    cur.execute("""
                        INSERT INTO meal_plans
                        (date, meal_type, recipe_id, notes)
                        VALUES (%s, %s, %s, %s)
                    """, (date, meal_type, recipe_id, notes))
                conn.commit()
                st.success(f"{meal_type} plan saved!")
        except Exception as e:
            st.error(f"Error saving meal plan: {str(e)}")
        finally:
            conn.close()

def display_recipe_preview(recipe_id):
    """Display a preview of the recipe details."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get recipe details
                cur.execute("""
                    SELECT name, description, servings, prep_time
                    FROM recipes WHERE recipe_id = %s
                """, (recipe_id,))
                recipe = cur.fetchone()
                
                if recipe:
                    st.markdown(f"""
                    #### {recipe['name']}
                    {recipe['description']}
                    
                    **Servings:** {recipe['servings']}  
                    **Prep Time:** {recipe['prep_time']} minutes
                    """)
                    
                    # Get ingredients preview
                    cur.execute("""
                        SELECT ingredient_name, quantity, unit
                        FROM recipe_ingredients
                        WHERE recipe_id = %s
                        LIMIT 3
                    """, (recipe_id,))
                    ingredients = cur.fetchall()
                    
                    if ingredients:
                        st.markdown("#### Key Ingredients:")
                        for ing in ingredients:
                            st.markdown(f"• {ing['quantity']} {ing['unit']} {ing['ingredient_name']}")
                        
                        # Add to grocery list button
                        servings = st.number_input("Servings to make:", min_value=1, value=recipe['servings'])
                        if st.button("Add ingredients to grocery list"):
                            add_ingredients_to_grocery_list(recipe_id, servings / recipe['servings'])
        finally:
            conn.close()

def display_meal_plan(date, meal_type, recipe_options):
    """Display meal plan for a specific meal type."""
    existing_meal = get_existing_meal(date, meal_type)
    
    recipe_id = st.selectbox(
        "Select Recipe",
        options=list(recipe_options.keys()),
        format_func=lambda x: recipe_options[x],
        key=f"{date}_{meal_type}",
        index=list(recipe_options.keys()).index(existing_meal.get('recipe_id', 0))
    )
    
    notes = st.text_area(
        "Notes",
        value=existing_meal.get('notes', ''),
        key=f"notes_{date}_{meal_type}",
        height=100
    )
    
    if recipe_id != 0:
        with st.expander("Recipe Details", expanded=True):  # Changed to True
            display_recipe_preview(recipe_id)
    
    if st.button("Save", key=f"save_{date}_{meal_type}"):
        save_meal_plan(date, meal_type, recipe_id, notes)

def add_ingredients_to_grocery_list(recipe_id, servings_multiplier=1):
    """Add recipe ingredients to grocery list."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT ingredient_name, quantity, unit
                    FROM recipe_ingredients
                    WHERE recipe_id = %s
                """, (recipe_id,))
                ingredients = cur.fetchall()
                
                for ingredient in ingredients:
                    qty = float(ingredient['quantity']) * servings_multiplier
                    
                    cur.execute("""
                        SELECT id, quantity
                        FROM grocery_items
                        WHERE item = %s AND purchased = FALSE
                    """, (ingredient['ingredient_name'],))
                    existing = cur.fetchone()
                    
                    if existing:
                        cur.execute("""
                            UPDATE grocery_items
                            SET quantity = quantity + %s
                            WHERE id = %s
                        """, (qty, existing['id']))
                    else:
                        cur.execute("""
                            INSERT INTO grocery_items
                            (item, quantity, unit, category)
                            VALUES (%s, %s, %s, 'From Meal Plan')
                        """, (ingredient['ingredient_name'], qty, ingredient['unit']))
                
                conn.commit()
                st.success("Ingredients added to grocery list!")
        except Exception as e:
            st.error(f"Error managing ingredients: {str(e)}")
        finally:
            conn.close()

def main():
    st.title("Meal Planner 🍳")
    
    # Initialize session state
    if 'num_ingredients' not in st.session_state:
        st.session_state.num_ingredients = 3
    
    # Add new recipe section
    with st.expander("Add New Recipe"):
        name = st.text_input("Recipe Name")
        description = st.text_area("Description")
        servings = st.number_input("Servings", min_value=1, value=4)
        prep_time = st.number_input("Prep Time (minutes)", min_value=1, value=30)
        instructions = st.text_area("Instructions")
        
        # Dynamic ingredient inputs with visual feedback
        col1, col2 = st.columns(2)
        with col1:
            if st.button('➕ Add Ingredient', key='add_ing'):
                st.session_state.num_ingredients += 1
                st.rerun()
        with col2:
            if st.button('➖ Remove Ingredient', key='remove_ing') and st.session_state.num_ingredients > 1:
                st.session_state.num_ingredients -= 1
                st.rerun()
        
        ingredients = []
        for i in range(st.session_state.num_ingredients):
            with st.container():
                st.markdown(f"### Ingredient {i+1}")
                cols = st.columns(3)
                with cols[0]:
                    name_i = st.text_input(f"Name", key=f"name_{i}")
                with cols[1]:
                    qty_i = st.number_input(
                        f"Quantity",
                        min_value=0.1,
                        value=1.0,
                        step=0.1,
                        key=f"qty_{i}"
                    )
                with cols[2]:
                    unit_i = st.selectbox(
                        f"Unit",
                        ["g", "kg", "ml", "l", "cup", "tbsp", "tsp", "piece"],
                        key=f"unit_{i}"
                    )
                
                if name_i and qty_i > 0:
                    ingredients.append((name_i, qty_i, unit_i))
        
        if st.button("Save Recipe"):
            if not name:
                st.error("Recipe name is required")
            elif not ingredients:
                st.error("At least one ingredient is required")
            else:
                conn = get_db_connection()
                if conn:
                    try:
                        with conn.cursor() as cur:
                            cur.execute("BEGIN")
                            try:
                                # Insert recipe
                                cur.execute("""
                                    INSERT INTO recipes 
                                    (name, description, servings, prep_time, instructions)
                                    VALUES (%s, %s, %s, %s, %s)
                                    RETURNING recipe_id
                                """, (name, description, servings, prep_time, instructions))
                                result = cur.fetchone()
                                if result:
                                    recipe_id = result[0]
                                    
                                    # Insert ingredients
                                    for ing in ingredients:
                                        cur.execute("""
                                            INSERT INTO recipe_ingredients
                                            (recipe_id, ingredient_name, quantity, unit)
                                            VALUES (%s, %s, %s, %s)
                                        """, (recipe_id, ing[0], ing[1], ing[2]))
                                    
                                    conn.commit()
                                    st.success("Recipe added successfully!")
                                    st.session_state.num_ingredients = 3  # Reset ingredient count
                            except Exception as e:
                                conn.rollback()
                                st.error(f"Error adding recipe: {str(e)}")
                    finally:
                        conn.close()
    
    # Meal Planning section
    st.header("Meal Planning")
    date = st.date_input("Select date", datetime.now())
    
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get all recipes for selection
                cur.execute("SELECT recipe_id, name FROM recipes ORDER BY name")
                recipes = cur.fetchall()
                recipe_options = {r['recipe_id']: r['name'] for r in recipes}
                recipe_options[0] = "Select a recipe..."
                
                # Display meal types side by side
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.subheader("🌅 Breakfast")
                    display_meal_plan(date, "Breakfast", recipe_options)
                with col2:
                    st.subheader("☀️ Lunch")
                    display_meal_plan(date, "Lunch", recipe_options)
                with col3:
                    st.subheader("🌙 Dinner")
                    display_meal_plan(date, "Dinner", recipe_options)
        finally:
            conn.close()

if __name__ == "__main__":
    main()
