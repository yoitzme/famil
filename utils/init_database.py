import streamlit as st
from utils.database import get_db_connection
from utils.logger import log_error, log_info

def initialize_database():
    """Initialize database with all required tables."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                # Drop all existing tables in correct order
                cur.execute("""
                    DROP TABLE IF EXISTS recipe_ingredients CASCADE;
                    DROP TABLE IF EXISTS meal_plans CASCADE;
                    DROP TABLE IF EXISTS recipes CASCADE;
                    DROP TABLE IF EXISTS family_messages CASCADE;
                    DROP TABLE IF EXISTS notifications CASCADE;
                    DROP TABLE IF EXISTS todo_items CASCADE;
                    DROP TABLE IF EXISTS events CASCADE;
                    DROP TABLE IF EXISTS chores CASCADE;
                    DROP TABLE IF EXISTS school_events CASCADE;
                    DROP TABLE IF EXISTS grocery_items CASCADE;
                """)
                
                # Create all tables in correct order
                cur.execute("""
                    -- Base tables (no foreign key dependencies)
                    CREATE TABLE recipes (
                        recipe_id SERIAL PRIMARY KEY,
                        name VARCHAR(200) NOT NULL,
                        description TEXT,
                        servings INTEGER CHECK (servings > 0),
                        prep_time INTEGER CHECK (prep_time > 0),
                        instructions TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

                    CREATE TABLE todo_items (
                        id SERIAL PRIMARY KEY,
                        task TEXT NOT NULL,
                        priority VARCHAR(20) DEFAULT 'normal',
                        due_date DATE,
                        completed BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        CONSTRAINT valid_priority CHECK (priority IN ('high', 'normal', 'low'))
                    );

                    CREATE TABLE events (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(200) NOT NULL,
                        description TEXT,
                        start_date DATE NOT NULL,
                        end_date DATE NOT NULL,
                        event_type VARCHAR(50) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        CONSTRAINT valid_dates CHECK (end_date >= start_date)
                    );

                    CREATE TABLE chores (
                        id SERIAL PRIMARY KEY,
                        task TEXT NOT NULL,
                        assigned_to VARCHAR(100) NOT NULL,
                        due_date DATE,
                        completed BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

                    CREATE TABLE school_events (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(200) NOT NULL,
                        description TEXT,
                        event_date DATE NOT NULL,
                        event_type VARCHAR(50) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

                    CREATE TABLE grocery_items (
                        id SERIAL PRIMARY KEY,
                        item VARCHAR(200) NOT NULL,
                        quantity DECIMAL(10,2) CHECK (quantity > 0),
                        unit VARCHAR(20),
                        category VARCHAR(50),
                        purchased BOOLEAN DEFAULT FALSE,
                        is_togo BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

                    CREATE TABLE family_messages (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(200) NOT NULL,
                        content TEXT NOT NULL,
                        author VARCHAR(100) NOT NULL,
                        priority INTEGER CHECK (priority IN (1, 2, 3)),
                        expires_at DATE,
                        pinned BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

                    CREATE TABLE notifications (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        message TEXT NOT NULL,
                        type VARCHAR(50) NOT NULL,
                        read BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        CONSTRAINT valid_type CHECK (type IN ('info', 'warning', 'error', 'success'))
                    );

                    -- Dependent tables (with foreign keys)
                    CREATE TABLE meal_plans (
                        id SERIAL PRIMARY KEY,
                        date DATE NOT NULL,
                        meal_type VARCHAR(50) NOT NULL,
                        recipe_id INTEGER REFERENCES recipes(recipe_id) ON DELETE SET NULL,
                        notes TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        CONSTRAINT valid_meal_type CHECK (meal_type IN ('Breakfast', 'Lunch', 'Dinner', 'Snack'))
                    );

                    CREATE TABLE recipe_ingredients (
                        id SERIAL PRIMARY KEY,
                        recipe_id INTEGER REFERENCES recipes(recipe_id) ON DELETE CASCADE,
                        ingredient_name VARCHAR(100) NOT NULL,
                        quantity DECIMAL(10,2) CHECK (quantity > 0),
                        unit VARCHAR(20) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

                    -- Create indexes for better performance
                    CREATE INDEX idx_meal_plans_date ON meal_plans(date);
                    CREATE INDEX idx_meal_plans_recipe ON meal_plans(recipe_id);
                    CREATE INDEX idx_recipe_ingredients_recipe ON recipe_ingredients(recipe_id);
                    CREATE INDEX idx_family_messages_expires ON family_messages(expires_at);
                    CREATE INDEX idx_notifications_user_read ON notifications(user_id, read);
                    CREATE INDEX idx_todo_items_due_date ON todo_items(due_date);
                    CREATE INDEX idx_chores_due_date ON chores(due_date);
                    CREATE INDEX idx_grocery_items_category ON grocery_items(category);
                    CREATE INDEX idx_school_events_date ON school_events(event_date);
                """)
                
                conn.commit()
                log_info("All tables created successfully")
                return True
                
        except Exception as e:
            log_error(f"Database initialization error: {str(e)}")
            conn.rollback()
            return False
        finally:
            conn.close()
    return False

if __name__ == "__main__":
    initialize_database()
