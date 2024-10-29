import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from utils.database import get_db_connection

def update_database_schema():
    """Update database schema with missing columns."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                # Add is_togo column to grocery_items table if not exists
                cur.execute("""
                    DO $$ 
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 
                            FROM information_schema.columns 
                            WHERE table_name = 'grocery_items' 
                            AND column_name = 'is_togo'
                        ) THEN
                            ALTER TABLE grocery_items 
                            ADD COLUMN is_togo BOOLEAN DEFAULT FALSE;
                        END IF;
                    END $$;

                    -- Add instructions column to recipes table if not exists
                    DO $$ 
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 
                            FROM information_schema.columns 
                            WHERE table_name = 'recipes' 
                            AND column_name = 'instructions'
                        ) THEN
                            ALTER TABLE recipes 
                            ADD COLUMN instructions TEXT;
                        END IF;
                    END $$;

                    -- Update recipes table structure if not exists
                    DO $$ 
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 
                            FROM information_schema.columns 
                            WHERE table_name = 'recipes' 
                            AND column_name = 'servings'
                        ) THEN
                            ALTER TABLE recipes 
                            ADD COLUMN servings INTEGER DEFAULT 4;
                        END IF;
                    END $$;

                    DO $$ 
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 
                            FROM information_schema.columns 
                            WHERE table_name = 'recipes' 
                            AND column_name = 'prep_time'
                        ) THEN
                            ALTER TABLE recipes 
                            ADD COLUMN prep_time INTEGER DEFAULT 30;
                        END IF;
                    END $$;

                    -- Create recipe_ingredients table if not exists
                    CREATE TABLE IF NOT EXISTS recipe_ingredients (
                        ingredient_id SERIAL PRIMARY KEY,
                        recipe_id INTEGER REFERENCES recipes(recipe_id),
                        ingredient_name VARCHAR(255) NOT NULL,
                        quantity DECIMAL NOT NULL,
                        unit VARCHAR(50) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

                    -- Create meal_plans table if not exists
                    CREATE TABLE IF NOT EXISTS meal_plans (
                        plan_id SERIAL PRIMARY KEY,
                        date DATE NOT NULL,
                        meal_type VARCHAR(50) NOT NULL,
                        recipe_id INTEGER REFERENCES recipes(recipe_id),
                        notes TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                conn.commit()
                st.success("Database schema updated successfully!")
        except Exception as e:
            st.error(f"Error updating schema: {str(e)}")
            print(f"Error updating schema: {str(e)}")
        finally:
            conn.close()

if __name__ == "__main__":
    update_database_schema()
