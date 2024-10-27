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
        color: #FFFFFF;
    }
    .card-header {
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .card-content {
        margin-top: 8px;
        color: #FFFFFF;
    }
    .date-header {
        background-color: var(--primary-background-color);
        padding: 10px;
        margin: 20px 0 10px 0;
        border-radius: 5px;
        border-left: 4px solid var(--primary-color);
    }
    .date-group {
        background-color: var(--secondary-background-color);
        padding: 15px;
        margin-bottom: 20px;
        border-radius: 8px;
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
        color: #FFFFFF;
        font-size: 0.9em;
    }
    .meal-card {
        background-color: var(--secondary-background-color);
        color: #FFFFFF;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid var(--primary-color);
    }
    .meal-title {
        color: #FFFFFF;
        font-size: 1.2em;
        font-weight: bold;
    }
    .meal-description {
        color: #E0E0E0;
        font-size: 0.9em;
        margin-top: 5px;
    }
    .ingredient-form {
        background-color: var(--secondary-background-color);
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .ingredient-header {
        color: #FFFFFF;
        font-size: 1.1em;
        margin-bottom: 10px;
    }
    @media (max-width: 768px) {
        .stColumn {
            flex: 0 1 100% !important;
            width: 100% !important;
        }
        .meal-card {
            margin: 8px 0;
        }
    }
</style>
''', unsafe_allow_html=True)
