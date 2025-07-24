# scrapers/others.py - Enhanced Other News Sources (Debugged Version)

import json
import re
import time
import requests
import sys
import os
import logging
from datetime import datetime, timezone, timedelta
from urllib.parse import urljoin
from pathlib import Path

# Enhanced import handling with better error recovery
try:
    from bs4 import BeautifulSoup, NavigableString
    HAS_BS4 = True
except ImportError:
    print("Warning: BeautifulSoup4 not installed. Web scraping functionality will be limited.")
    HAS_BS4 = False

# Add parent directory to path so we can import config and utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Enhanced config import with fallback
try:
    from config import SOURCES, HEADERS, SIMPLE_HEADERS, CONFIG
except ImportError:
    print("Warning: config.py not found. Using default configurations.")
    SOURCES = {
        'tradewinds': {
            'base': 'https://www.tradewindsnews.com',
            'latest': '/latest'
        },
        'bloomberg': {
            'base': 'https://www.bloomberg.com',
            'api': '/api/v1/stories'
        },
        'trendforce': {
            'base': 'https://www.trendforce.com',
            'news': '/news'
        },
        'udn': {
            'base': 'https://money.udn.com',
            'rank': '/rank/newest'
        },
        'gmk': {
            'base': 'https://gmk.center',
            'news': '/en/news'
        }
    }
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    SIMPLE_HEADERS = HEADERS
    CONFIG = {
        'request_delay': 2,
        'timeout': 30,
        'max_pages': 3
    }

# Enhanced utils import with fallback
try:
    from utils import get_content_with_retry, safe_soup_parsing, safe_translate
except ImportError:
    print("Warning: utils.py not found. Using fallback implementations.")
    
    def get_content_with_retry(url, headers=None, max_retries=3):
        """Fallback implementation"""
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=headers or HEADERS, timeout=30)
                response.raise_for_status()
                return response
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"Failed to fetch {url}: {e}")
                    return None
                time.sleep(5)
        return None
    
    def safe_soup_parsing(content, parser="html.parser"):
        """Fallback implementation"""
        if not content or not HAS_BS4:
            return None
        try:
            return BeautifulSoup(content, parser)
        except Exception as e:
            print(f"Failed to parse HTML: {e}")
            return None
    
    def safe_translate(text, source_lang="auto", target_lang="en"):
        """Improved fallback implementation using GoogleTranslator directly"""
        try:
            from deep_translator import GoogleTranslator
            translator = GoogleTranslator(source=source_lang, target=target_lang)
            result = translator.translate(text)
            return result if result else text
        except ImportError:
            print("deep_translator not available for translation")
            return text
        except Exception as e:
            print(f"Translation error: {e}")
            return text

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fetch_tradewinds_articles(max_pages=2):
    """Fetch TradeWinds articles using standardized approach"""
    logger.info(f"Fetching TradeWinds articles from {max_pages} pages...")
    
    if 'tradewinds' not in SOURCES:
        logger.error("TradeWinds configuration not found")
        return []
    
    base_url = SOURCES['tradewinds']['base']
    articles = []
    
    # Enhanced URL patterns for TradeWinds article categories
    article_patterns = {
        r'/tankers/': 'Tankers',
        r'/bulkers/': 'Bulkers', 
        r'/containers/': 'Containers',
        r'/gas/': 'Gas',
        r'/offshore/': 'Offshore',
        r'/cruise-and-ferry/': 'Cruise & Ferry',
        r'/technology/': 'Technology',
        r'/finance/': 'Finance',
        r'/opinion/': 'Opinion',
        r'/insurance/': 'Insurance',
        r'/casualties/': 'Casualties',
        r'/shipyards/': 'Shipyards',
        r'/shipbroking/': 'Shipbroking',
        r'/law/': 'Law',
        r'/sustainability/': 'Sustainability'
    }
    
    for page in range(1, max_pages + 1):
        logger.info(f"Processing TradeWinds page {page}/{max_pages}...")
        
        # Construct page URL
        try:
            if page == 1:
                url = f"{base_url}{SOURCES['tradewinds']['latest']}"
            else:
                url = f"{base_url}{SOURCES['tradewinds']['latest']}?page={page}"
        except KeyError as e:
            logger.error(f"Missing TradeWinds configuration: {e}")
            continue
        
        response = get_content_with_retry(url)
        if not response:
            logger.warning(f"Failed to fetch page {page}")
            continue
            
        content = response.content if hasattr(response, 'content') else response.text
        soup = safe_soup_parsing(content)
        if not soup:
            logger.warning(f"Failed to parse page {page}")
            continue
        
        page_articles = []
        
        # TARGET: h2 elements with class "teaser-title"
        teaser_titles = soup.find_all('h2', class_='teaser-title')
        logger.info(f"Found {len(teaser_titles)} teaser titles on page {page}")
        
        for teaser in teaser_titles:
            try:
                # Find the anchor tag within the h2 element
                link = teaser.find('a', class_='card-link')
                
                if not link:
                    continue
                    
                href = link.get('href', '')
                headline = link.get_text(strip=True)
                
                # Enhanced headline validation
                if len(headline) < 10 or len(headline) > 200:
                    continue
                
                # Convert relative URLs to absolute URLs
                if href.startswith('http'):
                    full_url = href
                else:
                    full_url = urljoin(base_url, href)
                
                # Enhanced category extraction from URL pattern
                category = "General"
                for pattern, cat_name in article_patterns.items():
                    if re.search(pattern, href):
                        category = cat_name
                        break
                
                # Create article with enhanced metadata
                article = {
                    "site": "TradeWinds",
                    "headline": f"[{category}] {headline}",
                    "link": full_url,
                    "category": category,
                    "source_page": page,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Add to articles list if not duplicate
                if not any(art['link'] == full_url for art in articles):
                    page_articles.append(article)
                    articles.append(article)
                    
            except Exception as e:
                logger.warning(f"Error processing teaser: {e}")
                continue
        
        logger.info(f"Page {page}: {len(page_articles)} articles added")
        
        # Rate limiting between pages
        if page < max_pages:
            time.sleep(CONFIG.get('request_delay', 2))
    
    # Enhanced deduplication based on headline similarity
    unique_articles = []
    seen_headlines = set()
    seen_urls = set()
    
    for article in articles:
        # Normalize headline for comparison
        normalized_headline = re.sub(r'[^\w\s]', '', article['headline'].lower())
        url = article['link']
        
        if normalized_headline not in seen_headlines and url not in seen_urls:
            seen_headlines.add(normalized_headline)
            seen_urls.add(url)
            unique_articles.append(article)
    
    logger.info(f"TradeWinds summary: {len(unique_articles)} unique articles (deduplicated from {len(articles)})")
    return unique_articles

def fetch_bloomberg_stories(hours=24):
    """Enhanced Bloomberg stories fetcher using the working API endpoint"""
    all_records = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    bloomberg_base = "https://www.bloomberg.com"
    
    logger.info(f"Fetching Bloomberg stories from last {hours} hours...")
    
    # Use the working API endpoint from your bloomberg.py
    base_url = "https://www.bloomberg.com/lineup-next/api/stories"
    max_pages = CONFIG.get('max_pages', 3)
    limit = 25
    
    # Enhanced retry configuration
    max_retries = 5
    retry_delay = 30
    
    for page in range(1, max_pages + 1):
        logger.info(f"Processing Bloomberg page {page}/{max_pages}...")
        
        # Construct URL using the working pattern
        url = f"{base_url}?limit={limit}&pageNumber={page}&types=ARTICLE,FEATURE,INTERACTIVE,LETTER,EXPLAINERS"
        
        # Enhanced retry mechanism
        content = None
        for attempt in range(max_retries):
            logger.info(f"Attempt {attempt + 1}/{max_retries} for page {page}...")
            
            try:
                # Add timestamp to avoid caching (like in working version)
                timestamp = int(time.time() * 1000)
                url_with_timestamp = f"{url}&t={timestamp}"
                
                # Use simple headers like in working version
                headers = {'user-agent': 'Mozilla/5.0'}
                
                response = requests.get(
                    url_with_timestamp, 
                    headers=headers, 
                    timeout=CONFIG.get('timeout', 30)
                )
                response.raise_for_status()
                response.encoding = response.apparent_encoding
                
                content = response.content
                logger.info(f"Page {page} fetched successfully (attempt {attempt + 1})")
                break
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for page {page}: {e}")
                
                if attempt == max_retries - 1:
                    logger.error(f"All attempts failed for page {page}")
                    break
                
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
        
        if not content:
            logger.warning(f"Failed to fetch page {page}, skipping...")
            continue
            
        # Parse content using the working approach
        try:
            # Decode content (following working pattern)
            if isinstance(content, bytes):
                json_text = content.decode('utf-8')
            else:
                json_text = str(content)
            
            # Parse JSON
            try:
                data = json.loads(json_text)
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error for page {page}: {e}")
                continue
            
            # Extract stories using working pattern
            if 'stories' in data:
                stories = data['stories']
            else:
                stories = data if isinstance(data, list) else []
            
            if not stories:
                logger.warning(f"No stories found in page {page}")
                continue
            
            # Process stories
            page_articles = []
            stories_within_timeframe = 0
            
            for story in stories:
                if not isinstance(story, dict):
                    continue
                
                try:
                    # Get basic story info
                    headline = story.get('headline', 'No headline').strip()
                    url_path = story.get('url', '')
                    published_at = story.get('publishedAt', '')
                    story_type = story.get('type', 'Unknown')
                    
                    if not headline or headline == 'No headline':
                        continue
                    
                    # Build full URL
                    if url_path:
                        if url_path.startswith('http'):
                            full_url = url_path
                        else:
                            full_url = bloomberg_base.rstrip('/') + url_path
                    else:
                        continue
                    
                    # Check if within timeframe
                    within_timeframe = True
                    if published_at:
                        try:
                            # Parse timestamp
                            if published_at.endswith('Z'):
                                pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                            else:
                                pub_date = datetime.fromisoformat(published_at)
                            
                            within_timeframe = pub_date >= cutoff
                        except Exception as e:
                            logger.warning(f"Error parsing timestamp {published_at}: {e}")
                            # If can't parse, assume it's recent
                            within_timeframe = True
                    
                    if not within_timeframe:
                        continue
                    
                    stories_within_timeframe += 1
                    
                    # Get category info
                    eyebrow = story.get('eyebrow', {})
                    category = eyebrow.get('text', 'General') if isinstance(eyebrow, dict) else 'General'
                    
                    # Create article record (using same structure as working code)
                    article = {
                        "site": "Bloomberg",
                        "headline": headline,
                        "link": full_url,
                        "published_at": published_at,
                        "category": category,
                        "type": story_type,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # Avoid duplicates
                    if not any(art['link'] == full_url for art in all_records):
                        page_articles.append(article)
                        all_records.append(article)
                    
                except Exception as e:
                    logger.warning(f"Error processing story: {e}")
                    continue
            
            logger.info(f"Page {page}: {len(page_articles)} articles added ({stories_within_timeframe} within timeframe)")
            
            # Early termination if no recent stories
            if stories_within_timeframe == 0 and page > 1:
                logger.info(f"No recent stories on page {page}, stopping pagination")
                break
                
        except Exception as e:
            logger.error(f"Error processing page {page}: {e}")
            continue
        
        # Rate limiting between pages (short delay like working version)
        if page < max_pages:
            time.sleep(2)
    
    # Sort by published time (newest first) like in working version
    try:
        all_records.sort(key=lambda x: x.get('published_at', ''), reverse=True)
    except Exception as e:
        logger.warning(f"Error sorting articles: {e}")
    
    # Enhanced deduplication
    unique_articles = []
    seen_urls = set()
    seen_headlines = set()
    
    for article in all_records:
        url = article['link']
        headline = article['headline'].lower().strip()
        
        # Skip duplicates
        if url in seen_urls or headline in seen_headlines:
            continue
        
        seen_urls.add(url)
        seen_headlines.add(headline)
        unique_articles.append(article)
    
    logger.info(f"Bloomberg summary: {len(unique_articles)} unique articles (deduplicated from {len(all_records)})")
    
    return unique_articles

def fetch_trendforce_articles(target_dates):
    """Enhanced TrendForce articles fetcher with improved parsing"""
    logger.info(f"Fetching TrendForce articles for {len(target_dates)} target dates...")
    
    if 'trendforce' not in SOURCES:
        logger.error("TrendForce configuration not found")
        return []
    
    articles = []
    target_date_strings = [d.strftime("%Y-%m-%d") for d in target_dates]
    logger.info(f"Looking for dates: {target_date_strings}")
    
    for page in range(1, CONFIG.get('max_pages', 3) + 1):
        logger.info(f"Processing TrendForce page {page}/{CONFIG.get('max_pages', 3)}...")
        
        try:
            url = (f"{SOURCES['trendforce']['base']}{SOURCES['trendforce']['news']}" 
                   if page == 1 
                   else f"{SOURCES['trendforce']['base']}/news/page/{page}/")
        except KeyError as e:
            logger.error(f"Missing TrendForce configuration: {e}")
            continue
        
        response = get_content_with_retry(url)
        if not response:
            logger.warning(f"Failed to fetch page {page}")
            continue
            
        content = response.content if hasattr(response, 'content') else response.text
        soup = safe_soup_parsing(content)
        if not soup:
            logger.warning(f"Failed to parse page {page}")
            continue
        
        page_articles = []
        
        # Method 1: Try the original selector
        cards = soup.select("div.insight-list-item")
        logger.info(f"Found {len(cards)} insight cards on page {page}")
        
        for card in cards:
            try:
                # Look for date in the insight tag
                date_div = card.select_one("div.insight-list-item-info > div.insight-tag")
                if not date_div:
                    # Try alternative selectors
                    date_div = card.select_one("div.insight-tag")
                    if not date_div:
                        continue
                
                date_found = None
                
                # Extract date from text content
                date_text = date_div.get_text(strip=True)
                logger.debug(f"Found date text: '{date_text}'")
                
                # Try to find date in various formats
                date_patterns = [
                    r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
                    r'(\d{4}/\d{2}/\d{2})',  # YYYY/MM/DD
                    r'(\d{2}/\d{2}/\d{4})',  # MM/DD/YYYY
                ]
                
                for pattern in date_patterns:
                    match = re.search(pattern, date_text)
                    if match:
                        found_date = match.group(1)
                        # Convert to YYYY-MM-DD format if needed
                        if '/' in found_date:
                            try:
                                if found_date.startswith('20'):  # YYYY/MM/DD
                                    date_found = found_date.replace('/', '-')
                                else:  # MM/DD/YYYY
                                    parts = found_date.split('/')
                                    date_found = f"{parts[2]}-{parts[0]:0>2}-{parts[1]:0>2}"
                            except:
                                continue
                        else:
                            date_found = found_date
                        break
                
                # Also check NavigableString children (original method)
                if not date_found and HAS_BS4:
                    for child in date_div.children:
                        if isinstance(child, NavigableString):
                            text = child.strip()
                            if re.match(r"^\d{4}-\d{2}-\d{2}$", text):
                                date_found = text
                                break
                
                if not date_found:
                    logger.debug(f"No valid date found in: '{date_text}'")
                    continue
                
                if date_found not in target_date_strings:
                    logger.debug(f"Date {date_found} not in target dates")
                    continue
                
                logger.info(f"✓ Found article for target date: {date_found}")
                
                # Extract headline and link
                headline = None
                link = None
                
                # Method 1: Look for strong tag with parent href
                strong = date_div.find("strong")
                if strong and strong.parent and strong.parent.get("href"):
                    headline = strong.get_text(strip=True)
                    link = urljoin(SOURCES['trendforce']['base'], strong.parent["href"])
                
                # Method 2: Look for any link in the card
                if not (headline and link):
                    link_elem = card.find("a", href=True)
                    if link_elem:
                        headline = link_elem.get_text(strip=True)
                        link = urljoin(SOURCES['trendforce']['base'], link_elem["href"])
                
                # Method 3: Look for title in different structures
                if not (headline and link):
                    title_elem = card.select_one("h3, h2, .title, .headline")
                    if title_elem:
                        headline = title_elem.get_text(strip=True)
                        # Look for nearby link
                        link_elem = title_elem.find("a", href=True) or title_elem.find_parent("a", href=True)
                        if link_elem:
                            link = urljoin(SOURCES['trendforce']['base'], link_elem["href"])
                
                if headline and link and len(headline) >= 5:
                    article = {
                        "site": "TrendForce",
                        "headline": headline,
                        "link": link,
                        "date": date_found,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # Avoid duplicates
                    if not any(a['link'] == link for a in articles):
                        page_articles.append(article)
                        articles.append(article)
                        logger.debug(f"  + {headline[:80]}...")
                else:
                    logger.debug(f"Could not extract valid headline/link from card")
                    
            except Exception as e:
                logger.warning(f"Error processing TrendForce card: {e}")
                continue
        
        logger.info(f"Page {page}: {len(page_articles)} articles added")
        
        # If no articles found on this page, try next page
        if len(page_articles) == 0 and page < CONFIG.get('max_pages', 3):
            logger.info(f"No articles found on page {page}, trying next page...")
    
    # Remove duplicates
    unique_articles = []
    seen_urls = set()
    for article in articles:
        if article['link'] not in seen_urls:
            seen_urls.add(article['link'])
            unique_articles.append(article)
    
    logger.info(f"TrendForce summary: {len(unique_articles)} unique articles found")
    return unique_articles

def fetch_udn_articles():
    """Enhanced UDN Money articles fetcher with correct Chinese language code"""
    logger.info("Fetching UDN Money articles with Chinese→English translation...")
    
    if 'udn' not in SOURCES:
        logger.error("UDN configuration not found")
        return []
    
    articles = []
    
    try:
        url = SOURCES['udn']['base'] + SOURCES['udn']['rank']
    except KeyError as e:
        logger.error(f"Missing UDN configuration: {e}")
        return articles
    
    response = get_content_with_retry(url)
    if not response:
        logger.warning("Failed to fetch UDN Money")
        return articles
        
    content = response.content if hasattr(response, 'content') else response.text
    soup = safe_soup_parsing(content)
    if not soup:
        logger.warning("Failed to parse UDN Money")
        return articles
    
    story_divs = soup.select("div.story__content")
    logger.info(f"Found {len(story_divs)} story divs")
    
    # Initialize translator with correct language code
    translator = None
    try:
        from deep_translator import GoogleTranslator
        # Use zh-TW for Traditional Chinese (Taiwan) or zh-CN for Simplified Chinese
        translator = GoogleTranslator(source='zh-TW', target='en')
        logger.info("Google Translator initialized successfully (Traditional Chinese → English)")
    except ImportError:
        logger.error("deep_translator not available - install with: pip install deep-translator")
        return articles
    except Exception as e:
        logger.error(f"Error initializing translator: {e}")
        # Try simplified Chinese as fallback
        try:
            translator = GoogleTranslator(source='zh-CN', target='en')
            logger.info("Using Simplified Chinese as fallback")
        except Exception as e2:
            logger.error(f"Fallback translator also failed: {e2}")
            return articles
    
    successful_translations = 0
    failed_translations = 0
    
    for div in story_divs:
        try:
            h3 = div.select_one("h3.story__headline")
            a = div.find("a", href=True)
            if not (h3 and a):
                continue
                
            cn_title = h3.get_text(strip=True)
            if len(cn_title) < 5:
                continue
            
            # Translation with enhanced error handling
            en_title = None
            translation_successful = False
            
            try:
                # Simple, direct translation
                en_title = translator.translate(cn_title)
                
                # Validate translation result
                if (en_title and 
                    en_title.strip() and 
                    en_title != cn_title and 
                    len(en_title) > 3 and
                    not en_title.startswith("Translation failed")):
                    
                    translation_successful = True
                    successful_translations += 1
                    logger.debug(f"✓ Translated: '{cn_title[:30]}...' → '{en_title[:30]}...'")
                else:
                    failed_translations += 1
                    en_title = f"[Chinese] {cn_title}"
                    logger.debug(f"✗ Translation invalid: '{cn_title[:30]}...' → '{en_title}'")
                    
            except Exception as e:
                failed_translations += 1
                en_title = f"[Chinese] {cn_title}"
                logger.warning(f"Translation error for '{cn_title[:30]}...': {e}")
            
            # Build full URL
            full_url = urljoin(SOURCES['udn']['base'], a["href"])
            
            article = {
                "site": "UDN Money",
                "headline": en_title,
                "link": full_url,
                "original_headline": cn_title,
                "translated": translation_successful,
                "timestamp": datetime.now().isoformat()
            }
            
            articles.append(article)
            
            # Rate limiting to avoid being blocked
            time.sleep(0.3)
            
        except Exception as e:
            logger.warning(f"Error processing UDN article: {e}")
            continue
    
    logger.info(f"UDN Money summary: {len(articles)} articles processed")
    logger.info(f"Translation results: {successful_translations} successful, {failed_translations} failed")
    
    return articles

def fetch_gmk_articles(target_dates):
    """Enhanced GMK Center articles fetcher using proven working approach"""
    logger.info(f"Fetching GMK Center articles for {len(target_dates)} target dates...")
    
    if 'gmk' not in SOURCES:
        logger.error("GMK configuration not found")
        return []
    
    articles = []
    base_url = SOURCES['gmk']['base']
    news_url = f"{base_url}{SOURCES['gmk']['news']}"
    
    # Build target date patterns - GMK uses format like "Tuesday 17.06.2025"
    target_patterns = []
    for target_date in target_dates:
        weekday = target_date.strftime("%A")
        day_no_zero = str(target_date.day)
        day_with_zero = f"{target_date.day:02d}"
        month = f"{target_date.month:02d}"
        year = str(target_date.year)
        
        # Add multiple format variations
        target_patterns.extend([
            f"{weekday} {day_no_zero}.{month}.{year}",
            f"{weekday} {day_with_zero}.{month}.{year}",
            f"{day_no_zero}.{month}.{year}",
            f"{day_with_zero}.{month}.{year}"
        ])
    
    logger.info(f"Looking for dates: {target_patterns}")
    
    try:
        # Fetch the news page
        response = get_content_with_retry(news_url)
        if not response:
            logger.warning("Failed to fetch GMK Center")
            return articles

        content = getattr(response, 'content', response.text)
        soup = safe_soup_parsing(content)
        if not soup:
            logger.warning("Failed to parse GMK Center")
            return articles

        # Method 1: Try structured HTML parsing first
        archive_container = soup.select_one('div.news-archive-list.archive-main-news')
        
        if archive_container:
            logger.info("Using structured HTML parsing...")
            
            # Look for date divs and their associated article lists
            for day_date_div in archive_container.select('div.day-date'):
                date_text = day_date_div.get_text(strip=True)
                logger.debug(f"Found date: {date_text}")
                
                # Check if this date matches our targets
                if not any(pattern in date_text for pattern in target_patterns):
                    continue
                
                logger.info(f"✓ Date matches target: {date_text}")
                
                # Find the article list following this date
                sibling = day_date_div.find_next_sibling()
                while sibling and not (sibling.name == 'ul' and 'archive-list' in sibling.get('class', [])):
                    sibling = sibling.find_next_sibling()
                
                if not sibling:
                    logger.debug(f"No article list found for date: {date_text}")
                    continue
                
                # Extract articles from this date's list
                date_articles_count = 0
                for link in sibling.select('li a[href]'):
                    try:
                        # Try to find title in span elements
                        title_span = (link.select_one('span.title-post.exclusive') or 
                                     link.select_one('span.title-post'))
                        
                        if title_span:
                            headline = title_span.get_text(strip=True)
                        else:
                            headline = link.get_text(strip=True)
                        
                        href = link.get('href', '')
                        
                        if len(headline) >= 5 and href:
                            full_url = urljoin(base_url, href)
                            
                            # Avoid duplicates
                            if not any(a['link'] == full_url for a in articles):
                                article = {
                                    "site": "GMK Center",
                                    "headline": headline,
                                    "link": full_url,
                                    "date": date_text,
                                    "timestamp": datetime.now().isoformat()
                                }
                                articles.append(article)
                                date_articles_count += 1
                                logger.debug(f"  + {headline[:80]}...")
                                
                    except Exception as e:
                        logger.warning(f"Error processing GMK article link: {e}")
                        continue
                
                logger.info(f"Found {date_articles_count} articles for {date_text}")
        
        # Method 2: Text-based parsing fallback (only if no articles found)
        if not articles:
            logger.info("No articles found with structured parsing, trying text-based fallback...")
            
            page_text = soup.get_text()
            lines = page_text.split('\n')
            current_date_match = False
            
            for line in lines:
                line = line.strip()
                
                # Check if this line contains target date
                if any(pattern in line for pattern in target_patterns):
                    current_date_match = True
                    logger.info(f"✓ Found target date in text: {line}")
                    continue
                
                # Check if we hit a different date
                if re.match(r'^[A-Za-z]+ \d{1,2}\.\d{2}\.\d{4}', line):
                    current_date_match = False
                    continue
                
                # Look for article links in target date sections
                if current_date_match and '[' in line and '](' in line and line.endswith(')'):
                    # Parse markdown-style links: [time Title](url)
                    match = re.match(r'^\[([^\]]+)\]\(([^)]+)\)', line)
                    if match:
                        title_with_time = match.group(1)
                        url_path = match.group(2)
                        
                        # Remove time prefix (e.g., "14:07 ")
                        title_match = re.match(r'^\d{1,2}:\d{2} (.+)', title_with_time)
                        headline = title_match.group(1) if title_match else title_with_time
                        
                        if len(headline) >= 5:
                            full_url = urljoin(base_url, url_path)
                            
                            if not any(a['link'] == full_url for a in articles):
                                article = {
                                    "site": "GMK Center",
                                    "headline": headline,
                                    "link": full_url,
                                    "date": "text_parsed",
                                    "timestamp": datetime.now().isoformat()
                                }
                                articles.append(article)
                                logger.debug(f"  + {headline[:80]}...")
        else:
            logger.info(f"Structured parsing successful, found {len(articles)} articles.")

    except Exception as e:
        logger.error(f"Error fetching/parsing GMK Center: {e}")
        return []

    # Remove duplicates based on URL
    unique_articles = []
    seen_urls = set()
    for article in articles:
        url = article['link']
        if url not in seen_urls:
            seen_urls.add(url)
            unique_articles.append(article)
    
    logger.info(f"GMK Center summary: {len(unique_articles)} unique articles found")
    return unique_articles

def fetch_all_others(hours, target_dates):
    """Fetch all other news sources - Enhanced version"""
    logger.info("Fetching other news sources...")
    all_sources = {}
    
    # Try TradeWinds
    try:
        logger.info("Fetching TradeWinds...")
        tradewinds_articles = fetch_tradewinds_articles()
        all_sources['TradeWinds'] = tradewinds_articles
        logger.info(f"TradeWinds: {len(tradewinds_articles)} articles")
    except Exception as e:
        logger.error(f"TradeWinds error: {e}")
        all_sources['TradeWinds'] = []
    
    # Try Bloomberg
    try:
        logger.info("Fetching Bloomberg...")
        bloomberg_articles = fetch_bloomberg_stories(hours)
        all_sources['Bloomberg'] = bloomberg_articles
        logger.info(f"Bloomberg: {len(bloomberg_articles)} articles")
    except Exception as e:
        logger.error(f"Bloomberg error: {e}")
        all_sources['Bloomberg'] = []
    
    # Try TrendForce
    try:
        logger.info("Fetching TrendForce...")
        trendforce_articles = fetch_trendforce_articles(target_dates)
        all_sources['TrendForce'] = trendforce_articles
        logger.info(f"TrendForce: {len(trendforce_articles)} articles")
    except Exception as e:
        logger.error(f"TrendForce error: {e}")
        all_sources['TrendForce'] = []
    
    # Try UDN Money
    try:
        logger.info("Fetching UDN Money...")
        udn_articles = fetch_udn_articles()
        all_sources['UDN Money'] = udn_articles
        logger.info(f"UDN Money: {len(udn_articles)} articles")
    except Exception as e:
        logger.error(f"UDN Money error: {e}")
        all_sources['UDN Money'] = []
    
    # Try GMK Center
    try:
        logger.info("Fetching GMK Center...")
        gmk_articles = fetch_gmk_articles(target_dates)
        all_sources['GMK Center'] = gmk_articles
        logger.info(f"GMK Center: {len(gmk_articles)} articles")
    except Exception as e:
        logger.error(f"GMK Center error: {e}")
        all_sources['GMK Center'] = []
    
    # Summary
    total_articles = sum(len(articles) for articles in all_sources.values())
    logger.info(f"Other sources summary: {total_articles} total articles collected")
    
    return all_sources

def validate_article_data(article):
    """Validate article data structure"""
    required_fields = ['site', 'headline', 'link']
    
    if not isinstance(article, dict):
        return False
    
    for field in required_fields:
        if field not in article or not article[field]:
            return False
    
    # Validate URL format
    link = article['link']
    if not (link.startswith('http://') or link.startswith('https://')):
        return False
    
    # Validate headline length
    headline = article['headline']
    if len(headline.strip()) < 5 or len(headline.strip()) > 500:
        return False
    
    return True

def deduplicate_articles(articles):
    """Remove duplicate articles based on URL and headline similarity"""
    if not articles:
        return []
    
    seen_urls = set()
    seen_headlines = set()
    unique_articles = []
    
    for article in articles:
        if not validate_article_data(article):
            continue
        
        url = article['link'].lower().strip()
        headline = article['headline'].lower().strip()
        
        # Normalize headline for comparison
        normalized_headline = re.sub(r'[^\w\s]', '', headline)
        
        if url not in seen_urls and normalized_headline not in seen_headlines:
            seen_urls.add(url)
            seen_headlines.add(normalized_headline)
            unique_articles.append(article)
    
    return unique_articles

if __name__ == "__main__":
    # Test the scrapers independently
    from datetime import date, timedelta
    
    test_hours = 24
    test_dates = [date.today(), date.today() - timedelta(days=1)]
    
    logger.info("Testing other sources...")
    test_sources = fetch_all_others(test_hours, test_dates)
    total_articles = sum(len(articles) for articles in test_sources.values())
    logger.info(f"Test Results: {total_articles} articles found across all other sources")
    
    # Print detailed results
    for source_name, articles in test_sources.items():
        logger.info(f"{source_name}: {len(articles)} articles")
        for i, article in enumerate(articles[:3]):  # Show first 3 articles
            logger.info(f"  {i+1}. {article.get('headline', 'No headline')[:100]}...")