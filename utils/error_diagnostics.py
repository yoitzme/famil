from utils.logger import log_error, log_info, log_warning
import streamlit as st
from utils.database import get_db_connection
import sys
import traceback
from datetime import datetime
import gc
import os
import re
from pathlib import Path

def run_diagnostics():
    """Run comprehensive system diagnostics with memory optimization."""
    log_info("Starting comprehensive system diagnostics")
    st.subheader("🔍 System Diagnostics")
    
    # Clear memory before starting
    gc.collect()
    
    all_results = []
    overall_status = True
    
    # Run checks one at a time to minimize memory usage
    checks = [
        ("Database Structure", check_database_tables),
        ("Input Validation", check_input_validation),
        ("Type Consistency", check_type_consistency)
    ]
    
    for check_name, check_function in checks:
        try:
            st.write(f"Running {check_name} check...")
            log_info(f"Starting {check_name} check")
            
            # Clear memory before each check
            gc.collect()
            
            results, status = check_function()
            if not status:
                overall_status = False
                for result in results:
                    if result["Status"] != "✅ Passed":
                        log_error(f"{result['Component']} check failed", 
                                f"Details: {result['Details']}\nError: {result['Error']}")
            all_results.extend(results)
            
            # Clear results after processing
            del results
            gc.collect()
            
        except Exception as e:
            overall_status = False
            error_details = log_diagnostic_error(check_name, e)
            all_results.append({
                "Component": check_name,
                "Status": "❌ Failed",
                "Details": "Error during check",
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Error": str(e)
            })
    
    # Display results in batches
    display_results_in_batches(all_results, batch_size=10)
    
    return overall_status

def display_results_in_batches(results, batch_size=10):
    """Display diagnostic results in batches to reduce memory usage."""
    for i in range(0, len(results), batch_size):
        batch = results[i:i+batch_size]
        
        for result in batch:
            cols = st.columns([2, 1, 3, 2])
            cols[0].write(result["Component"])
            cols[1].write(result["Status"])
            cols[2].write(result["Details"])
            if result["Error"]:
                with cols[3].expander("Show Error"):
                    st.code(result["Error"])
            
        # Clear batch from memory
        del batch
        gc.collect()

def check_database_tables():
    """Memory-optimized database table checks."""
    results = []
    all_passed = True
    conn = None
    
    try:
        conn = get_db_connection()
        if conn:
            with conn.cursor(name='server_cursor') as cur:
                cur.itersize = 50  # Small batch size
                
                # Process one table at a time
                for table_name in get_table_names(cur):
                    # Clear previous results
                    gc.collect()
                    
                    check_table_structure(cur, table_name, results)
                    
                    # Clear after each table check
                    conn.commit()
                    cur.execute("DISCARD ALL")
    except Exception as e:
        all_passed = False
        results.append({
            "Component": "Database Check",
            "Status": "❌ Failed",
            "Details": "Error during check",
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Error": str(e)
        })
    finally:
        if conn:
            conn.close()
        gc.collect()
    
    return results, all_passed

def get_table_names(cur):
    """Get table names in small batches."""
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE'
    """)
    
    while True:
        batch = cur.fetchmany(10)
        if not batch:
            break
        for row in batch:
            yield row[0]

def check_table_structure(cur, table_name, results):
    """Check single table structure with minimal memory usage."""
    try:
        # Check columns in small batches
        cur.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = %s
        """, (table_name,))
        
        columns = {}
        while True:
            batch = cur.fetchmany(10)
            if not batch:
                break
            for col_name, data_type in batch:
                columns[col_name] = data_type
            
            # Clear batch
            del batch
            gc.collect()
        
        # Process results
        if columns:
            results.append({
                "Component": f"Table Structure: {table_name}",
                "Status": "✅ Passed",
                "Details": f"Found {len(columns)} columns",
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Error": None
            })
        
        # Clear columns
        del columns
        gc.collect()
        
    except Exception as e:
        results.append({
            "Component": f"Table Check: {table_name}",
            "Status": "❌ Failed",
            "Details": f"Error checking table {table_name}",
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Error": str(e)
        })

def check_input_validation():
    """Check if input validation is working correctly."""
    try:
        # Test basic input validation
        test_cases = [
            ("text_input", "Test String", True),
            ("number_input", 42, True),
            ("date_input", "2024-01-01", True),
            ("text_input", "<script>alert('xss')</script>", False),
            ("number_input", "not a number", False),
            ("date_input", "invalid date", False)
        ]
        
        for input_type, test_value, expected_valid in test_cases:
            result = validate_input(input_type, test_value)
            if result != expected_valid:
                return False, f"Input validation failed for {input_type}"
        
        return True, "Input validation checks passed"
        
    except Exception as e:
        return False, f"Input validation check failed: {str(e)}"

def validate_input(input_type, value):
    """Validate input based on type."""
    try:
        if input_type == "text_input":
            # Check for XSS attempts
            if "<script>" in str(value).lower():
                return False
            # Check for reasonable length
            if len(str(value)) > 1000:
                return False
            return True
            
        elif input_type == "number_input":
            # Try to convert to float
            float(value)
            return True
            
        elif input_type == "date_input":
            # Try to parse date
            datetime.strptime(str(value), "%Y-%m-%d")
            return True
            
        return False
        
    except (ValueError, TypeError):
        return False

if __name__ == "__main__":
    run_diagnostics() 