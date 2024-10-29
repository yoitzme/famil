# Empty file to make the directory a Python package
import importlib

def load_page(page_number):
    """Load a numbered page module."""
    try:
        return importlib.import_module(f"pages.{page_number:02d}")
    except ImportError:
        return None
