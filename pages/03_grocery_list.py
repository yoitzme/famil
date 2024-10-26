import streamlit as st
import pandas as pd
from utils.database import get_db_connection
from utils.helpers import configure_page
from psycopg2.extras import RealDictCursor

configure_page()

def add_sample_groceries():
    """Add sample grocery items to the database."""
    sample_items = [
        ("Milk", 2, "Dairy", "Mom", False),
        ("Bread", 1, "Bakery", "Dad", False),
        ("Apples", 6, "Produce", "Mom", False),
        ("Chicken", 1, "Meat", "Dad", False),
        ("Cereal", 2, "Breakfast", "Emma", False),
        ("Eggs", 1, "Dairy", "Mom", False),
        ("Pasta", 2, "Pantry", "Sarah", False),
        ("Tomatoes", 4, "Produce", "James", False),
    ]
    
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM grocery_items")
                count = cur.fetchone()[0]
                if count == 0:
                    for item in sample_items:
                        cur.execute("""
                            INSERT INTO grocery_items 
                            (item, quantity, category, added_by, purchased)
                            VALUES (%s, %s, %s, %s, %s)
                        """, item)
                    conn.commit()
                    st.success("Sample grocery items added successfully!")
                    st.rerun()
        except Exception as e:
            st.error(f"Error adding sample items: {type(e).__name__}")
        finally:
            conn.close()

def main():
    st.title("Family Grocery List 🛒")
    
    # Add sample data button
    if st.sidebar.button("Add Sample Groceries"):
        add_sample_groceries()
    
    # Add new items form with multiple item support
    with st.expander("Add New Items"):
        with st.form("new_items"):
            items_input = st.text_area(
                "Add Multiple Items (one per line)",
                placeholder="Milk\nBread\nEggs"
            )
            col1, col2 = st.columns(2)
            with col1:
                category = st.selectbox("Category", 
                    ["Produce", "Dairy", "Meat", "Pantry", "Bakery", 
                     "Breakfast", "Snacks", "Beverages"])
            with col2:
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
                                        (item, quantity, category, added_by)
                                        VALUES (%s, %s, %s, %s)
                                    """, (item, 1, category, added_by))
                            conn.commit()
                            st.success("Items added successfully!")
                            st.rerun()
                        except Exception as e:
                            conn.rollback()
                            st.error(f"Error adding items: {type(e).__name__}")
                        finally:
                            conn.close()
    
    # Display grocery list with category grouping
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT category, COUNT(*) as count
                    FROM grocery_items
                    WHERE purchased = FALSE
                    GROUP BY category
                    ORDER BY category
                """)
                categories = cur.fetchall()
                
                for cat in categories:
                    st.markdown(f'''
                    <div class="category-header">
                        <h3>{cat['category']}</h3>
                        <div class="category-total">Total Items: {cat['count']}</div>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    cur.execute("""
                        SELECT * FROM grocery_items 
                        WHERE category = %s AND purchased = FALSE
                        ORDER BY item
                    """, (cat['category'],))
                    items = cur.fetchall()
                    
                    for item in items:
                        col1, col2, col3 = st.columns([3, 1, 1])
                        with col1:
                            st.markdown(f'''
                            <div class="item-card">
                                <strong>{item['item']}</strong><br>
                                <small>Added by: {item['added_by']}</small>
                            </div>
                            ''', unsafe_allow_html=True)
                        with col2:
                            quantity = st.number_input(
                                "Qty", 
                                min_value=1, 
                                value=item['quantity'],
                                key=f"qty_{item['id']}"
                            )
                            if quantity != item['quantity']:
                                cur.execute("""
                                    UPDATE grocery_items 
                                    SET quantity = %s 
                                    WHERE id = %s
                                """, (quantity, item['id']))
                                conn.commit()
                                st.rerun()
                        with col3:
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

if __name__ == "__main__":
    main()
