import streamlit as st
import pandas as pd
from datetime import datetime
from utils.database import get_db_connection
from utils.helpers import configure_page, format_date

configure_page()

def add_sample_events():
    """Add sample events to the database."""
    sample_events = [
        ("Parent-Teacher Conference", "Meet with Mrs. Smith", "2024-11-15", 
         "Conference"),
        ("School Play", "Romeo and Juliet performance", "2024-11-20", 
         "Performance"),
        ("Science Fair", "Present projects", "2024-12-05", "Academic"),
        ("Holiday Concert", "Winter music showcase", "2024-12-15", 
         "Performance"),
        ("End of Term", "Last day before break", "2024-12-20", "Academic"),
        ("Spring Semester Start", "First day back", "2025-01-05", "Academic"),
    ]
    
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                # Check if events already exist
                cur.execute("SELECT COUNT(*) FROM events")
                result = cur.fetchone()
                count = result[0] if result else 0
                
                if count == 0:
                    for event in sample_events:
                        cur.execute("""
                            INSERT INTO events 
                            (title, description, start_date, event_type)
                            VALUES (%s, %s, %s, %s)
                        """, event)
                    conn.commit()
                    st.success("Sample events added successfully!")
        except Exception as e:
            st.error(f"Error adding sample events: {str(e)}")
        finally:
            conn.close()

def get_event_color(event_type):
    """Return color based on event type."""
    colors = {
        "Conference": "#FF9999",  # Light red
        "Performance": "#99FF99",  # Light green
        "Academic": "#9999FF",    # Light blue
        "Sports": "#FFFF99",      # Light yellow
        "Other": "#FFB366"        # Light orange
    }
    return colors.get(event_type, "#FFFFFF")

def main():
    st.title("Events 📅")
    
    # Add sample data button
    if st.sidebar.button("Add Sample Events"):
        add_sample_events()
    
    # Add new event form
    with st.expander("Add New Event"):
        with st.form("new_event"):
            title = st.text_input("Event Title")
            description = st.text_area("Description")
            start_date = st.date_input("Event Date")
            event_type = st.selectbox("Event Type", 
                ["Conference", "Performance", "Academic", "Sports", "Other"])
            
            if st.form_submit_button("Add Event"):
                if not title:
                    st.error("Please enter an event title")
                else:
                    conn = get_db_connection()
                    if conn:
                        try:
                            with conn.cursor() as cur:
                                cur.execute("""
                                    INSERT INTO events 
                                    (title, description, start_date, event_type)
                                    VALUES (%s, %s, %s, %s)
                                """, (title, description, start_date, event_type))
                            conn.commit()
                            st.success("Event added successfully!")
                        except Exception as e:
                            st.error(f"Error adding event: {str(e)}")
                        finally:
                            conn.close()
    
    # Display events
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT title, description, start_date, event_type 
                    FROM events 
                    ORDER BY start_date
                """)
                events = cur.fetchall()
                
                # Filter options
                st.sidebar.subheader("Filter Options")
                filter_type = st.sidebar.multiselect(
                    "Filter by Event Type",
                    ["Conference", "Performance", "Academic", "Sports", "Other"]
                )
                
                # Timeline view with updated card styling
                st.subheader("Events Timeline")
                
                today = datetime.now().date()
                for event in events:
                    if not filter_type or event[3] in filter_type:
                        st.markdown(f'''
                        <div class="card">
                            <div class="card-header">
                                <strong>{event[0]}</strong>
                                <span class="event-type">{event[3]}</span>
                            </div>
                            <div class="card-content">
                                <p>{format_date(str(event[2]))}</p>
                                <p>{event[1]}</p>
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)
                        
        except Exception as e:
            st.error(f"Error displaying events: {str(e)}")
        finally:
            conn.close()

if __name__ == "__main__":
    main()
