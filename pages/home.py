import streamlit as st
from utils.database import get_db_connection
from utils.header import display_header
from datetime import datetime, timedelta

# Must be the first Streamlit command
st.set_page_config(
    page_title="Home | Family Hub",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def main():
    st.markdown('<div class="page-transition">', unsafe_allow_html=True)
    
    # Quick actions for frequently used tasks
    st.markdown("""
        <div class="quick-actions">
            <button class="quick-action-button">📝 New Task</button>
            <button class="quick-action-button">📅 Add Event</button>
            <button class="quick-action-button">🛒 Shopping List</button>
            <button class="quick-action-button">👨‍👩‍👧‍👦 Family Update</button>
        </div>
    """, unsafe_allow_html=True)
    
    # Rest of the home view content...
    st.markdown('</div>', unsafe_allow_html=True)