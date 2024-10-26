import streamlit as st
import pandas as pd
from utils.database import init_db
from utils.helpers import configure_page

# Configure the page
configure_page()

def main():
    # Initialize database
    init_db()
    
    st.title("Family Organization System")
    
    # Welcome message
    st.markdown("""
    ## Welcome to Your Family Dashboard! 👋
    
    Navigate through the different sections using the sidebar:
    - 📅 Calendar - Track family events and appointments
    - ✅ Chores - Manage household tasks
    - 🛒 Grocery List - Keep track of shopping needs
    - 🏫 School Events - Stay updated with school activities
    """)
    
    # Quick Actions Section
    st.subheader("Quick Actions")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("📋 Today's Tasks")
        # Display today's tasks from database
        
    with col2:
        st.info("🛒 Shopping List")
        # Display current shopping list items

if __name__ == "__main__":
    main()
