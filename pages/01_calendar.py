import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.database import get_db_connection
from utils.helpers import configure_page, format_date

configure_page()

def create_calendar_view(events):
    """Create an interactive calendar view using Plotly."""
    fig = go.Figure()
    
    for event in events:
        fig.add_trace(go.Scatter(
            x=[event['start_date']],
            y=[event['title']],
            mode='markers+text',
            name=event['title'],
            text=[event['title']],
            hoverinfo='text+x'
        ))
    
    fig.update_layout(
        title='Family Calendar',
        xaxis_title='Date',
        yaxis_title='Events',
        height=600
    )
    
    return fig

def main():
    st.title("Family Calendar 📅")
    
    # Add new event form
    with st.expander("Add New Event"):
        with st.form("new_event"):
            title = st.text_input("Event Title")
            description = st.text_area("Description")
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")
            event_type = st.selectbox("Event Type", 
                ["Family", "School", "Work", "Other"])
            
            if st.form_submit_button("Add Event"):
                conn = get_db_connection()
                if conn and title and start_date:
                    try:
                        with conn.cursor() as cur:
                            cur.execute("""
                                INSERT INTO events (title, description, start_date, 
                                end_date, event_type)
                                VALUES (%s, %s, %s, %s, %s)
                            """, (title, description, start_date, end_date, 
                                 event_type))
                        conn.commit()
                        st.success("Event added successfully!")
                    except Exception as e:
                        st.error(f"Error adding event: {type(e).__name__}")
                    finally:
                        conn.close()
    
    # Display calendar
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM events ORDER BY start_date")
                events = cur.fetchall()
                
                # Create and display calendar
                calendar = create_calendar_view(events)
                st.plotly_chart(calendar, use_container_width=True)
                
                # List view of upcoming events
                st.subheader("Upcoming Events")
                for event in events:
                    if event['start_date'] >= datetime.now().date():
                        st.info(f"""
                        **{event['title']}**  
                        Date: {format_date(str(event['start_date']))}  
                        Type: {event['event_type']}  
                        Description: {event['description']}
                        """)
        finally:
            conn.close()

if __name__ == "__main__":
    main()
