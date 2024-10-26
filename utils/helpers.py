import streamlit as st
from datetime import datetime
import pytz

def configure_page():
    """Configure common page settings."""
    st.set_page_config(
        page_title="Family Organization System",
        page_icon="👨‍👩‍👧‍👦",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def format_date(date_str):
    """Format date string for display."""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%B %d, %Y')
    except:
        return date_str

def get_local_timezone():
    """Get the local timezone."""
    return pytz.timezone('UTC')

def validate_date_input(date_str):
    """Validate date input."""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False
