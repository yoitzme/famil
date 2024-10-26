from datetime import datetime, timedelta
import streamlit as st
from typing import List, Dict, Any

def create_notification(conn, user_id: str, message: str, notification_type: str, priority: int = 1) -> bool:
    """Create a new notification in the database."""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO notifications (user_id, message, type, priority)
                VALUES (%s, %s, %s, %s)
            """, (user_id, message, notification_type, priority))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error creating notification: {str(e)}")
        return False

def get_notifications(conn, user_id: str, limit: int = 10, unread_only: bool = False) -> List[Dict[str, Any]]:
    """Get notifications for a user."""
    try:
        with conn.cursor() as cur:
            query = """
                SELECT notification_id, message, type, created_at, read_status, priority
                FROM notifications
                WHERE user_id = %s
            """
            if unread_only:
                query += " AND read_status = FALSE"
            query += " ORDER BY created_at DESC LIMIT %s"
            
            cur.execute(query, (user_id, limit))
            notifications = cur.fetchall()
            
            return [{
                'id': n[0],
                'message': n[1],
                'type': n[2],
                'created_at': n[3],
                'read_status': n[4],
                'priority': n[5]
            } for n in notifications]
    except Exception as e:
        st.error(f"Error fetching notifications: {str(e)}")
        return []

def mark_notification_as_read(conn, notification_id: int) -> bool:
    """Mark a notification as read."""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE notifications
                SET read_status = TRUE
                WHERE notification_id = %s
            """, (notification_id,))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error updating notification: {str(e)}")
        return False

def get_unread_count(conn, user_id: str) -> int:
    """Get count of unread notifications for a user."""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*)
                FROM notifications
                WHERE user_id = %s AND read_status = FALSE
            """, (user_id,))
            return cur.fetchone()[0]
    except Exception as e:
        st.error(f"Error counting notifications: {str(e)}")
        return 0

def check_and_create_notifications(conn):
    """Check for events and create notifications if needed."""
    tomorrow = datetime.now().date() + timedelta(days=1)
    
    # Check calendar events
    with conn.cursor() as cur:
        cur.execute("""
            SELECT title, start_date 
            FROM events 
            WHERE start_date = %s
        """, (tomorrow,))
        events = cur.fetchall()
        
        for event in events:
            message = f"Reminder: '{event[0]}' is tomorrow"
            create_notification(conn, "family", message, "event", priority=2)
    
    # Check due chores
    with conn.cursor() as cur:
        cur.execute("""
            SELECT task, assigned_to 
            FROM chores 
            WHERE due_date = %s AND completed = FALSE
        """, (tomorrow,))
        chores = cur.fetchall()
        
        for chore in chores:
            message = f"Chore due tomorrow: {chore[0]} (Assigned to: {chore[1]})"
            create_notification(conn, chore[1].lower(), message, "chore", priority=2)
    
    # Check school events
    with conn.cursor() as cur:
        cur.execute("""
            SELECT title
            FROM school_events 
            WHERE event_date = %s
        """, (tomorrow,))
        school_events = cur.fetchall()
        
        for event in school_events:
            message = f"School event tomorrow: {event[0]}"
            create_notification(conn, "family", message, "school", priority=3)

def get_notification_color(priority: int) -> str:
    """Get color based on notification priority."""
    colors = {
        1: "#B8E2F2",  # Light blue - low priority
        2: "#FFE4B5",  # Light orange - medium priority
        3: "#FFB6C1",  # Light red - high priority
    }
    return colors.get(priority, "#FFFFFF")
