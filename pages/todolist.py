import streamlit as st
from datetime import datetime, timedelta
from utils.database import get_db_connection
from utils.helpers import configure_page
from utils.styles import get_mobile_styles
from psycopg2.extras import RealDictCursor
from utils.header import display_header, display_page_title

def main():
    display_header()
    display_page_title("Todo List ✅")
    # Rest of the code...
