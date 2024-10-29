import streamlit as st
from utils.database import get_db_connection
from utils.database_migration import update_database_schema

if __name__ == "__main__":
    update_database_schema()
