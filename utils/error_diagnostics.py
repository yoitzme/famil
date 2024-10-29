import streamlit as st
import os
import psycopg2
import importlib.util
from pathlib import Path
import re
import html.parser

# Optional imports with fallbacks
try:
    import cssutils
    CSSUTILS_AVAILABLE = True
except ImportError:
    CSSUTILS_AVAILABLE = False

try:
    import jsbeautifier
    JSBEAUTIFIER_AVAILABLE = True
except ImportError:
    JSBEAUTIFIER_AVAILABLE = False

class ErrorDiagnostics:
    def __init__(self):
        self.errors = []
        self.warnings = []
        
    def check_all(self):
        """Run all diagnostic checks."""
        self.check_environment_variables()
        self.check_database_connection()
        self.check_required_files()
        self.check_table_structure()
        self.check_module_imports()
        self.check_file_permissions()
        self.check_duplicate_routes()
        self.check_style_conflicts()
        
        # Only run if optional dependencies are available
        if CSSUTILS_AVAILABLE:
            self.check_css_syntax()
        else:
            self.warnings.append("cssutils not installed - skipping CSS syntax validation")
            
        if JSBEAUTIFIER_AVAILABLE:
            self.check_javascript_syntax()
        else:
            self.warnings.append("jsbeautifier not installed - skipping JavaScript syntax validation")
            
        self.check_html_syntax()
        
        return self.get_report()
    
    def check_environment_variables(self):
        """Check if all required environment variables are set."""
        required_vars = ['PGHOST', 'PGDATABASE', 'PGUSER', 'PGPASSWORD', 'PGPORT']
        for var in required_vars:
            if var not in os.environ:
                self.errors.append(f"Missing environment variable: {var}")
    
    def check_database_connection(self):
        """Test database connection and permissions."""
        try:
            conn = psycopg2.connect(
                host=os.environ.get('PGHOST'),
                database=os.environ.get('PGDATABASE'),
                user=os.environ.get('PGUSER'),
                password=os.environ.get('PGPASSWORD'),
                port=os.environ.get('PGPORT')
            )
            conn.close()
        except Exception as e:
            self.errors.append(f"Database connection error: {str(e)}")
    
    def check_required_files(self):
        """Check if all required files exist."""
        required_files = [
            'main.py',
            'utils/database.py',
            'utils/features.py',
            'utils/helpers.py',
            'utils/styles.py',
            'pages/__init__.py'
        ]
        
        for file_path in required_files:
            if not Path(file_path).exists():
                self.errors.append(f"Missing required file: {file_path}")
    
    def check_table_structure(self):
        """Check database table structure."""
        try:
            conn = psycopg2.connect(
                host=os.environ.get('PGHOST'),
                database=os.environ.get('PGDATABASE'),
                user=os.environ.get('PGUSER'),
                password=os.environ.get('PGPASSWORD'),
                port=os.environ.get('PGPORT')
            )
            with conn.cursor() as cur:
                # Check each required table
                tables = ['todo_items', 'grocery_items', 'events', 'meal_plans', 'recipes']
                for table in tables:
                    cur.execute(f"""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = '{table}'
                        );
                    """)
                    if not cur.fetchone()[0]:
                        self.errors.append(f"Missing database table: {table}")
            conn.close()
        except Exception as e:
            self.errors.append(f"Error checking table structure: {str(e)}")
    
    def check_module_imports(self):
        """Check if all required Python modules are available."""
        required_modules = [
            'streamlit',
            'psycopg2',
            'datetime',
            'plotly',
            'pywebpush',
            'asyncio'
        ]
        
        for module in required_modules:
            if not importlib.util.find_spec(module):
                self.errors.append(f"Missing required module: {module}")
    
    def check_file_permissions(self):
        """Check file permissions."""
        files_to_check = [
            'main.py',
            'utils/database.py',
            'pages/__init__.py'
        ]
        
        for file_path in files_to_check:
            path = Path(file_path)
            if path.exists() and not os.access(path, os.R_OK):
                self.errors.append(f"No read permission for file: {file_path}")
    
    def check_duplicate_routes(self):
        """Check for duplicate route definitions."""
        pages_dir = Path('pages')
        if pages_dir.exists():
            routes = []
            for file in pages_dir.glob('*.py'):
                if file.stem.startswith('0'):
                    routes.append(file.stem)
            
            # Check for duplicates
            seen = set()
            for route in routes:
                if route in seen:
                    self.errors.append(f"Duplicate route found: {route}")
                seen.add(route)
    
    def check_style_conflicts(self):
        """Check for potential CSS style conflicts."""
        style_files = [
            'utils/styles.py',
            'main.py'
        ]
        
        css_selectors = set()
        for file_path in style_files:
            if Path(file_path).exists():
                with open(file_path, 'r') as f:
                    content = f.read()
                    if 'stSidebarNav' in content:
                        css_selectors.add('stSidebarNav')
        
        if len(css_selectors) > 1:
            self.warnings.append("Potential style conflicts detected for sidebar navigation")
    
    def check_css_syntax(self):
        """Check CSS syntax in style definitions."""
        if not CSSUTILS_AVAILABLE:
            return
            
        cssutils.log.setLevel(30)  # Suppress info messages
        files_to_check = [
            'main.py',
            'utils/styles.py',
            'pages/06_todo_list.py'
        ]
        
        for file_path in files_to_check:
            if Path(file_path).exists():
                with open(file_path, 'r') as f:
                    content = f.read()
                    # Extract CSS from markdown strings
                    css_blocks = re.findall(r'<style>(.*?)</style>', content, re.DOTALL)
                    
                    for css in css_blocks:
                        try:
                            cssutils.parseString(css)
                        except Exception as e:
                            self.errors.append(f"CSS syntax error in {file_path}: {str(e)}")
                        
                        # Check for common CSS issues
                        if '!important' in css:
                            self.warnings.append(f"Excessive use of !important in {file_path}")
                        
                        # Check for potentially conflicting selectors
                        selectors = re.findall(r'([^\{]+)\{', css)
                        selector_count = {}
                        for selector in selectors:
                            selector = selector.strip()
                            selector_count[selector] = selector_count.get(selector, 0) + 1
                            if selector_count[selector] > 1:
                                self.warnings.append(f"Duplicate CSS selector '{selector}' in {file_path}")

    def check_javascript_syntax(self):
        """Check JavaScript syntax in script tags."""
        if not JSBEAUTIFIER_AVAILABLE:
            return
            
        files_to_check = [
            'main.py',
            'pages/06_todo_list.py'
        ]
        
        for file_path in files_to_check:
            if Path(file_path).exists():
                with open(file_path, 'r') as f:
                    content = f.read()
                    # Extract JavaScript from script tags
                    js_blocks = re.findall(r'<script>(.*?)</script>', content, re.DOTALL)
                    
                    for js in js_blocks:
                        try:
                            # Format JavaScript to check syntax
                            jsbeautifier.beautify(js)
                            
                            # Check for common JavaScript issues
                            if 'var ' in js:
                                self.warnings.append(f"Use of 'var' instead of 'let/const' in {file_path}")
                            
                            if 'eval(' in js:
                                self.warnings.append(f"Use of eval() detected in {file_path}")
                            
                            if 'innerHTML' in js:
                                self.warnings.append(f"Direct innerHTML manipulation in {file_path}")
                        except Exception as e:
                            self.errors.append(f"JavaScript syntax error in {file_path}: {str(e)}")

    def check_html_syntax(self):
        """Check HTML syntax in markdown strings."""
        class HTMLValidator(html.parser.HTMLParser):
            def __init__(self):
                super().__init__()
                self.errors = []
                self.tags = []
            
            def handle_starttag(self, tag, attrs):
                self.tags.append(tag)
            
            def handle_endtag(self, tag):
                if not self.tags or self.tags[-1] != tag:
                    self.errors.append(f"Mismatched HTML tags: expected {self.tags[-1] if self.tags else 'none'}, got {tag}")
                else:
                    self.tags.pop()

        files_to_check = [
            'main.py',
            'pages/06_todo_list.py',
            'pages/03_grocery_list.py'
        ]
        
        for file_path in files_to_check:
            if Path(file_path).exists():
                with open(file_path, 'r') as f:
                    content = f.read()
                    # Extract HTML from markdown strings
                    html_blocks = re.findall(r'st\.markdown\(["\']<.*?>["\']', content, re.DOTALL)
                    
                    for html_content in html_blocks:
                        validator = HTMLValidator()
                        try:
                            validator.feed(html_content)
                            if validator.errors:
                                for error in validator.errors:
                                    self.errors.append(f"HTML syntax error in {file_path}: {error}")
                            if validator.tags:
                                self.errors.append(f"Unclosed HTML tags in {file_path}: {', '.join(validator.tags)}")
                        except Exception as e:
                            self.errors.append(f"HTML parsing error in {file_path}: {str(e)}")

    def get_report(self):
        """Generate diagnostic report."""
        report = {
            'errors': self.errors,
            'warnings': self.warnings,
            'status': 'ok' if not self.errors else 'error'
        }
        return report

def run_diagnostics():
    """Run diagnostics and display results in Streamlit."""
    st.write("Running system diagnostics...")
    
    diagnostics = ErrorDiagnostics()
    report = diagnostics.check_all()
    
    if report['errors']:
        st.error("### Errors Found:")
        for error in report['errors']:
            st.error(f"- {error}")
    
    if report['warnings']:
        st.warning("### Warnings:")
        for warning in report['warnings']:
            st.warning(f"- {warning}")
    
    if report['status'] == 'ok':
        st.success("All systems operational!")
    
    return report['status'] == 'ok'

if __name__ == "__main__":
    run_diagnostics() 