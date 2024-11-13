import streamlit as st
from typing import Optional

def get_device_info() -> dict:
    """Get information about the user's device."""
    user_agent = st.get_user_agent()
    return {
        'is_mobile': 'mobile' in user_agent.lower(),
        'is_ios': 'iphone' in user_agent.lower() or 'ipad' in user_agent.lower(),
        'is_android': 'android' in user_agent.lower()
    }

def add_to_home_screen_prompt():
    """Show 'Add to Home Screen' prompt for mobile users."""
    device_info = get_device_info()
    if device_info['is_mobile']:
        if device_info['is_ios']:
            st.info("📱 Tap the share button and select 'Add to Home Screen' for easy access")
        elif device_info['is_android']:
            st.info("📱 Open menu and select 'Add to Home Screen' for easy access")

def optimize_images(image: Optional[bytes], max_size: int = 800) -> Optional[bytes]:
    """Optimize images for mobile viewing."""
    if image:
        from PIL import Image
        import io
        
        # Open image
        img = Image.open(io.BytesIO(image))
        
        # Calculate new size maintaining aspect ratio
        ratio = max_size / max(img.size)
        if ratio < 1:
            new_size = tuple(int(dim * ratio) for dim in img.size)
            img = img.resize(new_size, Image.LANCZOS)
        
        # Save optimized image
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=85, optimize=True)
        return buffer.getvalue()
    return None 