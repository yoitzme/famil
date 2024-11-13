import streamlit as st
from datetime import datetime
from utils.database import get_db_connection
from psycopg2.extras import RealDictCursor
from utils.logger import log_error
from utils.helpers import format_date
from utils.styles import get_mobile_styles

def display_todo_list():
    """Display the todo list with filtering and sorting options."""
    st.subheader("📋 Todo List")
    
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get all todo items
                cur.execute("""
                    SELECT * FROM todo_items 
                    WHERE completed = FALSE 
                    ORDER BY due_date, priority DESC
                """)
                todos = cur.fetchall()
                
                if todos:
                    for todo in todos:
                        priority_color = {
                            'high': '🔴',
                            'normal': '🟡',
                            'low': '🟢'
                        }.get(todo['priority'], '⚪')
                        
                        st.markdown(f"""
                            <div style='padding: 10px; 
                                border-left: 3px solid var(--primary-color); 
                                margin: 5px 0; 
                                background: rgba(255,255,255,0.05); 
                                border-radius: 5px;'>
                                {priority_color} {todo['task']}<br>
                                <small style='color: #9CA3AF;'>
                                    Due: {format_date(str(todo['due_date']))}
                                </small>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No pending tasks")
                    
        except Exception as e:
            log_error(f"Error displaying todo list: {str(e)}")
        finally:
            conn.close()

def display_quick_notes():
    """Display quick notes widget."""
    st.subheader("📝 Quick Notes")
    
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM quick_notes 
                    ORDER BY created_at DESC 
                    LIMIT 5
                """)
                notes = cur.fetchall()
                
                if notes:
                    for note in notes:
                        st.markdown(f"""
                            <div style='padding: 10px; 
                                background: rgba(255,255,255,0.05); 
                                border-radius: 5px; 
                                margin: 5px 0;'>
                                {note['content']}<br>
                                <small style='color: #9CA3AF;'>
                                    Added: {format_date(str(note['created_at']))}
                                </small>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No notes yet")
                    
        except Exception as e:
            log_error(f"Error displaying quick notes: {str(e)}")
        finally:
            conn.close()

def display_weather_widget():
    """Display weather information."""
    try:
        st.markdown("""
            <div style='padding: 15px; 
                background: rgba(255,255,255,0.05); 
                border-radius: 10px; 
                text-align: center;'>
                <h3>Weather information coming soon!</h3>
                <p>This feature will display local weather updates.</p>
            </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        log_error(f"Error displaying weather widget: {str(e)}")
