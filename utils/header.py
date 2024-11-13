import streamlit as st

def display_header():
    """Display the animated Family Hub Dashboard header."""
    st.markdown("""
        <style>
            /* Header container */
            .dashboard-header {
                text-align: center;
                padding: 2rem;
                background: linear-gradient(90deg, rgba(255,75,75,0.1) 0%, rgba(255,143,0,0.1) 100%);
                border-radius: 10px;
                margin: 1rem 0 3rem 0;
                position: relative;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                border: 1px solid rgba(255,255,255,0.1);
                clear: both;
                display: block;
                width: 100%;
            }
            
            /* Title styling */
            .main-title {
                font-size: 2.5rem;
                font-weight: bold;
                background: linear-gradient(45deg, #FF4B4B, #FF8F00);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 1rem;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
                line-height: 1.4;
                display: block;
            }
            
            /* Subtitle styling */
            .subtitle {
                font-size: 1.2rem;
                color: #9CA3AF;
                animation: fadeInOut 4s infinite;
                display: block;
                margin-top: 0.5rem;
                clear: both;
            }
            
            /* Animation */
            @keyframes fadeInOut {
                0%, 100% { opacity: 0; transform: translateY(-10px); }
                20%, 80% { opacity: 1; transform: translateY(0); }
            }
            
            /* Page title styling */
            .page-title {
                font-size: 1.8rem;
                font-weight: bold;
                color: #FFFFFF;
                margin: 2rem 0;
                padding: 1rem 0;
                border-bottom: 2px solid rgba(255,255,255,0.1);
                clear: both;
                display: block;
                width: 100%;
            }
            
            /* Fix streamlit elements spacing */
            .stMarkdown {
                margin-bottom: 1rem;
            }
            
            .element-container {
                margin-bottom: 1rem;
            }
            
            /* Ensure proper spacing between elements */
            .block-container {
                padding-top: 2rem;
                padding-bottom: 2rem;
            }
            
            /* Fix for overlapping elements */
            div[data-testid="stVerticalBlock"] > div {
                margin-bottom: 1rem;
            }
        </style>
        
        <div class="dashboard-header">
            <h1 class="main-title">🏠 Family Hub Dashboard</h1>
            <p class="subtitle">Organizing Family Life Together</p>
        </div>
    """, unsafe_allow_html=True)

def display_page_title(title):
    """Display a consistent page title."""
    st.markdown(f'<h1 class="page-title">{title}</h1>', unsafe_allow_html=True)