import streamlit as st
from datetime import datetime, timedelta
from utils.database import get_db_connection
from utils.helpers import configure_page
from utils.styles import get_mobile_styles
from psycopg2.extras import RealDictCursor

def complete_todo(todo_id):
    """Mark a todo item as completed."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE todo_items 
                    SET completed = TRUE 
                    WHERE id = %s
                """, (todo_id,))
            conn.commit()
            st.success("Task completed!")
        except Exception as e:
            st.error(f"Error updating task: {str(e)}")
        finally:
            conn.close()

def handle_complete_todo():
    """Handle the complete todo POST request."""
    todo_id = st.experimental_get_query_params().get('id', [None])[0]
    if todo_id:
        complete_todo(int(todo_id))
        return {"success": True}
    return {"success": False}

def display_todo_item(todo):
    priority_colors = {
        'high': '#ff4b4b',
        'normal': '#ffa500',
        'low': '#00ff00'
    }
    
    priority_icons = {
        'high': '🔴',
        'normal': '🟡',
        'low': '🟢'
    }
    
    due_date_str = ""
    if todo['due_date']:
        if todo['due_date'] == datetime.now().date():
            due_date_str = "Today"
        elif todo['due_date'] == datetime.now().date() + timedelta(days=1):
            due_date_str = "Tomorrow"
        else:
            due_date_str = todo['due_date'].strftime("%b %d")
    
    st.markdown(f"""
        <div class="todo-item priority-{todo['priority']}">
            <div class="todo-checkbox-wrapper">
                <button class="todo-checkbox" onclick="complete_todo({todo['id']})">
                    <span class="checkbox-inner"></span>
                </button>
            </div>
            <div class="todo-content">
                <div class="todo-title">{todo['task']}</div>
                <div class="todo-meta">
                    <div class="todo-priority">
                        {priority_icons[todo['priority']]} {todo['priority'].title()}
                    </div>
                    {f'<div class="todo-due-date">📅 {due_date_str}</div>' if due_date_str else ''}
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def display_todo_list():
    """Display the todo list."""
    st.markdown("""
        <div class="todo-list-container">
            <div class="todo-list">
                <!-- Todo items will be inserted here -->
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, task, priority, due_date, created_at
                    FROM todo_items
                    WHERE completed = FALSE
                    ORDER BY priority, due_date NULLS LAST
                """)
                todos = cur.fetchall()
                
                if todos:
                    for todo in todos:
                        display_todo_item(todo)
                else:
                    st.info("No active tasks")
        finally:
            conn.close()

def display_completed_todos():
    """Display completed todo items."""
    st.markdown("""
        <div class="completed-todos-container">
            <div class="completed-todos-list">
                <!-- Completed items will be inserted here -->
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT task, created_at
                    FROM todo_items
                    WHERE completed = TRUE
                    ORDER BY created_at DESC
                    LIMIT 10
                """)
                completed = cur.fetchall()
                
                if completed:
                    for todo in completed:
                        st.markdown(f"""
                            <div class="completed-todo-item">
                                <div class="completed-todo-content">
                                    <span>✅ {todo['task']}</span>
                                    <span class="completed-date">
                                        {todo['created_at'].strftime("%b %d")}
                                    </span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No completed tasks")
        finally:
            conn.close()

def main():
    # Add this at the start of main()
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                # Ensure todo_items table exists
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS todo_items (
                        id SERIAL PRIMARY KEY,
                        task TEXT NOT NULL,
                        priority VARCHAR(20) DEFAULT 'normal',
                        due_date DATE,
                        completed BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                conn.commit()
        except Exception as e:
            st.error(f"Error initializing todo table: {str(e)}")
            st.stop()
        finally:
            conn.close()
    
    st.markdown(get_mobile_styles(), unsafe_allow_html=True)
    st.title("Todo List ✅")
    
    # Add new todo form
    with st.form("add_todo", clear_on_submit=True):
        st.markdown("""
            <div class="mobile-form">
                <!-- Form content will be inserted here -->
            </div>
        """, unsafe_allow_html=True)
        new_task = st.text_input("New Task")
        col1, col2 = st.columns([2, 1])
        with col1:
            due_date = st.date_input("Due Date", value=None)
        with col2:
            priority = st.selectbox(
                "Priority", 
                options=["high", "normal", "low"],
                format_func=lambda x: {"high": "🔴 High", "normal": "🟡 Normal", "low": "🟢 Low"}[x]
            )
        
        if st.form_submit_button("Add Task"):
            if new_task:
                conn = get_db_connection()
                if conn:
                    try:
                        with conn.cursor() as cur:
                            cur.execute("""
                                INSERT INTO todo_items (task, priority, due_date)
                                VALUES (%s, %s, %s)
                            """, (new_task, priority, due_date))
                        conn.commit()
                        st.success("Task added successfully!")
                    except Exception as e:
                        st.error(f"Error adding task: {str(e)}")
                    finally:
                        conn.close()
    
    # Display todos in tabs
    tab1, tab2 = st.tabs(["Active Tasks", "Completed Tasks"])
    
    st.markdown("""
    <script>
    function complete_todo(id) {
        fetch(`/complete_todo/${id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        })
        .then(response => {
            if (response.ok) {
                window.location.reload();
            }
        });
    }
    </script>
    """, unsafe_allow_html=True)
    
    with tab1:
        display_todo_list()
    
    with tab2:
        display_completed_todos()

    if 'action' in st.query_params and st.query_params['action'] == 'complete_todo':
        if 'id' in st.query_params:
            complete_todo(int(st.query_params['id']))
            # Clear the query params after handling
            st.query_params.clear()
            st.rerun()

    # Add the consistent sidebar styling
    st.markdown("""
        <style>
            /* Show sidebar navigation using specificity */
            body [data-testid="stSidebarNav"] {
                display: block;
                width: auto;
            }
            
            /* Hide duplicate todo list in sidebar using specificity */
            body [href*="/todo_list"] {
                display: none;
            }
        </style>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
