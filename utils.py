# utils.py - Enhanced Utility Functions (Debugged Version)

import requests
import time
import sys
import os
import re
import platform
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse
import logging

# ─── UTF-8 ENVIRONMENT SETUP ──────────────────────────────────────
def ensure_utf8_environment():
    """Ensure UTF-8 encoding for the application"""
    # Set environment variables for UTF-8
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    # For Windows console
    if sys.platform.startswith('win'):
        try:
            # Try to set console to UTF-8
            os.system('chcp 65001 > nul 2>&1')
        except:
            pass
    
    # Set default encoding
    if hasattr(sys, 'setdefaultencoding'):
        sys.setdefaultencoding('utf-8')

def safe_encode_text(text):
    """Safely encode text to handle various character sets"""
    if not text:
        return ""
    
    if isinstance(text, bytes):
        try:
            return text.decode('utf-8')
        except UnicodeDecodeError:
            try:
                return text.decode('latin-1')
            except UnicodeDecodeError:
                return text.decode('utf-8', errors='ignore')
    
    return str(text)

def make_utf8_request(url, headers=None, timeout=15):
    """Make HTTP request with proper UTF-8 handling"""
    if headers is None:
        try:
            from config import HEADERS
            headers = HEADERS.copy()
        except ImportError:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Charset': 'utf-8, iso-8859-1;q=0.5'
            }
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        
        # Ensure UTF-8 encoding
        if response.encoding.lower() != 'utf-8':
            response.encoding = 'utf-8'
        
        return response
        
    except Exception as e:
        print(f"Request failed for {url}: {e}")
        return None

def safe_write_file(filepath, content, encoding='utf-8'):
    """Safely write file with UTF-8 encoding"""
    try:
        with open(filepath, 'w', encoding=encoding, newline='') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error writing file {filepath}: {e}")
        return False

def safe_read_file(filepath, encoding='utf-8'):
    """Safely read file with UTF-8 encoding"""
    try:
        with open(filepath, 'r', encoding=encoding) as f:
            return f.read()
    except UnicodeDecodeError:
        # Fallback to other encodings
        for fallback_encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
            try:
                with open(filepath, 'r', encoding=fallback_encoding) as f:
                    return f.read()
            except:
                continue
        # Last resort - ignore errors
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return ""

def parse_with_utf8(html_content):
    """Parse HTML content with proper UTF-8 handling"""
    try:
        from bs4 import BeautifulSoup
        
        # Ensure content is UTF-8
        if isinstance(html_content, bytes):
            html_content = html_content.decode('utf-8', errors='ignore')
        
        # Parse with UTF-8 parser
        soup = BeautifulSoup(html_content, 'html.parser', from_encoding='utf-8')
        return soup
    except ImportError:
        print("Warning: BeautifulSoup4 not available")
        return None

# Optional imports with fallback handling
try:
    from bs4 import BeautifulSoup, NavigableString
    HAS_BS4 = True
except ImportError:
    print("Warning: BeautifulSoup4 not installed. Web scraping functionality will be limited.")
    HAS_BS4 = False

try:
    from deep_translator import GoogleTranslator
    HAS_TRANSLATOR = True
except ImportError:
    print("Warning: deep_translator not installed. Translation functionality will be disabled.")
    HAS_TRANSLATOR = False

try:
    import chardet
    HAS_CHARDET = True
except ImportError:
    HAS_CHARDET = False

# Import config with error handling
try:
    from config import HEADERS, CONFIG, SOURCES
except ImportError:
    print("Warning: config.py not found. Using default configurations.")
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Charset': 'utf-8, iso-8859-1;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    CONFIG = {
        'timeout': 30,
        'request_delay': 1,
        'output_dir': None,
        'excel_filename_format': 'daily_news_%Y%m%d.xlsx'
    }
    SOURCES = {}

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Optional imports with fallback handling
try:
    from bs4 import BeautifulSoup, NavigableString
    HAS_BS4 = True
except ImportError:
    print("Warning: BeautifulSoup4 not installed. Web scraping functionality will be limited.")
    HAS_BS4 = False

try:
    from deep_translator import GoogleTranslator
    HAS_TRANSLATOR = True
except ImportError:
    print("Warning: deep_translator not installed. Translation functionality will be disabled.")
    HAS_TRANSLATOR = False

try:
    import chardet
    HAS_CHARDET = True
except ImportError:
    HAS_CHARDET = False

# Import config with error handling
try:
    from config import HEADERS, CONFIG, SOURCES
except ImportError:
    print("Warning: config.py not found. Using default configurations.")
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    CONFIG = {
        'timeout': 30,
        'request_delay': 1,
        'output_dir': None,
        'excel_filename_format': 'daily_news_%Y%m%d.xlsx'
    }
    SOURCES = {}

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ─── FILE HANDLING UTILITIES ───────────────────────────────────────
def get_executable_dir():
    """Get the directory where the executable is located"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return os.path.dirname(sys.executable)
    else:
        # Running as script
        return os.path.dirname(os.path.abspath(__file__))

def get_desktop_path():
    """Get Desktop path for different operating systems"""
    try:
        system = platform.system()
        home_dir = Path.home()
        
        if system == "Windows":
            # Try Windows-specific Desktop locations
            desktop_paths = [
                home_dir / "Desktop",
                home_dir / "OneDrive" / "Desktop",  # OneDrive Desktop
                Path(os.environ.get('USERPROFILE', '')) / "Desktop"
            ]
        elif system == "Darwin":  # macOS
            desktop_paths = [home_dir / "Desktop"]
        else:  # Linux and others
            desktop_paths = [
                home_dir / "Desktop",
                home_dir / "desktop"  # Some Linux distros use lowercase
            ]
        
        # Return first existing Desktop path
        for desktop_path in desktop_paths:
            if desktop_path.exists():
                return str(desktop_path)
        
        # Fallback to home directory if no Desktop found
        logger.warning("Desktop folder not found, using home directory")
        return str(home_dir)
        
    except Exception as e:
        logger.error(f"Error finding Desktop path: {e}")
        return str(Path.home())

def get_output_directory():
    """Get or create output directory for results"""
    try:
        # Use configured output directory or default to Desktop
        if CONFIG.get('output_dir'):
            output_dir = Path(CONFIG['output_dir']).expanduser()
        else:
            desktop_dir = get_desktop_path()
            output_dir = Path(desktop_dir) / "news_collection"
        
        # Create directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if not output_dir.exists():
            raise OSError(f"Failed to create directory: {output_dir}")
            
        logger.info(f"Output directory ready: {output_dir}")
        return str(output_dir)
        
    except Exception as e:
        logger.error(f"Error setting up output directory: {e}")
        # Fallback to current directory
        fallback_dir = Path.cwd() / "news_collection"
        fallback_dir.mkdir(exist_ok=True)
        logger.info(f"Using fallback directory: {fallback_dir}")
        return str(fallback_dir)

def get_output_filepath():
    """Generate full path for output Excel file"""
    try:
        output_dir = get_output_directory()
        filename_format = CONFIG.get('excel_filename_format', 'daily_news_%Y%m%d.xlsx')
        excel_filename = datetime.now().strftime(filename_format)
        excel_path = Path(output_dir) / excel_filename
        return str(excel_path)
    except Exception as e:
        logger.error(f"Error generating output filepath: {e}")
        # Fallback filename
        fallback_filename = f"daily_news_{datetime.now().strftime('%Y%m%d')}.xlsx"
        return str(Path.cwd() / fallback_filename)

# ─── TIME UTILITIES ─────────────────────────────────────────────────
def get_collection_hours():
    """Determine collection period based on current day"""
    current_day = datetime.now().weekday()  # Monday=0, Sunday=6
    # Monday: 72h (weekend catch-up), others: 24h
    hours = 72 if current_day == 0 else 24
    logger.info(f"Collection period: {hours} hours ({'Weekend catch-up' if hours == 72 else 'Regular daily'})")
    return hours

def parse_relative_time(timestamp_text):
    """Enhanced parsing of relative time expressions to hours"""
    if not timestamp_text:
        return None
    
    # Clean the text
    text = str(timestamp_text).lower().strip()
    
    # Enhanced patterns for "X time ago"
    patterns = [
        (r'(\d+)\s*seconds?\s+ago', lambda x: int(x) / 3600),  # Convert to hours
        (r'(\d+)\s*mins?\s+ago', lambda x: int(x) / 60),
        (r'(\d+)\s*minutes?\s+ago', lambda x: int(x) / 60),
        (r'(\d+)\s*hrs?\s+ago', lambda x: int(x)),
        (r'(\d+)\s*hours?\s+ago', lambda x: int(x)),
        (r'(\d+)\s*days?\s+ago', lambda x: int(x) * 24),
        (r'(\d+)\s*weeks?\s+ago', lambda x: int(x) * 24 * 7),
        (r'(\d+)\s*months?\s+ago', lambda x: int(x) * 24 * 30),
        
        # Additional Hindi/English patterns for Indian news sites
        (r'(\d+)\s*घंटे\s+पहले', lambda x: int(x)),  # Hindi: hours ago
        (r'(\d+)\s*मिनट\s+पहले', lambda x: int(x) / 60),  # Hindi: minutes ago
        (r'(\d+)\s*दिन\s+पहले', lambda x: int(x) * 24),  # Hindi: days ago
        
        # ISO format timestamps
        (r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', lambda x: parse_iso_timestamp(x)),
        
        # Common time formats
        (r'(\d{1,2}:\d{2}\s*(AM|PM))', lambda x: parse_time_today(x)),
        (r'(\d{1,2}/\d{1,2}/\d{4})', lambda x: parse_date_format(x)),
        (r'(\d{1,2}-\d{1,2}-\d{4})', lambda x: parse_date_format(x, separator='-')),
    ]
    
    for pattern, converter in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return converter(match.group(1))
            except (ValueError, TypeError):
                continue
    
    # Handle special cases with more variations
    special_cases = {
        'just now': 0,
        'a moment ago': 0,
        'few seconds ago': 0,
        'a minute ago': 1/60,
        'an hour ago': 1,
        'today': 0,
        'this morning': 6,  # Assume 6 hours ago if morning
        'this afternoon': 3,  # Assume 3 hours ago if afternoon
        'this evening': 1,   # Assume 1 hour ago if evening
        'yesterday': 24,
        'a day ago': 24,
        'last night': 12,
        'this week': 24 * 3,  # 3 days ago
        'last week': 24 * 7,
        'a week ago': 24 * 7,
    }
    
    for phrase, hours in special_cases.items():
        if phrase in text:
            return hours
    
    return None

def parse_iso_timestamp(timestamp_str):
    """Parse ISO format timestamp and return hours difference from now"""
    try:
        # Parse ISO timestamp
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        diff = now - dt
        return diff.total_seconds() / 3600
    except Exception:
        return None

def parse_time_today(time_str):
    """Parse time format assuming it's from today"""
    try:
        # Remove timezone info and parse
        clean_time = re.sub(r'\s*[A-Z]{3,4}$', '', time_str.strip())
        time_obj = datetime.strptime(clean_time, '%I:%M %p')
        
        # Get current time
        now = datetime.now()
        today_with_parsed_time = now.replace(
            hour=time_obj.hour, 
            minute=time_obj.minute, 
            second=0, 
            microsecond=0
        )
        
        # If the time is in the future, assume it's from yesterday
        if today_with_parsed_time > now:
            today_with_parsed_time -= timedelta(days=1)
        
        diff = now - today_with_parsed_time
        return diff.total_seconds() / 3600
    except Exception:
        return None

def parse_date_format(date_str, separator='/'):
    """Parse date format and return hours difference from now"""
    try:
        if separator == '/':
            date_obj = datetime.strptime(date_str, '%m/%d/%Y')
        else:
            date_obj = datetime.strptime(date_str, '%m-%d-%Y')
        
        now = datetime.now()
        diff = now - date_obj
        return diff.total_seconds() / 3600
    except Exception:
        return None

def is_within_timeframe(timestamp_text, hours):
    """Enhanced check if timestamp is within specified hours"""
    if not timestamp_text:
        return True  # Include if no timestamp available
    
    try:
        parsed_hours = parse_relative_time(timestamp_text)
        if parsed_hours is None:
            return True  # Include if can't parse timestamp
        
        # Be slightly more lenient for edge cases
        return parsed_hours <= (hours + 1)  # Add 1 hour buffer
    except Exception as e:
        logger.warning(f"Error parsing timestamp '{timestamp_text}': {e}")
        return True  # Include on error

def extract_timestamp_from_element(element):
    """Enhanced timestamp extraction from element and context"""
    if not element or not HAS_BS4:
        return None
    
    try:
        # Check the element and its context for time information
        elements_to_check = [element]
        
        # Add parent, siblings, and nearby elements for context
        if hasattr(element, 'parent') and element.parent:
            elements_to_check.append(element.parent)
            
            # Add siblings
            if hasattr(element.parent, 'find_all'):
                siblings = element.parent.find_all(['time', 'span', 'div'], limit=5)
                elements_to_check.extend(siblings)
        
        # Check for time-related attributes first
        time_attributes = ['datetime', 'data-time', 'data-timestamp', 'data-published', 'title']
        for attr in time_attributes:
            if hasattr(element, 'get') and element.get(attr):
                timestamp = element.get(attr)
                if timestamp:
                    return timestamp
        
        # Enhanced time-related patterns
        time_patterns = [
            # Relative time patterns
            r'(\d+)\s*(second|minute|hour|day|week|month)s?\s+ago',
            r'(just now|a moment ago|few seconds ago)',
            r'(\d+)\s*(सेकंड|मिनट|घंटे|दिन)\s*(पहले|पूर्व)',  # Hindi patterns
            
            # Absolute time patterns
            r'(yesterday|today|this morning|this afternoon|this evening|last night)',
            r'(\d{1,2}:\d{2}\s*(AM|PM|am|pm)?)',
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{4}[-/]\d{2}[-/]\d{2})',
            
            # ISO and RFC patterns
            r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})',
            r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})',
            
            # Month day patterns
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}',
            r'\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}',
            
            # Special news site patterns
            r'Updated:\s*([^,\n]+)',
            r'Published:\s*([^,\n]+)',
            r'Posted:\s*([^,\n]+)',
        ]
        
        # Search through elements for timestamp patterns
        for elem in elements_to_check:
            if not hasattr(elem, 'get_text'):
                continue
                
            text = elem.get_text(strip=True)
            
            # Try each pattern
            for pattern in time_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    # Return the first match (most specific)
                    match = matches[0]
                    if isinstance(match, tuple):
                        return ' '.join(match)
                    return match
        
        return None
        
    except Exception as e:
        logger.warning(f"Error extracting timestamp: {e}")
        return None

# ─── WEB SCRAPING UTILITIES ─────────────────────────────────────────
def get_content_with_retry(url, headers=None, max_retries=3):
    """Enhanced web content fetching with retry mechanism and UTF-8 support"""
    if headers is None:
        headers = HEADERS
    
    logger.info(f"Fetching: {url}")
    
    for attempt in range(max_retries):
        try:
            # Add timestamp to avoid caching
            timestamp = int(time.time() * 1000)
            separator = '&' if '?' in url else '?'
            url_with_timestamp = f"{url}{separator}t={timestamp}"
            
            # Prepare headers with UTF-8 support
            request_headers = headers.copy()
            
            # Ensure UTF-8 charset is requested
            if 'Accept-Charset' not in request_headers:
                request_headers['Accept-Charset'] = 'utf-8, iso-8859-1;q=0.5'
            
            # For compiled apps, handle encoding issues
            if getattr(sys, 'frozen', False):
                request_headers['Accept-Encoding'] = 'identity'
            
            # Add additional headers for specific sites
            if 'hindustantimes.com' in url:
                request_headers.update({
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8',  # Include Hindi
                    'Accept-Charset': 'utf-8',
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache'
                })
            elif 'sedaily.com' in url:
                request_headers.update({
                    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Accept-Charset': 'utf-8'
                })
            elif 'udn.com' in url:
                request_headers.update({
                    'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Accept-Charset': 'utf-8'
                })
            
            response = requests.get(
                url_with_timestamp, 
                headers=request_headers, 
                timeout=CONFIG.get('timeout', 30),
                allow_redirects=True,
                verify=True  # SSL verification
            )
            response.raise_for_status()
            
            # Enhanced encoding handling with UTF-8 priority
            if response.encoding is None or response.encoding == 'ISO-8859-1':
                # Try to detect encoding from content
                if response.content and HAS_CHARDET:
                    try:
                        detected = chardet.detect(response.content)
                        if detected['confidence'] > 0.7:
                            response.encoding = detected['encoding']
                        else:
                            response.encoding = 'utf-8'
                    except Exception:
                        response.encoding = 'utf-8'
                else:
                    response.encoding = response.apparent_encoding or 'utf-8'
            
            # Force UTF-8 for known international sites
            if any(site in url for site in ['sedaily.com', 'udn.com', 'hindustantimes.com']):
                response.encoding = 'utf-8'
            
            logger.info(f"Successfully fetched {url} (attempt {attempt + 1}/{max_retries})")
            
            # Rate limiting
            if CONFIG.get('request_delay', 0) > 0:
                time.sleep(CONFIG['request_delay'])
            
            return response
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"Attempt {attempt + 1}/{max_retries} failed for {url}: {e}")
            
            if attempt == max_retries - 1:
                logger.error(f"Failed to fetch {url} after {max_retries} attempts")
                return None
            
            # Progressive backoff with jitter
            base_delay = 10  # Base delay in seconds
            delay = base_delay * (attempt + 1) + (time.time() % 3)  # Add jitter
            logger.info(f"Retrying in {delay:.1f} seconds...")
            time.sleep(delay)
    
    return None

def safe_soup_parsing(content, parser="lxml"):
    """Create BeautifulSoup object with enhanced error handling and UTF-8 support"""
    if not content or not HAS_BS4:
        return None
    
    try:
        # Ensure content is properly encoded
        if isinstance(content, bytes):
            content = safe_encode_text(content)
        
        # Try lxml first (fastest and most accurate)
        return BeautifulSoup(content, parser, from_encoding='utf-8')
    except Exception:
        try:
            # Fallback to html.parser (built-in)
            return BeautifulSoup(content, "html.parser", from_encoding='utf-8')
        except Exception:
            try:
                # Last resort: html5lib (most lenient)
                return BeautifulSoup(content, "html5lib", from_encoding='utf-8')
            except Exception as e:
                logger.warning(f"Failed to parse HTML content with all parsers: {e}")
                return None

def extract_clean_text(element):
    """Extract clean text from BeautifulSoup element with enhanced cleaning and UTF-8 support"""
    if not element:
        return ""
    
    try:
        # Get text and clean it
        text = element.get_text(separator=' ', strip=True)
        
        # Ensure UTF-8 encoding
        text = safe_encode_text(text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common unwanted characters but preserve important punctuation
        text = re.sub(r'[^\w\s\-.,!?;:()\[\]{}"\'/₹$€£¥\u0900-\u097F\u4e00-\u9fff\u3040-\u309F\u30A0-\u30FF가-힣]', '', text)
        
        # Remove common noise patterns
        noise_patterns = [
            r'\s*\|\s*',  # Pipe separators
            r'\s*›\s*',   # Breadcrumb separators
            r'\s*»\s*',   # Quote markers
            r'^\s*[-•]\s*',  # List markers at start
        ]
        
        for pattern in noise_patterns:
            text = re.sub(pattern, ' ', text)
        
        # Final cleanup
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    except Exception:
        return str(element) if element else ""

# ─── TRANSLATION UTILITIES ──────────────────────────────────────────
def safe_translate(text, source_lang="auto", target_lang="en"):
    """Safely translate text with enhanced fallback and caching, with UTF-8 support"""
    if not text or not text.strip() or not HAS_TRANSLATOR:
        return text
    
    try:
        # Ensure UTF-8 encoding
        text = safe_encode_text(text)
        
        # Normalize language codes
        lang_map = {
            "korean": "ko", "ko": "ko",
            "chinese": "zh", "zh": "zh", "zh-cn": "zh", "zh-tw": "zh",
            "english": "en", "en": "en",
            "hindi": "hi", "hi": "hi",
            "auto": "auto"
        }
        
        source = lang_map.get(source_lang.lower(), source_lang)
        target = lang_map.get(target_lang.lower(), target_lang)
        
        # Skip translation if already in target language
        if source == target:
            return text
        
        # Skip if text is too short or contains mostly numbers/symbols
        if len(text.strip()) < 3 or re.match(r'^[\d\s\W]+$', text):
            return text
        
        # Create translator
        translator = GoogleTranslator(source=source, target=target)
        
        # Handle long text by chunking
        max_length = 4900  # Google Translate limit is ~5000 chars
        if len(text) > max_length:
            # Split on sentence boundaries when possible
            sentences = re.split(r'[.!?]+', text)
            chunks = []
            current_chunk = ""
            
            for sentence in sentences:
                if len(current_chunk + sentence) < max_length:
                    current_chunk += sentence + ". "
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence + ". "
            
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            translated_chunks = []
            for chunk in chunks:
                try:
                    result = translator.translate(chunk)
                    result = safe_encode_text(result) if result else chunk
                    translated_chunks.append(result)
                    time.sleep(0.5)  # Rate limiting
                except Exception:
                    translated_chunks.append(chunk)
            
            return ' '.join(translated_chunks)
        else:
            result = translator.translate(text)
            result = safe_encode_text(result) if result else text
            return result
            
    except Exception as e:
        logger.warning(f"Translation failed for text starting with '{text[:50]}...': {e}")
        return text

def detect_language(text):
    """Enhanced language detection"""
    if not text or not text.strip():
        return "unknown"
    
    try:
        # Check for specific language patterns
        language_patterns = {
            'ko': r'[가-힣]',  # Korean Hangul
            'zh': r'[\u4e00-\u9fff]',  # Chinese characters
            'hi': r'[\u0900-\u097F]',  # Devanagari (Hindi)
            'ja': r'[\u3040-\u309F\u30A0-\u30FF]',  # Japanese Hiragana/Katakana
            'ar': r'[\u0600-\u06FF]',  # Arabic
            'th': r'[\u0E00-\u0E7F]',  # Thai
        }
        
        for lang, pattern in language_patterns.items():
            if re.search(pattern, text):
                return lang
        
        # Check for common English patterns
        if re.search(r'[a-zA-Z]', text) and not any(re.search(pattern, text) for pattern in language_patterns.values()):
            return "en"
        
        return "auto"
    except Exception:
        return "auto"

def translate_article_if_needed(article, source_name):
    """Enhanced article translation based on source configuration"""
    if not article or source_name not in SOURCES or not HAS_TRANSLATOR:
        return article
    
    source_config = SOURCES[source_name]
    
    # Check if translation is needed
    if not source_config.get('requires_translation', False):
        return article
    
    source_lang = source_config.get('translation_from', 'auto')
    target_lang = source_config.get('translation_to', 'en')
    
    try:
        # Translate relevant fields
        fields_to_translate = ['title', 'headline', 'description', 'summary']
        
        for field in fields_to_translate:
            if field in article and article[field]:
                original_text = article[field]
                translated_text = safe_translate(original_text, source_lang, target_lang)
                article[field] = translated_text
                
                # Store original for reference
                article[f'original_{field}'] = original_text
        
        # Add translation metadata
        article['translated'] = True
        article['original_language'] = source_lang
        article['translation_timestamp'] = datetime.now().isoformat()
        
    except Exception as e:
        logger.warning(f"Failed to translate article from {source_name}: {e}")
        article['translated'] = False
    
    return article

# ─── SELENIUM UTILITIES ─────────────────────────────────────────────
def setup_chrome_driver():
    """Import and setup Chrome driver from config"""
    try:
        from config import setup_chrome_driver as config_setup_driver
        return config_setup_driver()
    except ImportError:
        logger.warning("Chrome driver setup not available")
        return None

def safe_selenium_get(driver, url, wait_time=10):
    """Enhanced Selenium navigation with better error handling"""
    if not driver:
        return False
    
    try:
        driver.get(url)
        
        # Enhanced waiting strategy
        try:
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.common.by import By
            
            wait = WebDriverWait(driver, wait_time)
            
            # Wait for multiple conditions
            conditions = [
                EC.presence_of_element_located((By.TAG_NAME, "body")),
                lambda d: d.execute_script("return document.readyState") == "complete"
            ]
            
            for condition in conditions:
                try:
                    wait.until(condition)
                except Exception:
                    continue  # Try next condition
            
            # Additional wait for dynamic content
            time.sleep(2)
            
            return True
        except ImportError:
            logger.warning("Selenium not available")
            return False
    except Exception as e:
        logger.warning(f"Selenium navigation failed for {url}: {e}")
        return False

# ─── VALIDATION UTILITIES ───────────────────────────────────────────
def validate_article(article):
    """Enhanced article validation"""
    if not isinstance(article, dict):
        return False
    
    required_fields = ['headline', 'link']
    
    for field in required_fields:
        if field not in article or not article[field]:
            return False
    
    # Enhanced URL validation
    url = article.get('link', '')
    if not url.startswith(('http://', 'https://')):
        return False
    
    # Check for meaningful headline length
    headline = article.get('headline', '')
    if len(headline.strip()) < 5:
        return False
    
    # Check for spam indicators
    spam_indicators = ['click here', 'free download', 'limited time', '!!!']
    headline_lower = headline.lower()
    if any(indicator in headline_lower for indicator in spam_indicators):
        return False
    
    return True

def deduplicate_articles(articles):
    """Enhanced article deduplication with fuzzy matching"""
    if not articles:
        return []
    
    seen_urls = set()
    seen_titles = set()
    unique_articles = []
    
    def normalize_title(title):
        """Normalize title for better duplicate detection"""
        # Remove common prefixes and suffixes
        title = re.sub(r'^\[.*?\]\s*', '', title)  # Remove category tags
        title = re.sub(r'\s*\|\s*.*$', '', title)  # Remove site names after pipe
        title = re.sub(r'[^\w\s]', '', title.lower())  # Remove punctuation
        title = re.sub(r'\s+', ' ', title).strip()
        return title
    
    def normalize_url(url):
        """Normalize URL for better duplicate detection"""
        # Remove query parameters and fragments
        url = re.sub(r'[?#].*$', '', url)
        # Remove trailing slashes
        url = url.rstrip('/')
        return url.lower()
    
    for article in articles:
        if not validate_article(article):
            continue
        
        url = normalize_url(article['link'])
        title = normalize_title(article['headline'])
        
        # Skip if URL already seen
        if url in seen_urls:
            continue
        
        # Skip if very similar title already seen
        title_is_duplicate = False
        for seen_title in seen_titles:
            # Simple similarity check - if 80% of words match
            title_words = set(title.split())
            seen_words = set(seen_title.split())
            if len(title_words) > 0 and len(seen_words) > 0:
                intersection = len(title_words.intersection(seen_words))
                union = len(title_words.union(seen_words))
                similarity = intersection / union if union > 0 else 0
                if similarity > 0.8:
                    title_is_duplicate = True
                    break
        
        if title_is_duplicate:
            continue
        
        seen_urls.add(url)
        seen_titles.add(title)
        unique_articles.append(article)
    
    logger.info(f"Deduplicated: {len(articles)} → {len(unique_articles)} articles")
    return unique_articles

# ─── ENHANCED ARTICLE PROCESSING ──────────────────────────────────
def clean_headline(headline):
    """Clean and enhance headline formatting"""
    if not headline:
        return ""
    
    # Remove excessive whitespace
    headline = re.sub(r'\s+', ' ', headline).strip()
    
    # Remove common noise patterns
    noise_patterns = [
        r'^\s*[-•·]\s*',  # Remove leading bullets
        r'\s*\|\s*[^|]*$',  # Remove trailing site names after pipe
        r'\s*-\s*[^-]*$',   # Remove trailing site names after dash
        r'^\s*BREAKING:\s*',  # Remove breaking news prefix
        r'^\s*LATEST:\s*',    # Remove latest news prefix
    ]
    
    for pattern in noise_patterns:
        headline = re.sub(pattern, '', headline, flags=re.IGNORECASE)
    
    # Capitalize first letter
    if headline:
        headline = headline[0].upper() + headline[1:] if len(headline) > 1 else headline.upper()
    
    return headline.strip()

def enhance_article_metadata(article, source_name):
    """Add enhanced metadata to articles"""
    if not isinstance(article, dict):
        return article
    
    # Add timestamp if missing
    if 'timestamp' not in article:
        article['timestamp'] = datetime.now().isoformat()
    
    # Add source metadata
    article['source_name'] = source_name
    article['collection_date'] = datetime.now().date().isoformat()
    
    # Clean headline
    if 'headline' in article:
        article['headline'] = clean_headline(article['headline'])
    
    # Add URL domain for easier filtering
    if 'link' in article:
        try:
            parsed_url = urlparse(article['link'])
            article['domain'] = parsed_url.netloc
        except Exception:
            article['domain'] = 'unknown'
    
    # Add word count if description exists
    if 'description' in article and article['description']:
        article['word_count'] = len(article['description'].split())
    
    return article

def filter_articles_by_timeframe(articles, hours):
    """Filter articles based on timeframe"""
    if not articles:
        return []
    
    filtered_articles = []
    for article in articles:
        timestamp = article.get('timestamp', '')
        if is_within_timeframe(timestamp, hours):
            filtered_articles.append(article)
    
    logger.info(f"Time filter: {len(articles)} → {len(filtered_articles)} articles within {hours}h")
    return filtered_articles

def sort_articles_by_relevance(articles, keywords=None):
    """Sort articles by relevance based on keywords"""
    if not articles or not keywords:
        return articles
    
    def calculate_relevance_score(article):
        score = 0
        headline = article.get('headline', '').lower()
        description = article.get('description', '').lower()
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            # Higher score for keywords in headline
            score += headline.count(keyword_lower) * 3
            # Lower score for keywords in description
            score += description.count(keyword_lower) * 1
        
        return score
    
    # Sort by relevance score (descending)
    sorted_articles = sorted(articles, key=calculate_relevance_score, reverse=True)
    return sorted_articles

# ─── ERROR HANDLING AND LOGGING ──────────────────────────────────
def log_scraping_error(source_name, url, error, context=""):
    """Log scraping errors for debugging"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    error_msg = f"[{timestamp}] {source_name} - {url}: {error}"
    if context:
        error_msg += f" (Context: {context})"
    
    logger.error(error_msg)
    
    # Optionally write to log file
    try:
        log_dir = Path(get_output_directory()) / "logs"
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f"scraping_errors_{datetime.now().strftime('%Y%m%d')}.log"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(error_msg + '\n')
    except Exception:
        pass  # Don't fail if logging fails

def log_scraping_success(source_name, url, article_count):
    """Log successful scraping for monitoring"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    success_msg = f"[{timestamp}] ✓ {source_name} - {url}: {article_count} articles"
    logger.info(success_msg)

# ─── PERFORMANCE MONITORING ───────────────────────────────────────
def measure_performance(func):
    """Decorator to measure function performance"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"{func.__name__} completed in {duration:.2f} seconds")
        return result
    return wrapper

# ─── COMPATIBILITY FUNCTIONS ──────────────────────────────────────
def ensure_backward_compatibility(articles):
    """Ensure articles have required fields for backward compatibility"""
    if not articles:
        return []
    
    compatible_articles = []
    for article in articles:
        # Ensure required fields exist
        if 'headline' not in article and 'title' in article:
            article['headline'] = article['title']
        elif 'title' not in article and 'headline' in article:
            article['title'] = article['headline']
        
        if 'link' not in article and 'url' in article:
            article['link'] = article['url']
        elif 'url' not in article and 'link' in article:
            article['url'] = article['link']
        
        # Ensure site field exists
        if 'site' not in article:
            article['site'] = article.get('source_name', 'Unknown Source')
        
        compatible_articles.append(article)
    
    return compatible_articles

# ─── ADDITIONAL UTILITY FUNCTIONS ─────────────────────────────────
def validate_url(url):
    """Validate URL format and accessibility"""
    if not url:
        return False
    
    try:
        parsed = urlparse(url)
        return bool(parsed.netloc) and parsed.scheme in ('http', 'https')
    except Exception:
        return False

def safe_get_text(element, default=""):
    """Safely extract text from BeautifulSoup element"""
    if not element or not HAS_BS4:
        return default
    
    try:
        if hasattr(element, 'get_text'):
            return element.get_text(strip=True)
        elif hasattr(element, 'text'):
            return element.text.strip()
        else:
            return str(element).strip()
    except Exception:
        return default

def truncate_text(text, max_length=500, ellipsis="..."):
    """Safely truncate text to specified length"""
    if not text or len(text) <= max_length:
        return text
    
    # Try to break at word boundary
    truncated = text[:max_length - len(ellipsis)]
    last_space = truncated.rfind(' ')
    
    if last_space > max_length * 0.8:  # If we can break at a word boundary reasonably close
        truncated = truncated[:last_space]
    
    return truncated + ellipsis

def sanitize_filename(filename):
    """Sanitize filename for cross-platform compatibility"""
    if not filename:
        return "untitled"
    
    # Remove or replace invalid characters
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', filename)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    
    # Ensure it's not too long
    if len(sanitized) > 255:
        sanitized = sanitized[:255]
    
    # Ensure it's not empty
    if not sanitized:
        sanitized = "untitled"
    
    return sanitized

def get_domain_from_url(url):
    """Extract domain from URL"""
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except Exception:
        return "unknown"

def is_valid_article_content(article):
    """Check if article has meaningful content"""
    if not isinstance(article, dict):
        return False
    
    headline = article.get('headline', '')
    description = article.get('description', '')
    
    # Check minimum content requirements
    if len(headline.strip()) < 10:
        return False
    
    # Check for placeholder or error content
    error_indicators = [
        'page not found',
        'error 404',
        'access denied',
        'loading...',
        'please wait',
        'javascript required'
    ]
    
    content_to_check = (headline + ' ' + description).lower()
    if any(indicator in content_to_check for indicator in error_indicators):
        return False
    
    return True

def retry_with_backoff(func, max_retries=3, base_delay=1, max_delay=60):
    """Retry function with exponential backoff"""
    def wrapper(*args, **kwargs):
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                
                delay = min(base_delay * (2 ** attempt), max_delay)
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s: {e}")
                time.sleep(delay)
        
        return None
    return wrapper

def normalize_whitespace(text):
    """Normalize whitespace in text"""
    if not text:
        return ""
    
    # Replace multiple whitespace characters with single space
    normalized = re.sub(r'\s+', ' ', text)
    return normalized.strip()

def extract_numbers_from_text(text):
    """Extract all numbers from text"""
    if not text:
        return []
    
    try:
        numbers = re.findall(r'\d+(?:\.\d+)?', text)
        return [float(num) if '.' in num else int(num) for num in numbers]
    except Exception:
        return []

def get_file_size_mb(filepath):
    """Get file size in MB"""
    try:
        size_bytes = os.path.getsize(filepath)
        return size_bytes / (1024 * 1024)
    except Exception:
        return 0

def ensure_directory_exists(directory_path):
    """Ensure directory exists, create if necessary"""
    try:
        Path(directory_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {directory_path}: {e}")
        return False

# ─── CONFIGURATION HELPERS ────────────────────────────────────────
def get_config_value(key, default=None):
    """Safely get configuration value"""
    try:
        return CONFIG.get(key, default)
    except Exception:
        return default

def update_config(key, value):
    """Safely update configuration value"""
    try:
        CONFIG[key] = value
        return True
    except Exception as e:
        logger.error(f"Failed to update config {key}: {e}")
        return False

# ─── DEBUGGING AND DIAGNOSTICS ───────────────────────────────────
def print_system_info():
    """Print system information for debugging"""
    info = {
        "Platform": platform.platform(),
        "Python Version": sys.version,
        "Current Directory": os.getcwd(),
        "Script Directory": get_executable_dir(),
        "Desktop Path": get_desktop_path(),
        "Output Directory": get_output_directory(),
        "Has BeautifulSoup": HAS_BS4,
        "Has Translator": HAS_TRANSLATOR,
        "Has Chardet": HAS_CHARDET,
    }
    
    logger.info("System Information:")
    for key, value in info.items():
        logger.info(f"  {key}: {value}")

def diagnose_dependencies():
    """Diagnose missing dependencies"""
    dependencies = {
        'requests': True,  # Always available
        'beautifulsoup4': HAS_BS4,
        'deep_translator': HAS_TRANSLATOR,
        'chardet': HAS_CHARDET,
    }
    
    missing = [dep for dep, available in dependencies.items() if not available]
    
    if missing:
        logger.warning(f"Missing dependencies: {', '.join(missing)}")
        logger.info("Install missing dependencies with:")
        for dep in missing:
            logger.info(f"  pip install {dep}")
    else:
        logger.info("All dependencies are available")
    
    return missing

def test_utf8_support():
    """Test UTF-8 support with various international characters"""
    test_strings = {
        'korean': '서울경제',
        'chinese': '聯合新聞網', 
        'japanese': '日本経済新聞',
        'hindi': 'हिंदुस्तान टाइम्स',
        'mixed': 'News: 서울 & 東京 update'
    }
    
    logger.info("Testing UTF-8 support:")
    for lang, text in test_strings.items():
        encoded = safe_encode_text(text)
        logger.info(f"  {lang}: {encoded}")
    
    return True

if __name__ == "__main__":
    # Run diagnostics if script is executed directly
    print_system_info()
    diagnose_dependencies()