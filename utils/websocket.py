import asyncio
import json
from datetime import datetime
import streamlit as st
from streamlit.web.server.websocket_headers import _get_websocket_headers

class WebSocketManager:
    def __init__(self):
        self.connections = set()
        self._lock = asyncio.Lock()
        
    async def register(self, websocket):
        async with self._lock:
            self.connections.add(websocket)
        
    async def unregister(self, websocket):
        async with self._lock:
            self.connections.remove(websocket)
        
    async def broadcast(self, message):
        if self.connections:
            message_json = json.dumps(message)
            tasks = []
            async with self._lock:
                for connection in self.connections:
                    try:
                        tasks.append(connection.send(message_json))
                    except Exception:
                        continue
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

    def send_update(self, update_type, data):
        """Synchronous method to send updates."""
        message = {
            "type": update_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        st.session_state['websocket_messages'] = st.session_state.get('websocket_messages', []) + [message]
        st.rerun()

websocket_manager = WebSocketManager()

# Initialize session state for websocket messages
if 'websocket_messages' not in st.session_state:
    st.session_state['websocket_messages'] = []

def process_websocket_messages():
    """Process any pending websocket messages."""
    if 'websocket_messages' in st.session_state and st.session_state['websocket_messages']:
        for message in st.session_state['websocket_messages']:
            # Handle the message based on type
            if message['type'] == 'task_update':
                st.experimental_rerun()
            elif message['type'] == 'notification':
                st.toast(message['data']['message'])
        # Clear processed messages
        st.session_state['websocket_messages'] = []
