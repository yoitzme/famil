import streamlit as st
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
                
                for ingredient in ingredients:
                    qty = float(ingredient['quantity']) * servings_multiplier
                    
                    # Check if ingredient exists
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

def display_recipe(recipe_id):
    """Display recipe details."""
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
                    
                    servings = st.number_input("Servings to make:", min_value=1, value=recipe['servings'])
                    multiplier = servings / recipe['servings']
                    
                    if st.button("Add to Grocery List"):
                        add_ingredients_to_grocery_list(recipe_id, multiplier)
        finally:
            conn.close()

def main():
    st.title("Meal Planner 🍳")
    
    # Add new recipe section with dynamic ingredients
    with st.expander("Add New Recipe"):
        name = st.text_input("Recipe Name")
        description = st.text_area("Description")
        servings = st.number_input("Servings", min_value=1, value=4)
        prep_time = st.number_input("Prep Time (minutes)", min_value=1, value=30)
        instructions = st.text_area("Instructions")
        
        # Dynamic ingredient inputs
        num_ingredients = st.session_state.get('num_ingredients', 3)
        col1, col2 = st.columns(2)
        with col1:
            if st.button('Add Ingredient'):
                num_ingredients += 1
                st.session_state.num_ingredients = num_ingredients
        with col2:
            if st.button('Remove Ingredient') and num_ingredients > 1:
                num_ingredients -= 1
                st.session_state.num_ingredients = num_ingredients
        
        ingredients = []
        for i in range(num_ingredients):
            with st.container():
                st.markdown(f"### Ingredient {i+1}")
                cols = st.columns(4)
                with cols[0]:
                    name_i = st.text_input(f"Name ###{i}", key=f"name_{i}")
                with cols[1]:
                    qty_i = st.number_input(f"Quantity ###{i}", 
                        min_value=0.1, 
                        value=1.0, 
                        step=0.1,
                        key=f"qty_{i}")
                with cols[2]:
                    unit_i = st.selectbox(f"Unit ###{i}",
                        ["g", "kg", "ml", "l", "cup", "tbsp", "tsp", "piece"],
                        key=f"unit_{i}")
                
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
    
    # Display recipes and meal planning
    tab1, tab2 = st.tabs(["Recipes", "Meal Planning"])
    
    with tab1:
        st.header("Recipe Library")
        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("SELECT recipe_id, name FROM recipes ORDER BY name")
                    recipes = cur.fetchall()
                    
                    if recipes:
                        selected_recipe = st.selectbox(
                            "Select a recipe",
                            options=[r['recipe_id'] for r in recipes],
                            format_func=lambda x: next(r['name'] for r in recipes if r['recipe_id'] == x)
                        )
                        
                        if selected_recipe:
                            display_recipe(selected_recipe)
                    else:
                        st.info("No recipes available. Add some recipes to get started!")
            finally:
                conn.close()
    
    with tab2:
        st.header("Meal Planning")
        date = st.date_input("Select date", datetime.now())
        
        meal_types = ["Breakfast", "Lunch", "Dinner"]
        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Get all recipes for selection
                    cur.execute("SELECT recipe_id, name FROM recipes ORDER BY name")
                    recipes = cur.fetchall()
                    recipe_options = {r['recipe_id']: r['name'] for r in recipes}
                    recipe_options[0] = "Select a recipe..."
                    
                    # Get existing meal plans
                    cur.execute("""
                        SELECT meal_type, recipe_id, notes
                        FROM meal_plans
                        WHERE date = %s
                    """, (date,))
                    existing_meals = {m['meal_type']: m for m in cur.fetchall()}
                    
                    for meal_type in meal_types:
                        st.subheader(meal_type)
                        existing_meal = existing_meals.get(meal_type, {})
                        
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            recipe_id = st.selectbox(
                                f"Recipe for {meal_type}",
                                options=list(recipe_options.keys()),
                                format_func=lambda x: recipe_options[x],
                                key=f"{date}_{meal_type}",
                                index=list(recipe_options.keys()).index(
                                    existing_meal.get('recipe_id', 0)
                                )
                            )
                        
                        notes = st.text_area(
                            "Notes",
                            value=existing_meal.get('notes', ''),
                            key=f"notes_{date}_{meal_type}"
                        )
                        
                        if st.button(f"Save {meal_type}", key=f"save_{date}_{meal_type}"):
                            if recipe_id != 0:
                                try:
                                    if existing_meal:
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

if __name__ == "__main__":
    main()
