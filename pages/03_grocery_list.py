import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.database import get_db_connection
from utils.helpers import configure_page, format_date
from psycopg2.extras import RealDictCursor

configure_page()

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

def main():
    st.title("Grocery List 🛒")
    
    # Add item form
    with st.form("add_item"):
        item = st.text_input("Item")
        col1, col2 = st.columns(2)
        with col1:
            quantity = st.number_input("Quantity", min_value=1, value=1)
        with col2:
            unit = st.selectbox("Unit", ["piece", "g", "kg", "ml", "l", "cup", "tbsp", "tsp"])
        category = st.selectbox("Category", ["Produce", "Dairy", "Meat", "Pantry", "Other"])
        
        if st.form_submit_button("Add Item"):
            if item:
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
    
    # Display items
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get all items
                cur.execute("""
                    SELECT id, item, quantity, unit, category, purchased
                    FROM grocery_items
                    ORDER BY category, item
                """)
                items = cur.fetchall()
                
                # Get unique categories
                categories = sorted(set(item['category'] for item in items if not item['purchased']))
                
                # Display items by category
                st.subheader("Current List")
                for category in categories:
                    with st.expander(f"{category} Items", expanded=True):
                        for item in items:
                            if item['category'] == category and not item['purchased']:
                                col1, col2, col3 = st.columns([3, 1, 1])
                                with col1:
                                    st.write(f"{item['item']}")
                                with col2:
                                    st.write(f"{item['quantity']} {item.get('unit', 'piece')}")
                                with col3:
                                    if st.button("✅", key=f"buy_{item['id']}"):
                                        mark_as_purchased(item['id'])
                                        st.rerun()
                
                # Display purchased items
                with st.expander("Recently Purchased Items", expanded=False):
                    purchased_items = [item for item in items if item['purchased']]
                    for item in purchased_items:
                        st.write(f"✅ {item['item']} ({item['quantity']} {item.get('unit', 'piece')})")
                        
        except Exception as e:
            st.error(f"Error managing grocery list: {str(e)}")
        finally:
            conn.close()

if __name__ == "__main__":
    main()
