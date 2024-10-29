import streamlit as st
from datetime import datetime
import json
import os

class ErrorRecovery:
    def __init__(self):
        self.error_log = []
        self.recovery_actions = {
            'database_connection': self.recover_database_connection,
            'file_permission': self.recover_file_permission,
            'style_conflict': self.recover_style_conflict
        }
    
    def log_error(self, error_type, details, recovery_attempted=False):
        """Log error with timestamp and recovery status."""
        self.error_log.append({
            'timestamp': datetime.now().isoformat(),
            'type': error_type,
            'details': str(details),
            'recovery_attempted': recovery_attempted
        })
        
        # Save to persistent storage
        self.save_error_log()
    
    def recover_database_connection(self):
        """Attempt to recover database connection."""
        try:
            if 'db_pool' in st.session_state:
                del st.session_state['db_pool']
            return init_connection_pool()
        except Exception as e:
            self.log_error('database_recovery_failed', str(e))
            return False
    
    def recover_style_conflict(self):
        """Reset and reload styles."""
        try:
            st.markdown(get_consolidated_styles(), unsafe_allow_html=True)
            return True
        except Exception as e:
            self.log_error('style_recovery_failed', str(e))
            return False
    
    def save_error_log(self):
        """Save error log to file."""
        try:
            with open('error_log.json', 'w') as f:
                json.dump(self.error_log, f, indent=2)
        except Exception as e:
            st.error(f"Failed to save error log: {str(e)}")

error_recovery = ErrorRecovery() 