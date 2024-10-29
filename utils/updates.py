import asyncio
from utils.websocket import websocket_manager

def send_update(update_type, data):
    """Send real-time update to all connected clients."""
    websocket_manager.send_update(update_type, data)

def notify_all(title, message, priority="normal"):
    """Send notification to all connected clients."""
    websocket_manager.send_update("notification", {
        "title": title,
        "message": message,
        "priority": priority
    })
