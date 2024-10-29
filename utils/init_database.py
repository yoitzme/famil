import streamlit as st
from utils.database import get_db_connection

def initialize_database():
    """Initialize all database tables."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                # Create all tables
                cur.execute("""
                    -- Create todo_items table
                    CREATE TABLE IF NOT EXISTS todo_items (
                        id SERIAL PRIMARY KEY,
                        task TEXT NOT NULL,
                        priority VARCHAR(20) DEFAULT 'normal',
                        due_date DATE,
                        completed BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

                    -- Create grocery_items table
                    CREATE TABLE IF NOT EXISTS grocery_items (
                        id SERIAL PRIMARY KEY,
                        item TEXT NOT NULL,
                        quantity INTEGER DEFAULT 1,
                        unit VARCHAR(50) DEFAULT 'piece',
                        category VARCHAR(50),
                        purchased BOOLEAN DEFAULT FALSE,
                        is_togo BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

                    -- Create events table
                    CREATE TABLE IF NOT EXISTS events (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(255) NOT NULL,
                        description TEXT,
                        start_date DATE NOT NULL,
                        end_date DATE,
                        event_type VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

                    -- Create meal_plans table
                    CREATE TABLE IF NOT EXISTS meal_plans (
                        id SERIAL PRIMARY KEY,
                        date DATE NOT NULL,
                        meal_type VARCHAR(50),
                        recipe_id INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

                    -- Create recipes table
                    CREATE TABLE IF NOT EXISTS recipes (
                        recipe_id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        description TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                conn.commit()
                print("Database initialized successfully!")
                return True
        except Exception as e:
            print(f"Error initializing database: {str(e)}")
            return False
        finally:
            conn.close()
    return False

if __name__ == "__main__":
    initialize_database()
