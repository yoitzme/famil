import streamlit as st
from utils.database import get_db_connection
import sys
import traceback
from datetime import datetime

def run_diagnostics():
    """
    Run system diagnostics and display detailed error information
    Returns True if all checks pass, False otherwise
    """
    st.subheader("🔍 System Diagnostics")
    
    # Create a table to display diagnostic results
    results = []
    all_passed = True
    
    # Check database connection
    try:
        conn = get_db_connection()
        if conn:
            results.append({
                "Component": "Database Connection",
                "Status": "✅ Passed",
                "Details": "Successfully connected to database",
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Error": None
            })
            conn.close()
        else:
            all_passed = False
            results.append({
                "Component": "Database Connection",
                "Status": "❌ Failed",
                "Details": "Could not establish database connection",
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Error": "Connection returned None"
            })
    except Exception as e:
        all_passed = False
        results.append({
            "Component": "Database Connection",
            "Status": "❌ Failed",
            "Details": f"Database connection error: {str(e)}",
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Error": traceback.format_exc()
        })

    # Check required tables
    try:
        conn = get_db_connection()
        if conn:
            with conn.cursor() as cur:
                required_tables = ['todo_items', 'events', 'meal_plans', 'recipes']
                for table in required_tables:
                    cur.execute(f"""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = %s
                        );
                    """, (table,))
                    exists = cur.fetchone()[0]
                    if exists:
                        results.append({
                            "Component": f"Table Check: {table}",
                            "Status": "✅ Passed",
                            "Details": f"Table '{table}' exists",
                            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "Error": None
                        })
                    else:
                        all_passed = False
                        results.append({
                            "Component": f"Table Check: {table}",
                            "Status": "❌ Failed",
                            "Details": f"Table '{table}' does not exist",
                            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "Error": "Table not found in database"
                        })
            conn.close()
    except Exception as e:
        all_passed = False
        results.append({
            "Component": "Table Checks",
            "Status": "❌ Failed",
            "Details": f"Error checking tables: {str(e)}",
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Error": traceback.format_exc()
        })

    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 7):
        results.append({
            "Component": "Python Version",
            "Status": "✅ Passed",
            "Details": f"Python {python_version.major}.{python_version.minor}.{python_version.micro}",
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Error": None
        })
    else:
        all_passed = False
        results.append({
            "Component": "Python Version",
            "Status": "❌ Failed",
            "Details": f"Python version {python_version.major}.{python_version.minor}.{python_version.micro} is below required 3.7",
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Error": "Incompatible Python version"
        })

    # Display results in an expandable table
    st.write("System Diagnostic Results:")
    
    # Create columns for the table
    cols = st.columns([2, 1, 3, 2, 3])
    cols[0].write("**Component**")
    cols[1].write("**Status**")
    cols[2].write("**Details**")
    cols[3].write("**Timestamp**")
    cols[4].write("**Error**")

    # Display results with alternating background colors
    for idx, result in enumerate(results):
        with st.container():
            if idx % 2 == 0:
                st.markdown("""
                    <style>
                        div[data-testid="stHorizontalBlock"]:nth-of-type({}) {{
                            background-color: rgba(240, 242, 246, 0.5);
                        }}
                    </style>
                """.format(idx + 2), unsafe_allow_html=True)
            
            cols = st.columns([2, 1, 3, 2, 3])
            cols[0].write(result["Component"])
            cols[1].write(result["Status"])
            cols[2].write(result["Details"])
            cols[3].write(result["Timestamp"])
            if result["Error"]:
                with cols[4].expander("Show Error"):
                    st.code(result["Error"])
            else:
                cols[4].write("None")

    # Display overall status
    if all_passed:
        st.success("✅ All system checks passed!")
    else:
        st.error("❌ Some system checks failed. Please review the errors above.")

    return all_passed

if __name__ == "__main__":
    run_diagnostics() 