# Main application file with updated CSS styles
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.database import init_db, get_db_connection
from utils.helpers import configure_page, format_date
from utils.notifications import (
    get_notifications, mark_notification_as_read, 
    get_unread_count, check_and_create_notifications,
    get_notification_color, get_notification_sound
)
from psycopg2.extras import RealDictCursor

# Configure the page
configure_page()

# Add custom styles for dark theme
st.markdown('''
<style>
    .stButton button {
        width: 100%;
        border-radius: 5px;
        padding: 8px 12px;
    }
    .card {
        background-color: var(--secondary-background-color);
        padding: 15px;
        border-radius: 8px;
        margin: 8px 0;
        border-left: 4px solid var(--primary-color);
        color: #FFFFFF;  /* Make text white for better contrast */
    }
    .card-header {
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .card-content {
        margin-top: 8px;
        color: #FFFFFF;  /* Make text white for better contrast */
    }
    .fixed-height-container {
        height: 300px;
        overflow-y: auto;
        padding: 10px;
        border: 1px solid var(--secondary-background-color);
        border-radius: 8px;
    }
    .event-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    .event-content {
        color: #FFFFFF;  /* Make event description text white */
        font-size: 0.9em;
    }
</style>
''', unsafe_allow_html=True)

[Rest of the main.py file remains unchanged]
