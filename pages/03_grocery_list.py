import streamlit as st
import pandas as pd
from utils.database import get_db_connection
from utils.helpers import configure_page

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
        except Exception as e:
            st.error(f"Error adding sample items: {type(e).__name__}")
        finally:
            conn.close()

def main():
    st.title("Family Grocery List 🛒")
    
    # Add sample data button
    if st.sidebar.button("Add Sample Groceries"):
        add_sample_groceries()
    
    # Add new item form
    with st.expander("Add New Item"):
        with st.form("new_item"):
            col1, col2 = st.columns(2)
            with col1:
                item = st.text_input("Item Name")
                quantity = st.number_input("Quantity", min_value=1, value=1)
            with col2:
                category = st.selectbox("Category", 
                    ["Produce", "Dairy", "Meat", "Pantry", "Bakery", 
                     "Breakfast", "Snacks", "Beverages"])
                added_by = st.selectbox("Added By", 
                    ["Mom", "Dad", "Emma", "James", "Sarah"])
            
            if st.form_submit_button("Add Item"):
                conn = get_db_connection()
                if conn and item:
                    try:
                        with conn.cursor() as cur:
                            cur.execute("""
                                INSERT INTO grocery_items 
                                (item, quantity, category, added_by)
                                VALUES (%s, %s, %s, %s)
                            """, (item, quantity, category, added_by))
                        conn.commit()
                        st.success("Item added successfully!")
                    except Exception as e:
                        st.error(f"Error adding item: {type(e).__name__}")
                    finally:
                        conn.close()
    
    # Display grocery list
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT * FROM grocery_items 
                    ORDER BY category, purchased, item
                """)
                items = cur.fetchall()
                
                # Filter options
                st.sidebar.subheader("Filter Options")
                filter_category = st.sidebar.multiselect(
                    "Filter by Category",
                    ["Produce", "Dairy", "Meat", "Pantry", "Bakery", 
                     "Breakfast", "Snacks", "Beverages"]
                )
                show_purchased = st.sidebar.checkbox("Show Purchased Items")
                
                # Group items by category
                st.subheader("Shopping List")
                
                current_category = None
                for item in items:
                    if (not filter_category or item[3] in filter_category) and \
                       (show_purchased or not item[4]):
                        
                        if item[3] != current_category:
                            st.markdown(f"### {item[3]}")
                            current_category = item[3]
                        
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"""
                            **{item[1]}** (Qty: {item[2]})  
                            Added by: {item[4]}
                            """)
                        with col2:
                            if not item[4]:  # if not purchased
                                if st.button("✅", key=f"buy_{item[0]}"):
                                    with conn.cursor() as update_cur:
                                        update_cur.execute("""
                                            UPDATE grocery_items 
                                            SET purchased = TRUE 
                                            WHERE id = %s
                                        """, (item[0],))
                                    conn.commit()
                                    st.rerun()
        finally:
            conn.close()

if __name__ == "__main__":
    main()
