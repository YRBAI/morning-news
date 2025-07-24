# config.py - Configuration and Constants

# ─── HEADERS CONFIGURATION ─────────────────────────────────────────
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Charset": "utf-8, iso-8859-1;q=0.5", 
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Cache-Control": "max-age=0"
}

SIMPLE_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
}

# Korean headers for SEdaily
KOREAN_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Charset": "utf-8", 
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

# ─── NEWS SOURCES CONFIGURATION ────────────────────────────────────
SOURCES = {
    'edge_singapore': {
        'base': 'https://www.theedgesingapore.com',
        'urls': [
            'https://www.theedgesingapore.com',  # Try main page first - more likely to have JSON-LD
            'https://www.theedgesingapore.com/news',  # News section
            'https://www.theedgesingapore.com/section/latest',  # Keep as fallback
            'https://www.theedgesingapore.com/section/business'
        ],
        'requires_selenium': True
    },
    'nikkei_japan': {
        'base': "https://asia.nikkei.com",
        'urls': [
            'https://asia.nikkei.com/Location/East-Asia/Japan?page=1',
            'https://asia.nikkei.com/Location/East-Asia/Japan?page=2'
        ],
        'requires_selenium': False
    },
    'hindustantimes_india': {
        'base': "https://www.hindustantimes.com",
        'urls': [
            'https://www.hindustantimes.com/india-news',
            'https://www.hindustantimes.com/india-news/page-2',
            'https://www.hindustantimes.com/india-news/page-3',
            'https://www.hindustantimes.com/india-news/page-4'
        ],
        'requires_selenium': True  # Enhanced to support both methods
    },
    'sedaily_korea': {
        'base': "https://www.sedaily.com",
        'url': 'https://www.sedaily.com/v/NewsMain/GC',  # Add single URL for compatibility
        'urls': ['https://www.sedaily.com/v/NewsMain/GC'],
        'requires_translation': True,
        'translation_from': 'ko',
        'translation_to': 'en',
        'requires_selenium': False
    },
    'yahoo_finance': {
        'base': "https://finance.yahoo.com",
        'urls': [
            'https://uk.finance.yahoo.com/',
            'https://uk.finance.yahoo.com/topic/stocks/',
            'https://finance.yahoo.com/topic/latest-news/'
        ],
        'requires_selenium': False
    },
    'tradewinds': {
        'base': "https://www.tradewindsnews.com",
        'latest': "/latest",  # Add this key for others.py compatibility
        'urls': ["https://www.tradewindsnews.com/latest"],
        'requires_selenium': False
    },
    'trendforce': {
        'base': "https://www.trendforce.com",
        'news': "/news/",  # Add this key for others.py compatibility
        'urls': ["https://www.trendforce.com/news/"],
        'requires_selenium': False
    },
    'udn': {
        'base': "https://money.udn.com",
        'rank': "/rank/newest/1001/0/1",  # Add this key for others.py compatibility
        'urls': ["https://money.udn.com/rank/newest/1001/0/1"],
        'requires_translation': True,
        'translation_from': 'zh',
        'translation_to': 'en',
        'requires_selenium': False
    },
    'gmk': {
        'base': "https://gmk.center",
        'news': "/en/news/",  # Add this key for others.py compatibility
        'urls': ["https://gmk.center/en/news/"],
        'requires_selenium': False
    },
    'bloomberg': {
        'base': "https://www.bloomberg.com",
        'api': "/lineup-next/api/stories",  # Changed from 'api_url' to 'api'
        'urls': ["https://www.bloomberg.com/lineup-next/api/stories"],
        'is_api': True,
        'requires_selenium': False
    },
    'business_times': {
        'base': "https://www.businesstimes.com.sg",
        'urls': ["https://www.businesstimes.com.sg/singapore/economy-policy"],
        'requires_selenium': False
    },
    'straits_times': {
        'base': "https://www.straitstimes.com",
        'urls': ["https://www.straitstimes.com/singapore/latest"],
        'requires_selenium': False
    },
    'yahoo_finance_sg': {
        'base': "https://sg.finance.yahoo.com",
        'urls': ["https://sg.finance.yahoo.com/topic/singapore/"],
        'requires_selenium': False
    }
}

# ─── CONFIGURATION PARAMETERS ──────────────────────────────────────
CONFIG = {
    'max_retries': 5,
    'retry_delay': 30,
    'request_delay': 2,
    'timeout': 15,
    'max_pages': 3,
    'output_dir': '~/Desktop/news_collection',
    'excel_filename_format': 'daily_news_%Y%m%d.xlsx',
    'date_format': '%Y-%m-%d %H:%M:%S',
    'max_workers': 4  # For concurrent processing
}

# ─── SELENIUM CONFIGURATION ────────────────────────────────────────
# Initialize Selenium-related variables
SELENIUM_AVAILABLE = False
WEBDRIVER_MANAGER_AVAILABLE = False
webdriver = None
Options = None
By = None
WebDriverWait = None
EC = None
Service = None
ChromeDriverManager = None

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    SELENIUM_AVAILABLE = True
    
    try:
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        WEBDRIVER_MANAGER_AVAILABLE = True
    except ImportError:
        WEBDRIVER_MANAGER_AVAILABLE = False
        print("Warning: WebDriver Manager not available. Manual ChromeDriver setup required.")
    
except ImportError as e:
    print(f"Warning: Selenium not available. Sources requiring Selenium will be skipped. Error: {e}")

# Selenium Chrome options
def get_chrome_options():
    """Get Chrome options for Selenium"""
    if not SELENIUM_AVAILABLE:
        return None
    
    options = Options()
    
    # Basic options
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    
    # Anti-detection measures
    options.add_argument(f'--user-agent={HEADERS["User-Agent"]}')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Additional performance options
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-plugins')
    options.add_argument('--disable-images')
    options.add_argument('--disable-javascript')  # Can be removed if JS is needed
    options.add_argument('--disable-background-timer-throttling')
    options.add_argument('--disable-renderer-backgrounding')
    options.add_argument('--disable-backgrounding-occluded-windows')
    
    return options

def setup_chrome_driver():
    """Setup Chrome driver with improved configuration and anti-detection measures"""
    if not SELENIUM_AVAILABLE:
        print("❌ Selenium not available")
        return None
    
    try:
        # Get Chrome options
        chrome_options = get_chrome_options()
        if not chrome_options:
            return None
        
        driver = None
        
        # Method 1: Try WebDriver Manager first (recommended)
        if WEBDRIVER_MANAGER_AVAILABLE:
            try:
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
                print("✓ Chrome driver setup with WebDriver Manager")
            except Exception as e:
                print(f"WebDriver Manager failed: {e}")
        
        # Method 2: Try system ChromeDriver as fallback
        if not driver:
            try:
                driver = webdriver.Chrome(options=chrome_options)
                print("✓ Chrome driver setup with system ChromeDriver")
            except Exception as e:
                print(f"System ChromeDriver failed: {e}")
                print("💡 Try installing ChromeDriver manually or run: pip install webdriver-manager")
                return None
        
        # Configure anti-detection measures
        try:
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": HEADERS["User-Agent"]
            })
        except Exception:
            pass  # Anti-detection measures are optional
        
        return driver
        
    except Exception as e:
        print(f"❌ Chrome driver setup failed: {e}")
        return None

# ─── VALIDATION FUNCTIONS ───────────────────────────────────────────
def validate_config():
    """Validate configuration settings"""
    errors = []
    
    # Check required config values
    required_configs = ['max_retries', 'timeout', 'request_delay']
    for key in required_configs:
        if key not in CONFIG:
            errors.append(f"Missing required config: {key}")
        elif not isinstance(CONFIG[key], (int, float)) or CONFIG[key] <= 0:
            errors.append(f"Config {key} must be a positive number")
    
    # Check sources configuration
    for source_name, source_config in SOURCES.items():
        if 'urls' not in source_config:
            errors.append(f"Source {source_name} missing 'urls' configuration")
        elif not isinstance(source_config['urls'], list):
            errors.append(f"Source {source_name} 'urls' must be a list")
        elif not source_config['urls']:
            errors.append(f"Source {source_name} 'urls' cannot be empty")
        
        # Check if source requires Selenium but Selenium is not available
        if source_config.get('requires_selenium', False) and not SELENIUM_AVAILABLE:
            print(f"Warning: Source {source_name} requires Selenium but Selenium is not available")
    
    if errors:
        raise ValueError(f"Configuration validation failed:\n" + "\n".join(errors))
    
    return True

def get_sources_by_country():
    """Get sources organized by country for easier management"""
    return {
        'singapore': ['edge_singapore', 'business_times', 'straits_times', 'yahoo_finance_sg'],
        'japan': ['nikkei_japan'],
        'india': ['hindustantimes_india'],
        'korea': ['sedaily_korea'],
        'yahoo': ['yahoo_finance'],  # Added Yahoo as separate category
        'taiwan': ['udn'],
        'international': ['tradewinds', 'trendforce', 'gmk', 'bloomberg']
    }

def get_sources_requiring_selenium():
    """Get list of sources that require Selenium"""
    return [name for name, config in SOURCES.items() if config.get('requires_selenium', False)]

def get_sources_requiring_translation():
    """Get list of sources that require translation"""
    return [name for name, config in SOURCES.items() if config.get('requires_translation', False)]

# ─── INITIALIZATION ─────────────────────────────────────────────────
# Validate configuration on import
try:
    validate_config()
    print("✓ Configuration validation passed")
except ValueError as e:
    print(f"✗ Configuration validation failed: {e}")
    
# Check Selenium availability for sources that need it
selenium_sources = get_sources_requiring_selenium()
if selenium_sources and not SELENIUM_AVAILABLE:
    print(f"⚠ Warning: The following sources require Selenium but it's not available: {', '.join(selenium_sources)}")
    print("  Install with: pip install selenium webdriver-manager")