import streamlit as st
from datetime import datetime, timedelta
from utils.database import get_db_connection
from utils.helpers import format_date
from psycopg2.extras import RealDictCursor
from utils.header import display_header, display_page_title

def add_sample_school_events():
    """Add sample school events to the database."""
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
                cur.execute("SELECT COUNT(*) FROM school_events")
                count = cur.fetchone()[0]
                if count == 0:
                    for event in sample_events:
                        cur.execute("""
                            INSERT INTO school_events 
                            (title, description, event_date, event_type)
                            VALUES (%s, %s, %s, %s)
                        """, event)
                    conn.commit()
                    st.success("Sample school events added successfully!")
        except Exception as e:
            st.error(f"Error adding sample events: {type(e).__name__}")
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
    display_header()
    display_page_title("School Events 🎓")
    
    # Add sample data button
    if st.sidebar.button("Add Sample School Events"):
        add_sample_school_events()
    
    # Add new event form
    with st.expander("Add New School Event"):
        with st.form("new_school_event"):
            title = st.text_input("Event Title")
            description = st.text_area("Description")
            event_date = st.date_input("Event Date")
            event_type = st.selectbox("Event Type", 
                ["Conference", "Performance", "Academic", "Sports", "Other"])
            
            if st.form_submit_button("Add Event"):
                conn = get_db_connection()
                if conn and title:
                    try:
                        with conn.cursor() as cur:
                            cur.execute("""
                                INSERT INTO school_events 
                                (title, description, event_date, event_type)
                                VALUES (%s, %s, %s, %s)
                            """, (title, description, event_date, event_type))
                        conn.commit()
                        st.success("Event added successfully!")
                    except Exception as e:
                        st.error(f"Error adding event: {type(e).__name__}")
                    finally:
                        conn.close()
    
    # Display school events
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT * FROM school_events 
                    ORDER BY event_date
                """)
                events = cur.fetchall()
                
                # Filter options
                st.sidebar.subheader("Filter Options")
                filter_type = st.sidebar.multiselect(
                    "Filter by Event Type",
                    ["Conference", "Performance", "Academic", "Sports", "Other"]
                )
                
                # Timeline view
                st.subheader("School Events Timeline")
                
                today = datetime.now().date()
                for event in events:
                    if not filter_type or event[4] in filter_type:
                        event_date = event[3]
                        
                        # Create colored box based on event type
                        st.markdown(f"""
                        <div style="
                            background-color: {get_event_color(event[4])};
                            padding: 10px;
                            border-radius: 5px;
                            margin: 5px 0;
                        ">
                            <h3>{event[1]}</h3>
                            <p><strong>Date:</strong> {format_date(str(event_date))}</p>
                            <p><strong>Type:</strong> {event[4]}</p>
                            <p>{event[2]}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
        finally:
            conn.close()

if __name__ == "__main__":
    main()
