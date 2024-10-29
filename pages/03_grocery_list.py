import streamlit as st
from datetime import datetime, timedelta
from utils.database import get_db_connection
from utils.helpers import configure_page, format_date, is_mobile
from utils.styles import get_mobile_styles
from psycopg2.extras import RealDictCursor

# Add the consistent sidebar styling
st.markdown("""
    <style>
        /* Show sidebar navigation */
        section[data-testid="stSidebarNav"] {
            display: block !important;
            width: auto !important;
        }
    </style>
""", unsafe_allow_html=True)

def mark_as_purchased(item_id):
    """Mark an item as purchased."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE grocery_items 
                    SET purchased = TRUE 
                    WHERE id = %s
                """, (item_id,))
            conn.commit()
            st.success("Item marked as purchased!")
        except Exception as e:
            st.error(f"Error updating item: {str(e)}")
        finally:
            conn.close()

def add_to_togo_list(item_id):
    """Add item to to-go list."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE grocery_items 
                    SET is_togo = TRUE 
                    WHERE id = %s
                """, (item_id,))
            conn.commit()
            st.success("Added to to-go list!")
        except Exception as e:
            st.error(f"Error updating to-go list: {str(e)}")
        finally:
            conn.close()

def remove_from_togo_list(item_id):
    """Remove item from to-go list."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE grocery_items 
                    SET is_togo = FALSE 
                    WHERE id = %s
                """, (item_id,))
            conn.commit()
            st.success("Removed from to-go list!")
        except Exception as e:
            st.error(f"Error updating to-go list: {str(e)}")
        finally:
            conn.close()

def display_category_items(category, items):
    """Display items for a specific category."""
    category_items = [item for item in items if item['category'] == category and not item['purchased']]
    
    for item in category_items:
        col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
        with col1:
            st.write(f"{item['item']}")
        with col2:
            st.write(f"{item['quantity']} {item.get('unit', 'piece')}")
        with col3:
            if st.button("✅", key=f"buy_{item['id']}"):
                mark_as_purchased(item['id'])
                st.rerun()
        with col4:
            togo_button = "📱" if not item.get('is_togo') else "❌"
            if st.button(togo_button, key=f"togo_{item['id']}"):
                if item.get('is_togo'):
                    remove_from_togo_list(item['id'])
                else:
                    add_to_togo_list(item['id'])
                st.rerun()

def display_grocery_list():
    """Display the grocery list."""
    st.markdown("""
        <div class="grocery-list-container">
            <div class="grocery-list-content">
                <!-- Grocery items will be inserted here -->
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, item, quantity, unit, category
                    FROM grocery_items
                    WHERE purchased = FALSE
                    ORDER BY category, item
                """)
                items = cur.fetchall()
                
                if items:
                    for item in items:
                        st.markdown(f"""
                            <div class="grocery-item">
                                <div class="grocery-item-content">
                                    <strong>{item['item']}</strong>
                                    <div class="item-details">
                                        {item['quantity']} {item.get('unit', 'piece')} - {item['category']}
                                    </div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No items in grocery list")
        finally:
            conn.close()

def main():
    st.markdown(get_mobile_styles(), unsafe_allow_html=True)
    st.title("Grocery List 🛒")
    
    # Add tabs for regular list and to-go list
    tab1, tab2 = st.tabs(["📝 Full List", "📱 To-Go List"])
    
    with tab1:
        # Mobile-optimized add item form
        with st.form(key="add_item_form"):
            st.markdown("""
                <div class="mobile-form">
                    <!-- Form content will be inserted here -->
                </div>
            """, unsafe_allow_html=True)
            item = st.text_input("Item")
            
            if is_mobile():
                quantity = st.number_input("Quantity", min_value=1, value=1)
                unit = st.selectbox("Unit", ["piece", "g", "kg", "ml", "l", "cup", "tbsp", "tsp"])
            else:
                col1, col2 = st.columns(2)
                with col1:
                    quantity = st.number_input("Quantity", min_value=1, value=1)
                with col2:
                    unit = st.selectbox("Unit", ["piece", "g", "kg", "ml", "l", "cup", "tbsp", "tsp"])
            
            category = st.selectbox("Category", ["Produce", "Dairy", "Meat", "Pantry", "Other"])
            submit = st.form_submit_button("Add Item")
            
            if submit and item:
                conn = get_db_connection()
                if conn:
                    try:
                        with conn.cursor() as cur:
                            cur.execute(
                                "INSERT INTO grocery_items (item, quantity, unit, category) VALUES (%s, %s, %s, %s)",
                                (item, quantity, unit, category)
                            )
                        conn.commit()
                        st.success("Item added successfully!")
                    except Exception as e:
                        st.error(f"Error adding item: {str(e)}")
                    finally:
                        conn.close()
        
        # Display full list
        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT id, item, quantity, unit, category, purchased, is_togo
                        FROM grocery_items
                        ORDER BY category, item
                    """)
                    items = cur.fetchall()
                    
                    categories = sorted(set(item['category'] for item in items if not item['purchased']))
                    
                    for category in categories:
                        with st.expander(f"{category} Items", expanded=True):
                            display_category_items(category, items)
                    
                    # Display purchased items
                    with st.expander("Recently Purchased Items", expanded=False):
                        purchased_items = [item for item in items if item['purchased']]
                        for item in purchased_items:
                            st.write(f"✅ {item['item']} ({item['quantity']} {item.get('unit', 'piece')})")
                
            finally:
                conn.close()
    
    with tab2:
        # Display to-go list
        st.markdown("""
            <div class="mobile-friendly-list">
                <!-- To-go list items will be inserted here -->
            </div>
        """, unsafe_allow_html=True)
        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT id, item, quantity, unit, category
                        FROM grocery_items
                        WHERE is_togo = TRUE AND purchased = FALSE
                        ORDER BY category, item
                    """)
                    togo_items = cur.fetchall()
                    
                    if togo_items:
                        for item in togo_items:
                            st.markdown(f"""
                            <div class="list-item">
                                <div class="item-content">
                                    <strong>{item['item']}</strong><br>
                                    {item['quantity']} {item.get('unit', 'piece')} - {item['category']}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No items in to-go list. Add items by clicking 📱 in the full list.")
            finally:
                conn.close()

if __name__ == "__main__":
    main()
