def get_consolidated_styles():
    """Consolidate all styles to prevent conflicts and duplicates."""
    return """
    <style>
        /* Reset and Base Styles */
        :root {
            --primary-color: #FF4B4B;
            --secondary-color: #FF8F00;
            --bg-primary: #0E1117;
            --bg-secondary: #262730;
            --text-primary: #FFFFFF;
            --text-secondary: #9CA3AF;
        }

        /* Global Reset */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        /* Streamlit Overrides - Using Specificity Instead of !important */
        body .stApp {
            background-color: var(--bg-primary);
            color: var(--text-primary);
        }

        /* Layout Structure */
        body .main .block-container {
            padding-top: 5rem;
            max-width: none;
        }

        /* Navigation */
        body [data-testid="stSidebarNav"] {
            position: fixed;
            left: 0;
            top: 0;
            height: 100vh;
            background: var(--bg-secondary);
            z-index: 99;
        }

        /* Tab System */
        body .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
            flex-wrap: wrap;
        }

        /* Mobile Optimizations */
        @media (max-width: 768px) {
            body .main .block-container {
                padding: 1rem;
            }
            
            body .stTabs [data-baseweb="tab"] {
                padding: 0.5rem;
            }
        }
    </style>
    """

def get_base_styles():
    """Get base application styles."""
    return """
    <style>
        /* Base Theme */
        :root {
            --primary-color: #FF4B4B;
            --secondary-color: #FF8F00;
            --bg-primary: #0E1117;
            --bg-secondary: #262730;
            --text-primary: #FFFFFF;
            --text-secondary: #9CA3AF;
        }

        /* Layout */
        .main .block-container {
            padding: 2rem 1rem !important;
            max-width: none !important;
        }

        /* Components */
        .stButton button {
            width: 100%;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            border: none;
            font-weight: 500;
        }

        /* Cards */
        .card {
            background: var(--bg-secondary);
            border-radius: 12px;
            padding: 1rem;
            margin: 1rem 0;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
    </style>
    """

def get_mobile_styles():
    """Get mobile-specific styles."""
    return """
    <style>
        /* Mobile Form */
        body #root .stApp .mobile-form {
            padding: 1rem;
            background: var(--bg-secondary);
            border-radius: 12px;
            margin-bottom: 1rem;
        }

        /* Mobile List */
        body #root .stApp .mobile-friendly-list {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }

        body #root .stApp .list-item {
            background: var(--bg-secondary);
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid var(--primary-color);
        }

        /* Mobile Navigation */
        @media (max-width: 768px) {
            body #root .stApp .stTabs [data-baseweb="tab-list"] {
                flex-wrap: nowrap;
                overflow-x: auto;
                scrollbar-width: none;
            }

            body #root .stApp .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
                display: none;
            }

            body #root .stApp .stTabs [data-baseweb="tab"] {
                white-space: nowrap;
            }
        }
    </style>
    """

def get_panel_styles():
    """Get panel-specific styles."""
    return """
    <style>
        .panel {
            background: var(--bg-secondary);
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .panel-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .panel-title {
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--text-primary);
        }
    </style>
    """

