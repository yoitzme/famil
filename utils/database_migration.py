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
                
                # Add unit column to grocery_items table if not exists
                cur.execute("""
                    DO $$ 
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 
                            FROM information_schema.columns 
                            WHERE table_name = 'grocery_items' 
                            AND column_name = 'unit'
                        ) THEN
                            ALTER TABLE grocery_items 
                            ADD COLUMN unit VARCHAR(50) DEFAULT 'piece' NOT NULL;
                        END IF;
                    END $$;
                """)
                
                conn.commit()
                st.success("Database schema updated successfully!")
        except Exception as e:
            st.error(f"Error updating schema: {str(e)}")
        finally:
            conn.close()

# Run the migration when this file is executed directly
if __name__ == "__main__":
    update_database_schema()