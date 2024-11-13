import streamlit as st
from functools import wraps

def ensure_context():
    """Ensure Streamlit context is properly initialized"""
    if not hasattr(st, '_is_initialized'):
        st._is_initialized = True
        if 'context_ready' not in st.session_state:
            st.session_state.context_ready = True
    return True

def require_context(func):
    """Decorator to ensure Streamlit context is available"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            ensure_context()
            return func(*args, **kwargs)
        except Exception as e:
            # Silently fail in bare mode
            return None
    return wrapper 