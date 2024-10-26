import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.database import get_db_connection
from utils.helpers import configure_page, format_date
from psycopg2.extras import RealDictCursor

configure_page()

# Rest of the imports and configuration...
[Previous code from lines 1-367 remains the same]

                            with col3:
                                st.write(item.get('unit', 'piece'))  # Default to 'piece' if unit is missing
                            with col4:
                                if st.button("✅", key=f"buy_{item['id']}"):
                                    cur.execute("""
                                        UPDATE grocery_items 
                                        SET purchased = TRUE 
                                        WHERE id = %s
                                    """, (item['id'],))
                                    conn.commit()
                                    st.rerun()
                    except Exception as e:
                        st.error(f"Error managing grocery list: {str(e)}")
                    finally:
                        conn.close()

[Rest of the file remains the same]
