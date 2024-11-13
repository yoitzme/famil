import os
import sys

# Set environment variables before anything else
os.environ['STREAMLIT_SERVER_PORT'] = '5000'
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def run_app():
    import streamlit.web.bootstrap as bootstrap
    flag_options = {
        'server.port': 5000,
        'server.headless': True,
        'browser.serverAddress': '0.0.0.0',
        'server.enableCORS': False,
        'server.enableXsrfProtection': False
    }
    bootstrap.run('main.py', '', flag_options, [])

if __name__ == '__main__':
    run_app() 