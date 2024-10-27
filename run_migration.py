import streamlit as st
from utils.database import get_db_connection

def update_database_schema():
    """Update database schema with missing columns."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                # Add instructions column to recipes table
                cur.execute("""
                    ALTER TABLE recipes 
                    ADD COLUMN IF NOT EXISTS instructions TEXT;
                """)
                
                # Add unit column to grocery_items table
                cur.execute("""
                    ALTER TABLE grocery_items 
                    ADD COLUMN IF NOT EXISTS unit VARCHAR(50) DEFAULT 'piece';
                """)
                
                conn.commit()
                print("Database schema updated successfully!")
        except Exception as e:
            print(f"Error updating schema: {str(e)}")
        finally:
            conn.close()

if __name__ == "__main__":
    update_database_schema()
