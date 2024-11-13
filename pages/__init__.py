# Empty file to make the directory a Python package
import importlib

def load_page(page_name):
    """Load a page module by name."""
    try:
        return importlib.import_module(f"pages.{page_name}")
    except ImportError:
        return None
