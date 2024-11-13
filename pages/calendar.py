import streamlit as st
from datetime import datetime, timedelta
from utils.database import get_db_connection
from utils.header import display_header, display_page_title
from psycopg2.extras import RealDictCursor

def main():
    display_header()
    display_page_title("Calendar 📅")
    
    # Calendar view implementation
    st.subheader("Monthly View")
    
    # Get current date
    current_date = datetime.now()
    selected_month = st.date_input("Select Month", current_date)
    
    # Get events for the selected month
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM events 
                    WHERE EXTRACT(MONTH FROM start_date) = %s
                    AND EXTRACT(YEAR FROM start_date) = %s
                    ORDER BY start_date
                """, (selected_month.month, selected_month.year))
                events = cur.fetchall()
        finally:
            conn.close()
    
    # Event management
    with st.expander("Add New Event"):
        with st.form("new_event"):
            title = st.text_input("Event Title")
            description = st.text_area("Description")
            start_date = st.date_input("Start Date")
            event_type = st.selectbox("Event Type", 
                ["Conference", "Performance", "Academic", "Sports", "Other"])
            
            if st.form_submit_button("Add Event"):
                if title:
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
    
    # Display upcoming events
    st.subheader("Upcoming Events")
    if 'events' in locals() and events:
        for event in events:
            st.markdown(f"""
                <div style='padding: 10px; border-left: 3px solid var(--primary-color); 
                    margin: 5px 0; background: rgba(255,255,255,0.05); border-radius: 5px;'>
                    <h3>{event['title']}</h3>
                    <p>{event['description']}</p>
                    <small style='color: #9CA3AF;'>
                        Date: {event['start_date'].strftime('%Y-%m-%d')} | 
                        Type: {event['event_type']}
                    </small>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No events found for the selected month")

if __name__ == "__main__":
    main()
