import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.database import get_db_connection
from utils.helpers import configure_page, format_date
from psycopg2.extras import RealDictCursor

configure_page()

def get_event_color(event_type):
    """Return color based on event type."""
    colors = {
        "Family": "#FF9999",    # Light red
        "School": "#99FF99",    # Light green
        "Work": "#9999FF",      # Light blue
        "Other": "#FFB366"      # Light orange
    }
    return colors.get(event_type, "#FFFFFF")

def add_sample_calendar_events():
    """Add sample calendar events to the database."""
    sample_events = [
        ("Emma's Birthday", "Birthday party at home", "2024-11-10", 
         "2024-11-10", "Family"),
        ("Doctor Appointment", "Annual checkup", "2024-11-15", 
         "2024-11-15", "Family"),
        ("School Meeting", "Parent council", "2024-11-20", 
         "2024-11-20", "School"),
        ("Work Presentation", "Quarterly review", "2024-11-25", 
         "2024-11-25", "Work"),
        ("Family Dinner", "Grandparents visiting", "2024-12-01", 
         "2024-12-01", "Family"),
    ]
    
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM events")
                count = cur.fetchone()[0]
                if count == 0:
                    for event in sample_events:
                        cur.execute("""
                            INSERT INTO events 
                            (title, description, start_date, end_date, event_type)
                            VALUES (%s, %s, %s, %s, %s)
                        """, event)
                    conn.commit()
                    st.success("Sample calendar events added successfully!")
        except Exception as e:
            st.error(f"Error adding sample events: {type(e).__name__}")
        finally:
            conn.close()

def clear_all_sample_data():
    """Clear all sample data from all tables."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                tables = ['events', 'chores', 'grocery_items', 'school_events', 'notifications']
                for table in tables:
                    cur.execute(f"DELETE FROM {table}")
                conn.commit()
                st.success("All sample data cleared successfully!")
        except Exception as e:
            st.error(f"Error clearing sample data: {type(e).__name__}")
        finally:
            conn.close()

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
            marker=dict(
                color=get_event_color(event['event_type']),
                size=15,
                line=dict(color='black', width=1)
            ),
            hovertemplate=(
                f"<b>{event['title']}</b><br>"
                f"Date: {format_date(str(event['start_date']))}<br>"
                f"Type: {event['event_type']}<br>"
                f"Description: {event['description']}<br>"
                "<extra></extra>"
            )
        ))
    
    fig.update_layout(
        title='Family Calendar',
        xaxis_title='Date',
        yaxis_title='Events',
        height=600,
        showlegend=False,
        hovermode='closest'
    )
    
    return fig

def main():
    st.title("Family Calendar 📅")
    
    # Add sample data button
    if st.sidebar.button("Add Sample Calendar Events"):
        add_sample_calendar_events()
    
    # Clear all sample data button with confirmation
    if st.sidebar.button("Clear All Sample Data"):
        with st.sidebar:
            st.warning("""
            This will clear ALL sample data from:
            - Calendar Events
            - Chores
            - Grocery Items
            - School Events
            - Notifications
            
            Are you sure?
            """)
            if st.button("Yes, Clear Everything"):
                clear_all_sample_data()
    
    # Add new event form
    with st.expander("Add New Event"):
        with st.form("new_event"):
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Event Title")
                description = st.text_area("Description")
            with col2:
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
                                INSERT INTO events 
                                (title, description, start_date, end_date, event_type)
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
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Filter options
                st.sidebar.subheader("Filter Options")
                filter_type = st.sidebar.multiselect(
                    "Filter by Event Type",
                    ["Family", "School", "Work", "Other"]
                )
                
                # Get events
                cur.execute("SELECT * FROM events ORDER BY start_date")
                events = cur.fetchall()
                
                # Filter events
                filtered_events = [
                    event for event in events 
                    if not filter_type or event['event_type'] in filter_type
                ]
                
                # Create and display calendar
                calendar = create_calendar_view(filtered_events)
                st.plotly_chart(calendar, use_container_width=True)
                
                # List view of upcoming events
                st.subheader("Upcoming Events")
                
                # Group events by month
                current_month = None
                for event in filtered_events:
                    if event['start_date'] >= datetime.now().date():
                        event_month = event['start_date'].strftime('%B %Y')
                        
                        if event_month != current_month:
                            st.markdown(f"### {event_month}")
                            current_month = event_month
                        
                        st.markdown(f"""
                        <div style="
                            background-color: {get_event_color(event['event_type'])};
                            padding: 10px;
                            border-radius: 5px;
                            margin: 5px 0;
                        ">
                            <h4>{event['title']}</h4>
                            <p><strong>Date:</strong> {format_date(str(event['start_date']))}</p>
                            <p><strong>Type:</strong> {event['event_type']}</p>
                            <p>{event['description']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
        finally:
            conn.close()

if __name__ == "__main__":
    main()
