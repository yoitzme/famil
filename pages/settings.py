import streamlit as st
from utils.error_diagnostics import run_diagnostics
from utils.database import get_db_connection
from utils.init_database import initialize_database
from utils.settings_manager import (
    load_settings,
    save_settings,
    reset_settings,
    get_theme_options
)
from utils.system_info import get_system_info
from utils.backup_manager import create_backup, restore_backup
from utils.header import display_header
from utils.logger import display_logs_in_settings, clear_old_logs
import json

def render_settings_page():
    # Display header at the top of the page
    display_header()
    
    st.title("⚙️ Settings")
    
    # Create tabs for different settings categories
    settings_tabs = st.tabs([
        "🔍 Diagnostics",
        "🎨 Appearance",
        "🔔 Notifications",
        "💾 Backup & Restore",
        "ℹ️ System Info",
        "📝 Logs"
    ])
    
    # Load current settings
    current_settings = load_settings()
    
    # Diagnostics Tab
    with settings_tabs[0]:
        st.header("System Diagnostics")
        
        # Add system status indicator
        system_status = st.empty()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Run Diagnostics"):
                with st.spinner("Running diagnostics..."):
                    if run_diagnostics():
                        system_status.success("✅ All systems operational")
                    else:
                        system_status.error("❌ System issues detected")
        
        with col2:
            if st.button("Initialize Database"):
                with st.spinner("Initializing database..."):
                    if initialize_database():
                        st.success("Database initialized successfully")
                    else:
                        st.error("Failed to initialize database")
        
        with col3:
            if st.button("Reset Settings"):
                with st.spinner("Resetting settings..."):
                    reset_settings()
                    st.success("Settings reset to defaults")
                    st.rerun()
    
    # Appearance Tab
    with settings_tabs[1]:
        st.header("Appearance Settings")
        
        # Theme Selection
        selected_theme = st.selectbox(
            "Select Theme",
            options=get_theme_options(),
            index=get_theme_options().index(current_settings.get('theme', 'light'))
        )
        
        # Font Size
        font_size = st.slider(
            "Base Font Size (px)",
            min_value=12,
            max_value=24,
            value=current_settings.get('font_size', 16)
        )
        
        # Compact Mode
        compact_mode = st.toggle(
            "Compact Mode",
            value=current_settings.get('compact_mode', False)
        )
        
        if st.button("Save Appearance Settings"):
            current_settings.update({
                'theme': selected_theme,
                'font_size': font_size,
                'compact_mode': compact_mode
            })
            save_settings(current_settings)
            st.success("Appearance settings saved!")
    
    # Notifications Tab
    with settings_tabs[2]:
        st.header("Notification Settings")
        
        # Email Notifications
        email_notifications = st.toggle(
            "Email Notifications",
            value=current_settings.get('email_notifications', False)
        )
        
        if email_notifications:
            email_address = st.text_input(
                "Email Address",
                value=current_settings.get('email_address', '')
            )
        
        # Push Notifications
        push_notifications = st.toggle(
            "Push Notifications",
            value=current_settings.get('push_notifications', True)
        )
        
        # Notification Sound
        notification_sound = st.toggle(
            "Notification Sound",
            value=current_settings.get('notification_sound', True)
        )
        
        if st.button("Save Notification Settings"):
            current_settings.update({
                'email_notifications': email_notifications,
                'email_address': email_address if email_notifications else '',
                'push_notifications': push_notifications,
                'notification_sound': notification_sound
            })
            save_settings(current_settings)
            st.success("Notification settings saved!")
    
    # Backup & Restore Tab
    with settings_tabs[3]:
        st.header("Backup & Restore")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Create Backup")
            if st.button("Create New Backup"):
                backup_file = create_backup()
                st.success(f"Backup created successfully: {backup_file}")
                st.download_button(
                    "Download Backup",
                    data=open(backup_file, 'rb'),
                    file_name=backup_file.split('/')[-1],
                    mime='application/octet-stream'
                )
        
        with col2:
            st.subheader("Restore from Backup")
            uploaded_file = st.file_uploader("Choose backup file", type=['zip'])
            if uploaded_file is not None and st.button("Restore from Backup"):
                success = restore_backup(uploaded_file)
                if success:
                    st.success("Backup restored successfully!")
                else:
                    st.error("Failed to restore backup")
    
    # System Info Tab
    with settings_tabs[4]:
        st.header("System Information")
        
        system_info = get_system_info()
        
        # Display system information in an organized way
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Application Info")
            st.write(f"Version: {system_info['app_version']}")
            st.write(f"Python Version: {system_info['python_version']}")
            st.write(f"Streamlit Version: {system_info['streamlit_version']}")
        
        with col2:
            st.subheader("Database Info")
            st.write(f"Database Size: {system_info['db_size']}")
            st.write(f"Number of Records: {system_info['record_count']}")
            st.write(f"Last Backup: {system_info['last_backup']}")
    
    # Logs Tab
    with settings_tabs[5]:
        st.header("System Logs")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            display_logs_in_settings()
        
        with col2:
            if st.button("Clear Old Logs"):
                days = st.number_input("Days to keep", min_value=1, value=7)
                clear_old_logs(days)
                st.success(f"Cleared logs older than {days} days")

if __name__ == "__main__":
    render_settings_page() 