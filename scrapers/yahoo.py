# scrapers/yahoo.py - Enhanced Yahoo Finance News Scraper

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import sys
import os
import re
import json

# Add parent directory to path so we can import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import HEADERS
except ImportError:
    # Fallback headers if config is not available
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

def clean_headline(headline):
    """Clean and validate headline text"""
    if not headline:
        return None
    
    # Remove extra whitespace and newlines
    headline = re.sub(r'\s+', ' ', headline).strip()
    
    # Skip if too short
    if len(headline) < 10:
        return None
    
    # Skip navigation and common UI elements
    skip_phrases = [
        'yahoo finance', 'sign in', 'subscribe', 'watchlist', 'portfolio', 
        'screeners', 'markets', 'news', 'videos', 'more', 'home', 
        'my portfolios', 'upgrade to premium', 'trending tickers',
        'personal finance', 'credit cards', 'banking', 'mortgages'
    ]
    
    headline_lower = headline.lower()
    if any(phrase in headline_lower for phrase in skip_phrases) and len(headline) < 50:
        return None
    
    return headline

def extract_articles_from_links(soup, base_url, topic_name):
    """Extract articles from Yahoo Finance using specific clamp classes"""
    articles = []
    seen_urls = set()
    
    print(f"Extracting articles for {topic_name} using Yahoo Finance clamp classes...")
    
    # Yahoo Finance specific selectors for UK latest
    if 'uk.finance.yahoo.com' in base_url:
        # UK Yahoo Finance specific classes
        clamp_selectors = [
            '.clamp.yf-zt3p0l',  # 6 news articles
            '.clamp.tw-line-clamp-none.yf-zt3p0l',  # 14 news articles
        ]
    else:
        # US Yahoo Finance - use general news selectors
        clamp_selectors = [
            'a[href*="/news/"]',
            '.clamp',
        ]
    
    print(f"Using selectors: {clamp_selectors}")
    
    # Extract articles using clamp classes
    for selector in clamp_selectors:
        elements = soup.select(selector)
        print(f"Found {len(elements)} elements with selector: {selector}")
        
        for element in elements:
            try:
                # Look for link within the clamp element or as parent
                link = None
                
                # Method 1: Element itself is a link
                if element.name == 'a':
                    link = element
                
                # Method 2: Find link within the element
                if not link:
                    link = element.find('a', href=True)
                
                # Method 3: Check parent elements for link
                if not link:
                    parent = element.parent
                    while parent and not link:
                        if parent.name == 'a' and parent.get('href'):
                            link = parent
                            break
                        link = parent.find('a', href=True)
                        if link:
                            break
                        parent = parent.parent
                
                # Method 4: Check child elements more thoroughly
                if not link:
                    all_links = element.find_all('a', href=True)
                    for potential_link in all_links:
                        href = potential_link.get('href', '')
                        if '/news/' in href:
                            link = potential_link
                            break
                
                if not link:
                    continue
                
                href = link.get('href', '')
                
                # Validate news URL
                if not any(pattern in href for pattern in [
                    'finance.yahoo.com/news/',
                    'uk.finance.yahoo.com/news/',
                    '/news/'
                ]):
                    continue
                
                # Build full URL
                if href.startswith('http'):
                    full_url = href
                elif href.startswith('/'):
                    if 'uk.finance.yahoo.com' in base_url:
                        full_url = f"https://uk.finance.yahoo.com{href}"
                    else:
                        full_url = f"https://finance.yahoo.com{href}"
                else:
                    full_url = urljoin(base_url, href)
                
                # Skip duplicates
                if full_url in seen_urls:
                    continue
                seen_urls.add(full_url)
                
                # Extract headline - prioritize clamp element text
                headline = None
                
                # Method 1: Get text from clamp element itself
                clamp_text = element.get_text(strip=True)
                if clamp_text and len(clamp_text) > 10:
                    headline = clean_headline(clamp_text)
                
                # Method 2: Try link attributes
                if not headline:
                    headline = clean_headline(link.get('aria-label', '')) or clean_headline(link.get('title', ''))
                
                # Method 3: Try link text
                if not headline:
                    link_text = link.get_text(strip=True)
                    if link_text and len(link_text) > 10:
                        headline = clean_headline(link_text)
                
                # Skip if no valid headline
                if not headline:
                    continue
                
                # Add article
                articles.append({
                    'site': f'Yahoo Finance ({topic_name})',
                    'headline': headline,
                    'link': full_url,
                    'topic': topic_name.lower(),
                    'selector_used': selector
                })
                
                print(f"  ✓ Found: {headline[:80]}...")
                
            except Exception as e:
                print(f"  ❌ Error processing element: {e}")
                continue
    
    print(f"Total articles found: {len(articles)}")
    
    # Show breakdown by selector
    selector_counts = {}
    for article in articles:
        selector = article.get('selector_used', 'unknown')
        selector_counts[selector] = selector_counts.get(selector, 0) + 1
    
    print("Breakdown by selector:")
    for selector, count in selector_counts.items():
        print(f"  - {selector}: {count} articles")
    
    return articles

def fetch_yahoo_finance_news(topic="uk_latest"):
    """Function to fetch Yahoo Finance articles using Selenium approach like Edge Singapore"""
    
    # Import Selenium components
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        SELENIUM_AVAILABLE = True
    except ImportError:
        print("❌ Selenium not available. Install with: pip install selenium")
        return []
    
    # Define URLs for different topics
    urls = {
        "uk_latest": "https://uk.finance.yahoo.com/",
        "latest": "https://finance.yahoo.com/topic/latest-news/"
    }
    
    if topic not in urls:
        print(f"Invalid topic '{topic}'. Choose from: {list(urls.keys())}")
        return []
    
    url = urls[topic]
    print(f"Fetching {topic} news from: {url} using Selenium...")
    
    # Setup Chrome driver (similar to Edge Singapore approach)
    def setup_chrome_driver():
        """Setup Chrome driver with optimal settings"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Additional options to avoid detection
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return driver
        except Exception as e:
            print(f"❌ Failed to setup Chrome driver: {e}")
            return None
    
    driver = setup_chrome_driver()
    if not driver:
        print("❌ Could not setup Chrome driver")
        return []
    
    articles = []
    
    try:
        print(f"📱 Navigating to: {url}")
        driver.get(url)
        
        # Wait for page to load completely
        WebDriverWait(driver, 15).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        # Handle consent page if redirected
        current_url = driver.current_url
        if 'consent.yahoo.com' in current_url:
            print("🔄 Detected consent page, attempting to handle...")
            
            try:
                # Look for "Reject all" or "Accept all" buttons
                wait = WebDriverWait(driver, 10)
                
                # Try different consent button selectors
                consent_selectors = [
                    "//button[contains(text(), 'Reject all')]",
                    "//button[contains(text(), 'Accept all')]", 
                    "//button[contains(text(), 'Continue')]",
                    "//input[@value='agree']",
                    "//button[@name='agree']"
                ]
                
                button_clicked = False
                for selector in consent_selectors:
                    try:
                        button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                        button.click()
                        print(f"✅ Clicked consent button: {selector}")
                        button_clicked = True
                        break
                    except:
                        continue
                
                if button_clicked:
                    # Wait for redirect back to main page
                    WebDriverWait(driver, 10).until(
                        lambda d: 'finance.yahoo.com' in d.current_url and 'consent' not in d.current_url
                    )
                    print("✅ Successfully handled consent page")
                else:
                    print("⚠ Could not find consent button, continuing anyway...")
                    
            except Exception as e:
                print(f"⚠ Consent handling failed: {e}")
        
        # Additional wait for content to load
        time.sleep(5)
        
        # Get page source and parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Debug: Check what we got
        page_title = soup.title.string if soup.title else "No title"
        print(f"📄 Page title: {page_title}")
        
        # Strategy 1: JSON-LD structured data (like Edge Singapore)
        print("🔍 Looking for JSON-LD structured data...")
        json_scripts = soup.find_all('script', {'type': 'application/ld+json'})
        print(f"Found {len(json_scripts)} JSON-LD scripts")
        
        for script_idx, script in enumerate(json_scripts):
            try:
                if script.string:
                    data = json.loads(script.string.strip())
                    print(f"Processing JSON-LD script {script_idx + 1}...")
                    
                    # Look for news articles in structured data
                    def extract_from_json(obj, path=""):
                        found_articles = []
                        if isinstance(obj, dict):
                            # Look for article-like structures
                            if obj.get('@type') in ['Article', 'NewsArticle']:
                                headline = obj.get('headline') or obj.get('name')
                                url = obj.get('url')
                                if headline and url:
                                    found_articles.append({'headline': headline, 'url': url})
                            
                            # Recursively search nested objects
                            for key, value in obj.items():
                                found_articles.extend(extract_from_json(value, f"{path}.{key}"))
                        
                        elif isinstance(obj, list):
                            for i, item in enumerate(obj):
                                found_articles.extend(extract_from_json(item, f"{path}[{i}]"))
                        
                        return found_articles
                    
                    json_articles = extract_from_json(data)
                    if json_articles:
                        print(f"✅ Found {len(json_articles)} articles in JSON-LD")
                        for article in json_articles:
                            articles.append({
                                'site': f'Yahoo Finance ({topic})',
                                'headline': article['headline'],
                                'link': article['url'],
                                'topic': topic.lower()
                            })
                        
                        if articles:
                            return articles  # Return early if JSON-LD worked
                            
            except Exception as e:
                print(f"❌ Error processing JSON-LD script {script_idx + 1}: {e}")
                continue
        
        # Strategy 2: Yahoo Finance specific selectors (enhanced from original)
        print("🔍 Using Yahoo Finance specific HTML selectors...")
        
        # Look for the specific clamp classes first
        clamp_selectors = [
            '.clamp.yf-zt3p0l',
            '.clamp.tw-line-clamp-none.yf-zt3p0l',
            '.clamp',  # Fallback to any clamp class
        ]
        
        for selector in clamp_selectors:
            elements = soup.select(selector)
            print(f"Found {len(elements)} elements with selector: {selector}")
            
            for element in elements:
                try:
                    # Get headline from clamp element
                    headline = element.get_text(strip=True)
                    
                    if not headline or len(headline) < 10:
                        continue
                    
                    # Find associated link
                    link = None
                    
                    # Method 1: Element is inside a link
                    parent = element.parent
                    while parent and not link:
                        if parent.name == 'a' and parent.get('href'):
                            link = parent
                            break
                        parent = parent.parent
                    
                    # Method 2: Look for nearby links
                    if not link:
                        # Look in siblings
                        for sibling in element.find_next_siblings('a'):
                            if sibling.get('href'):
                                link = sibling
                                break
                        
                        # Look in parent's siblings
                        if not link and element.parent:
                            for sibling in element.parent.find_next_siblings():
                                link_in_sibling = sibling.find('a', href=True)
                                if link_in_sibling:
                                    link = link_in_sibling
                                    break
                    
                    if link:
                        href = link.get('href', '')
                        
                        # Build full URL
                        if href.startswith('/'):
                            if 'uk.finance.yahoo.com' in url:
                                full_url = f"https://uk.finance.yahoo.com{href}"
                            else:
                                full_url = f"https://finance.yahoo.com{href}"
                        elif href.startswith('http'):
                            full_url = href
                        else:
                            continue
                        
                        # Validate it's a news URL
                        if '/news/' in full_url:
                            # Clean headline
                            headline = clean_headline(headline)
                            if headline:
                                articles.append({
                                    'site': f'Yahoo Finance ({topic})',
                                    'headline': headline,
                                    'link': full_url,
                                    'topic': topic.lower()
                                })
                                print(f"✅ Found: {headline[:60]}...")
                
                except Exception as e:
                    continue
            
            if articles:
                print(f"✅ Found {len(articles)} articles using {selector}")
                break
        
        # Strategy 3: General Yahoo Finance selectors (fallback)
        if not articles:
            print("🔍 Using fallback selectors...")
            
            fallback_selectors = [
                'a[href*="/news/"]',
                '[data-ylk*="ct:story"] a',
                '.js-stream-content a',
                'h1 a, h2 a, h3 a',
            ]
            
            for selector in fallback_selectors:
                links = soup.select(selector)
                print(f"Trying {selector}: found {len(links)} links")
                
                for link in links[:20]:  # Limit to first 20
                    href = link.get('href', '')
                    
                    if '/news/' not in href:
                        continue
                    
                    # Get headline
                    headline = (
                        link.get('aria-label', '') or
                        link.get('title', '') or
                        link.get_text(strip=True)
                    )
                    
                    headline = clean_headline(headline)
                    if not headline:
                        continue
                    
                    # Build full URL
                    if href.startswith('/'):
                        if 'uk.finance.yahoo.com' in url:
                            full_url = f"https://uk.finance.yahoo.com{href}"
                        else:
                            full_url = f"https://finance.yahoo.com{href}"
                    elif href.startswith('http'):
                        full_url = href
                    else:
                        continue
                    
                    articles.append({
                        'site': f'Yahoo Finance ({topic})',
                        'headline': headline,
                        'link': full_url,
                        'topic': topic.lower()
                    })
                    print(f"✅ Found: {headline[:60]}...")
                
                if articles:
                    break
        
        # Remove duplicates
        unique_articles = []
        seen_urls = set()
        seen_headlines = set()
        
        for article in articles:
            url_key = article['link']
            headline_key = article['headline'].lower()[:50]
            
            if url_key not in seen_urls and headline_key not in seen_headlines:
                seen_urls.add(url_key)
                seen_headlines.add(headline_key)
                unique_articles.append(article)
        
        print(f"✅ Found {len(unique_articles)} unique {topic} articles")
        return unique_articles
        
    except Exception as e:
        print(f"❌ Error with Selenium approach: {e}")
        return []
    
    finally:
        try:
            driver.quit()
        except:
            pass

def fetch_articles():
    """Main function to fetch articles from all Yahoo Finance topics"""
    
    print("=" * 50)
    print("YAHOO FINANCE - Starting enhanced collection...")
    print("=" * 50)
    
    all_articles = []
    topics = ["uk_latest", "latest"]
    
    for i, topic in enumerate(topics, 1):
        print(f"\n[{i}/{len(topics)}] --- Fetching {topic.upper()} articles ---")
        
        try:
            articles = fetch_yahoo_finance_news(topic)
            all_articles.extend(articles)
            
            if articles:
                print(f"✓ {topic.capitalize()}: {len(articles)} articles collected")
            else:
                print(f"⚠ {topic.capitalize()}: No articles found")
                
        except Exception as e:
            print(f"❌ Failed to fetch {topic} articles: {e}")
        
        # Wait between requests to be respectful
        if i < len(topics):
            print("Waiting 5 seconds before next topic...")
            time.sleep(5)
    
    # Final deduplication across all topics
    print(f"\n--- Deduplicating across all topics ---")
    
    seen_urls = set()
    seen_headlines = set()
    unique_articles = []
    
    for article in all_articles:
        url_key = article['link']
        headline_key = article['headline'].lower()[:60]  # Longer key for better matching
        
        if url_key not in seen_urls and headline_key not in seen_headlines:
            seen_urls.add(url_key)
            seen_headlines.add(headline_key)
            unique_articles.append(article)
    
    print(f"✓ Yahoo Finance: {len(unique_articles)} total unique articles collected")
    print(f"  (Removed {len(all_articles) - len(unique_articles)} duplicates)")
    
    # Count articles by topic for summary
    topic_counts = {}
    for article in unique_articles:
        topic = article['topic']
        topic_counts[topic] = topic_counts.get(topic, 0) + 1
    
    print("\nBreakdown by topic:")
    for topic, count in topic_counts.items():
        print(f"  - {topic.capitalize()}: {count} articles")
    
    # Show some sample headlines
    if unique_articles:
        print(f"\nSample headlines collected:")
        for i, article in enumerate(unique_articles[:5]):
            print(f"  {i+1}. [{article['topic']}] {article['headline'][:70]}...")
    
    return unique_articles

if __name__ == "__main__":
    # Test the scraper
    print("Testing Yahoo Finance scraper...")
    articles = fetch_articles()
    print(f"\nTest completed: {len(articles)} articles found")
    
    if articles:
        print("\nFirst few articles:")
        for i, article in enumerate(articles[:3]):
            print(f"{i+1}. {article['headline']}")
            print(f"   Link: {article['link']}")
            print(f"   Topic: {article['topic']}")
            print()
    else:
        print("No articles found. Check network connection and website structure.")