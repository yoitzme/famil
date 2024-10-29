import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.database import get_db_connection
from utils.helpers import configure_page, format_date

configure_page()

def add_sample_chores():
    """Add sample chores data to the database."""
    sample_chores = [
        ("Clean bedroom", "Emma", "2024-10-26", False),
        ("Take out trash", "James", "2024-10-26", False),
        ("Do dishes", "Sarah", "2024-10-26", False),
        ("Vacuum living room", "David", "2024-10-27", False),
        ("Clean bathroom", "Emma", "2024-10-27", False),
        ("Mow lawn", "James", "2024-10-28", False),
        ("Fold laundry", "Sarah", "2024-10-28", False),
    ]
    
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM chores")
                count = cur.fetchone()[0]
                if count == 0:
                    for chore in sample_chores:
                        cur.execute("""
                            INSERT INTO chores (task, assigned_to, due_date, completed)
                            VALUES (%s, %s, %s, %s)
                        """, chore)
                    conn.commit()
                    st.success("Sample chores added successfully!")
        except Exception as e:
            st.error(f"Error adding sample chores: {type(e).__name__}")
        finally:
            conn.close()

def main():
    st.markdown("""
        <style>
            /* Show sidebar navigation */
            section[data-testid="stSidebarNav"] {
                display: block !important;
                width: auto !important;
            }
        </style>
    """, unsafe_allow_html=True)
    st.title("Family Chores ✨")
    
    # Add sample data button
    if st.sidebar.button("Add Sample Chores"):
        add_sample_chores()
    
    # Add new chore form
    with st.expander("Add New Chore"):
        with st.form("new_chore"):
            task = st.text_input("Task Description")
            assigned_to = st.selectbox("Assign To", 
                ["Emma", "James", "Sarah", "David"])
            due_date = st.date_input("Due Date")
            
            if st.form_submit_button("Add Chore"):
                conn = get_db_connection()
                if conn and task:
                    try:
                        with conn.cursor() as cur:
                            cur.execute("""
                                INSERT INTO chores (task, assigned_to, due_date)
                                VALUES (%s, %s, %s)
                            """, (task, assigned_to, due_date))
                        conn.commit()
                        st.success("Chore added successfully!")
                    except Exception as e:
                        st.error(f"Error adding chore: {type(e).__name__}")
                    finally:
                        conn.close()
    
    # Display chores
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT * FROM chores 
                    ORDER BY due_date, completed
                """)
                chores = cur.fetchall()
                
                # Filter options
                st.sidebar.subheader("Filter Options")
                filter_person = st.sidebar.multiselect(
                    "Filter by Person",
                    ["Emma", "James", "Sarah", "David"]
                )
                
                # Show completed checkbox moved out of sidebar with default True
                show_completed = st.checkbox("Show Completed Tasks", value=True)
                
                # Display chores in tabs by date
                st.subheader("Tasks Overview")
                tab1, tab2, tab3 = st.tabs(["Today", "Tomorrow", "Upcoming"])
                
                today = datetime.now().date()
                tomorrow = today + timedelta(days=1)
                
                for chore in chores:
                    if (not filter_person or chore[2] in filter_person) and \
                       (show_completed or not chore[3]):
                        
                        due_date = chore[3]
                        content = f"""
                        **{chore[1]}**  
                        Assigned to: {chore[2]}  
                        Status: {'✅ Completed' if chore[3] else '⏳ Pending'}
                        """
                        
                        if due_date == today:
                            with tab1:
                                st.info(content)
                        elif due_date == tomorrow:
                            with tab2:
                                st.warning(content)
                        else:
                            with tab3:
                                st.success(content)
                                
        finally:
            conn.close()

if __name__ == "__main__":
    main()
