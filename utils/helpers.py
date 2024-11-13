import streamlit as st
from datetime import datetime
import pytz

def get_streamlit_context():
    """Get Streamlit context safely"""
    try:
        return st.session_state.get('context_ready', False)
    except:
        return False

def configure_page():
    """Configure common page settings."""
    # Skip if already configured
    if 'page_configured' in st.session_state:
        return
        
    try:
        st.set_page_config(
            page_title="Family Organization System",
            page_icon="👨‍👩‍👧‍👦",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        st.session_state.page_configured = True
    except Exception:
        pass

def is_mobile():
    """Check if the user is on a mobile device"""
    if not get_streamlit_context():
        return False
        
    try:
        user_agent = st.get_user_agent()
        return (
            'mobile' in user_agent.lower() or 
            'android' in user_agent.lower() or 
            'iphone' in user_agent.lower() or 
            'ipad' in user_agent.lower()
        )
    except:
        return False

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

def wrap_html_content(content, wrapper_class=""):
    """Wrap HTML content in proper tags with optional wrapper class."""
    return f"""
        <div class="{wrapper_class}">
            {content}
        </div>
    """
