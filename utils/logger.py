import logging
import os
from datetime import datetime
import streamlit as st
from pathlib import Path

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Configure logging
def setup_logger():
    """Configure and return the logger."""
    logger = logging.getLogger('FamilyHub')
    
    if not logger.handlers:  # Prevent duplicate handlers
        logger.setLevel(logging.DEBUG)
        
        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s'
        )
        console_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        
        # File handler for detailed logs
        log_file = LOGS_DIR / f"family_hub_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        
        # Console handler for important messages
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        
        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger

# Create logger instance
logger = setup_logger()

def log_error(error, context=None, show_notification=True):
    """Log an error with context and optionally show a notification."""
    error_msg = f"Error: {str(error)}"
    if context:
        error_msg = f"{error_msg} | Context: {context}"
    logger.error(error_msg, exc_info=True)
    
    if show_notification:
        # Store error in session state for display
        if 'error_log' not in st.session_state:
            st.session_state.error_log = []
        
        error_entry = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'error': error_msg,
            'context': context,
            'id': f"error_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"  # Add unique ID
        }
        st.session_state.error_log.append(error_entry)
        
        # Show error notification
        st.error(f"Error occurred: {error_msg}")
        
        # Add download button for latest logs with unique key
        log_file = LOGS_DIR / f"family_hub_{datetime.now().strftime('%Y%m%d')}.log"
        if log_file.exists():
            with open(log_file, 'r') as f:
                log_contents = f.read()
            # Use error entry ID for unique key
            st.download_button(
                "Download Error Log",
                log_contents,
                file_name=f"error_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                key=error_entry['id']
            )

def log_warning(message, context=None, show_notification=True):
    """Log a warning with context and optionally show a notification."""
    warning_msg = f"Warning: {message}"
    if context:
        warning_msg = f"{warning_msg} | Context: {context}"
    logger.warning(warning_msg)
    
    if show_notification:
        if 'warning_log' not in st.session_state:
            st.session_state.warning_log = []
        st.session_state.warning_log.append({
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'message': warning_msg,
            'context': context
        })
        st.warning(warning_msg)

def log_info(message, context=None, show_notification=False):
    """Log an info message with context and optionally show a notification."""
    info_msg = message
    if context:
        info_msg = f"{info_msg} | Context: {context}"
    logger.info(info_msg)
    
    if show_notification:
        if 'info_log' not in st.session_state:
            st.session_state.info_log = []
        st.session_state.info_log.append({
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'message': info_msg,
            'context': context
        })
        st.info(info_msg)

def display_logs_in_settings():
    """Display recent logs in the settings page."""
    st.subheader("Recent Logs")
    
    try:
        # Get most recent log file
        log_files = sorted(LOGS_DIR.glob("*.log"), key=os.path.getmtime, reverse=True)
        if log_files:
            latest_log = log_files[0]
            with open(latest_log, 'r') as f:
                logs = f.readlines()
            
            # Display last 50 lines by default
            num_lines = st.slider("Number of log lines to display", 10, 100, 50)
            logs = logs[-num_lines:]
            
            # Filter options
            log_levels = st.multiselect(
                "Filter by log level",
                ["ERROR", "WARNING", "INFO", "DEBUG"],
                default=["ERROR", "WARNING"]
            )
            
            # Display filtered logs
            for log in logs:
                if any(level in log for level in log_levels):
                    if "ERROR" in log:
                        st.error(log.strip())
                    elif "WARNING" in log:
                        st.warning(log.strip())
                    elif "INFO" in log:
                        st.info(log.strip())
                    else:
                        st.text(log.strip())
            
            # Add download button for full logs with unique key
            button_key = f"download_full_logs_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            st.download_button(
                "Download Full Logs",
                "\n".join(logs),
                file_name=f"full_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                key=button_key
            )
        else:
            st.info("No logs found")
    except Exception as e:
        st.error(f"Error displaying logs: {str(e)}")

def clear_old_logs(days=7):
    """Clear logs older than specified days."""
    try:
        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
        for log_file in LOGS_DIR.glob("*.log"):
            if log_file.stat().st_mtime < cutoff:
                log_file.unlink()
        log_info(f"Cleared logs older than {days} days")
    except Exception as e:
        log_error(e, "Error clearing old logs")

def get_recent_errors():
    """Get recent errors from the session state."""
    return st.session_state.get('error_log', [])

def get_recent_warnings():
    """Get recent warnings from the session state."""
    return st.session_state.get('warning_log', [])

def clear_log_notifications():
    """Clear log notifications from session state."""
    if 'error_log' in st.session_state:
        del st.session_state.error_log
    if 'warning_log' in st.session_state:
        del st.session_state.warning_log 