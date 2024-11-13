import json
import os
from pathlib import Path

SETTINGS_FILE = Path("config/settings.json")

def load_settings():
    """Load settings from JSON file."""
    if not SETTINGS_FILE.exists():
        return get_default_settings()
    
    try:
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return get_default_settings()

def save_settings(settings):
    """Save settings to JSON file."""
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)

def reset_settings():
    """Reset settings to default values."""
    save_settings(get_default_settings())

def get_default_settings():
    """Get default settings."""
    return {
        'theme': 'light',
        'font_size': 16,
        'compact_mode': False,
        'email_notifications': False,
        'email_address': '',
        'push_notifications': True,
        'notification_sound': True
    }

def get_theme_options():
    """Get available theme options."""
    return ['light', 'dark', 'custom'] 