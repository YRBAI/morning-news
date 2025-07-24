# scrapers/__init__.py
"""
Multi-Country News Scraper Package

This package contains scrapers for different countries and news sources.
Each scraper module should implement a fetch_articles() or fetch_all() function.
"""

# Import all scraper modules
try:
    from . import singapore
    print("✓ Singapore scraper loaded")
except ImportError as e:
    print(f"❌ Singapore scraper failed to load: {e}")
    singapore = None

try:
    from . import japan
    print("✓ Japan scraper loaded")
except ImportError as e:
    print(f"❌ Japan scraper failed to load: {e}")
    japan = None

try:
    from . import india
    print("✓ India scraper loaded")
except ImportError as e:
    print(f"❌ India scraper failed to load: {e}")
    india = None

try:
    from . import korea
    print("✓ Korea scraper loaded")
except ImportError as e:
    print(f"❌ Korea scraper failed to load: {e}")
    korea = None

try:
    from . import yahoo
    print("✓ Yahoo Finance scraper loaded")
except ImportError as e:
    print(f"❌ Yahoo Finance scraper failed to load: {e}")
    yahoo = None

try:
    from . import others
    print("✓ Others scraper loaded")
except ImportError as e:
    print(f"❌ Others scraper failed to load: {e}")
    others = None

# List all available scrapers
__all__ = ['singapore', 'japan', 'india', 'korea', 'yahoo', 'others']

# Version info
__version__ = "4.0.0"
__author__ = "News Scraper Team"
__description__ = "Multi-country news scraping system"