# scrapers/singapore.py - Singapore News Sources

import json
import time
import sys
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from selenium.webdriver.support.ui import WebDriverWait

# Add parent directory to path so we can import config and utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import SOURCES, HEADERS, SELENIUM_AVAILABLE
from utils import get_content_with_retry, safe_soup_parsing, setup_chrome_driver

def extract_articles_from_page(soup, base_url):
    """Extract articles from a single page using Edge Singapore optimized approach"""
    articles = []
    
    # Strategy 1: JSON-LD structured data (ENHANCED DEBUG VERSION)
    json_scripts = soup.find_all('script', {'type': 'application/ld+json'})
    print(f"    Found {len(json_scripts)} JSON-LD scripts")
    
    for script_idx, script in enumerate(json_scripts):
        try:
            if script.string:
                print(f"    Processing script {script_idx + 1}...")
                data = json.loads(script.string.strip())
                
                # Handle @graph structure (new Edge Singapore format)
                if isinstance(data, dict) and '@graph' in data:
                    print(f"    Found @graph structure with {len(data['@graph'])} items")
                    graph_items = data['@graph']
                    
                    # Look for ItemList within @graph
                    for graph_idx, graph_item in enumerate(graph_items):
                        if isinstance(graph_item, dict) and graph_item.get('@type') == 'ItemList':
                            data = graph_item
                            print(f"    ✓ Found ItemList within @graph at position {graph_idx + 1}")
                            break
                    else:
                        print(f"    ❌ No ItemList found in @graph")
                        continue
                
                # Handle both single objects and arrays (original logic)
                elif isinstance(data, list):
                    print(f"    Data is a list with {len(data)} items")
                    for item in data:
                        if isinstance(item, dict) and item.get('@type') == 'ItemList':
                            data = item
                            print(f"    ✓ Found ItemList in array")
                            break
                    else:
                        print(f"    ❌ No ItemList found in array")
                        continue
                elif isinstance(data, dict) and data.get('@type') == 'ItemList':
                    print(f"    ✓ Data is directly an ItemList")
                else:
                    print(f"    ❌ Data type: {type(data)}, @type: {data.get('@type') if isinstance(data, dict) else 'N/A'}")
                    continue
                
                # Now process the ItemList structure
                if isinstance(data, dict) and data.get('@type') == 'ItemList':
                    items = data.get('itemListElement', [])
                    print(f"    ✓ Processing ItemList with {len(items)} items")
                    
                    for item_idx, item in enumerate(items):
                        if isinstance(item, dict) and item.get('@type') == 'ListItem':
                            title = item.get('name', '').strip()
                            url = item.get('url', '').strip()
                            
                            # Validate title and URL
                            if title and url and len(title) > 10:
                                # URLs from Edge Singapore are already complete but may need fixing
                                if url.startswith('https://www.theedgesingapore.com'):
                                    # Debug: Print original URL
                                    print(f"      🔍 Original URL: {url}")
                                    
                                    # Fix double slashes first
                                    if '//news/' in url or '//section/' in url:
                                        url = url.replace('theedgesingapore.com//', 'theedgesingapore.com/')
                                        print(f"      🔧 Fixed double slashes: {url}")
                                    
                                    # Fix the URL by removing /section/latest/ if present
                                    if '/section/latest/' in url:
                                        corrected_url = url.replace('https://www.theedgesingapore.com/section/latest/', 'https://www.theedgesingapore.com/')
                                        print(f"      🔧 Fixed section/latest: {url} -> {corrected_url}")
                                        url = corrected_url
                                    else:
                                        print(f"      ✅ URL structure correct: {url}")
                                    
                                    articles.append({
                                        'title': title,
                                        'link': url
                                    })
                                    print(f"      ✓ Added: {title[:50]}...")
                                else:
                                    print(f"      ❌ Invalid URL format: {url}")
                            else:
                                print(f"      ❌ Invalid title/URL: title='{title}' (len={len(title)}), url='{url}'")
                    
                    # If we found articles from JSON-LD, return them immediately
                    if articles:
                        print(f"    ✓ Successfully extracted {len(articles)} articles from JSON-LD")
                        return articles
                        
        except json.JSONDecodeError as e:
            print(f"    ❌ JSON decode error in script {script_idx + 1}: {e}")
            continue
        except Exception as e:
            print(f"    ❌ Error processing script {script_idx + 1}: {e}")
            continue
    
    print("    No articles found in JSON-LD, trying fallback methods...")
    
    # Strategy 2: Edge Singapore specific HTML structure (NEW)
    print("    Trying Edge Singapore HTML structure with class='undefined'...")
    undefined_elements = soup.find_all(class_="undefined")
    print(f"    Found {len(undefined_elements)} elements with class='undefined'")
    
    for elem in undefined_elements:
        try:
            # Look for href attribute directly on this element
            href = elem.get('href')
            if href:
                # Get the text content as the headline
                headline = elem.get_text(strip=True)
                
                if headline and len(headline) > 10 and href.startswith('/'):
                    # Build full URL
                    full_url = base_url.rstrip('/') + href
                    
                    # Fix double slashes if present
                    if '//news/' in full_url:
                        full_url = full_url.replace('theedgesingapore.com//', 'theedgesingapore.com/')
                    
                    # Skip if it's just category text
                    if headline.lower() not in ['company in the news', 'latest news', 'breaking news']:
                        articles.append({
                            'title': headline,
                            'link': full_url
                        })
                        print(f"      ✓ Added from HTML: {headline[:50]}...")
        except Exception as e:
            print(f"      ❌ Error processing undefined element: {e}")
            continue
    
    if articles:
        print(f"    ✓ Found {len(articles)} articles using Edge Singapore HTML structure")
        return articles
    
    # Strategy 3: Look for h1 elements with links (fallback for the structure you showed)
    print("    Trying h1 elements with links...")
    h1_links = soup.select('h1 a[href]')
    print(f"    Found {len(h1_links)} h1 links")
    
    for link in h1_links:
        try:
            headline = link.get_text(strip=True)
            href = link.get('href', '')
            
            if headline and len(headline) > 10 and href:
                # Build full URL
                if href.startswith('/'):
                    full_url = base_url.rstrip('/') + href
                elif href.startswith('http'):
                    full_url = href
                else:
                    continue
                
                # Filter out navigation
                if not any(skip in headline.lower() for skip in ['subscribe', 'login', 'menu']):
                    articles.append({
                        'title': headline,
                        'link': full_url
                    })
                    print(f"      ✓ Added from h1: {headline[:50]}...")
        except Exception as e:
            print(f"      ❌ Error processing h1 link: {e}")
            continue
    
    if articles:
        print(f"    ✓ Found {len(articles)} articles using h1 links")
        return articles
    
    # Strategy 4: Generic article selectors (original fallback)
    article_selectors = ['article', '[class*="article"]', '[class*="news"]', '[class*="story"]']
    
    for selector in article_selectors:
        elements = soup.select(selector)
        print(f"    Trying selector '{selector}': found {len(elements)} elements")
        
        for element in elements[:15]:  # Limit to first 15
            title_elem = (element.find(['h1', 'h2', 'h3', 'h4']) or element.find('a'))
            link_elem = element.find('a', href=True)
            
            if title_elem and link_elem:
                title = title_elem.get_text().strip()
                href = link_elem.get('href', '')
                
                if title and len(title) > 10 and len(title) < 200 and href:
                    if href.startswith('/'):
                        href = base_url.rstrip('/') + href
                    elif not href.startswith('http'):
                        href = base_url.rstrip('/') + '/' + href.lstrip('/')
                    
                    if not any(skip in title.lower() for skip in ['subscribe', 'login', 'menu', 'by ', '•']):
                        articles.append({
                            'title': title,
                            'link': href
                        })
                        print(f"      ✓ Added from {selector}: {title[:50]}...")
        
        if articles:
            print(f"    ✓ Found {len(articles)} articles using selector '{selector}'")
            break
    
    print(f"    Final result: {len(articles)} articles extracted")
    return articles

def fetch_edge_singapore_articles():
    """Fetch Edge Singapore articles - Focus on section/latest first"""
    if not SELENIUM_AVAILABLE:
        print("  Selenium not available. Skipping Edge Singapore...")
        return []
    
    print("  Setting up Chrome driver for Edge Singapore...")
    
    driver = setup_chrome_driver()
    if not driver:
        print("  Failed to setup Chrome driver for Edge Singapore")
        return []
    
    articles = []
    
    # Force try section/latest first
    url = "https://www.theedgesingapore.com/section/latest"
    print(f"    🎯 Focusing on URL: {url}")
    
    try:
        # Navigate and wait
        driver.get(url)
        WebDriverWait(driver, 15).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(5)  # Give it more time
        
        # Parse content
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Debug: Check what we actually got
        page_title = soup.title.string if soup.title else "No title"
        print(f"    Page title: {page_title}")
        
        # Check for JSON-LD
        json_scripts = soup.find_all('script', {'type': 'application/ld+json'})
        print(f"    Found {len(json_scripts)} JSON-LD scripts")
        
        if json_scripts:
            print(f"    ✓ JSON-LD found! Processing...")
            # Extract articles
            found_articles = extract_articles_from_page(soup, url)
            
            if found_articles:
                # Convert to the format expected by main
                for article in found_articles:
                    headline = article.get('title', '') or article.get('headline', '')
                    link = article.get('link', '') or article.get('url', '')
                    
                    if headline and link:
                        articles.append({
                            'site': 'The Edge Singapore',
                            'headline': headline,
                            'link': link
                        })
                
                print(f"    ✓ Found {len(found_articles)} articles from section/latest")
            else:
                print(f"    ❌ JSON-LD found but no articles extracted")
        else:
            print(f"    ❌ No JSON-LD scripts found on section/latest")
            
            # Quick fallback - look for any article links
            print(f"    Trying HTML fallback on section/latest...")
            article_links = soup.select('a[href*="/news/"]')
            print(f"    Found {len(article_links)} news links")
            
            for link in article_links[:10]:  # Take first 10
                href = link.get('href', '')
                headline = link.get_text(strip=True)
                
                if headline and len(headline) > 15 and href:
                    if href.startswith('/'):
                        full_url = "https://www.theedgesingapore.com" + href
                    else:
                        full_url = href
                    
                    articles.append({
                        'site': 'The Edge Singapore',
                        'headline': headline,
                        'link': full_url
                    })
                    print(f"      ✓ Added from HTML: {headline[:50]}...")
        
    except Exception as e:
        print(f"    ❌ Error with section/latest: {e}")
    finally:
        try:
            driver.quit()
        except:
            pass
    
    # Debug: Print final articles
    print(f"🔍 DEBUG: Final articles from section/latest:")
    for i, article in enumerate(articles[:3], 1):
        print(f"  {i}. {article['headline'][:50]}...")
        print(f"     Link: {article['link']}")
    
    return articles

def fetch_business_times_articles(max_pages=3):
    """Fetch Business Times Singapore articles"""
    base_url = "https://www.businesstimes.com.sg/singapore"
    articles = []
    
    for page in range(1, max_pages + 1):
        if page == 1:
            url = base_url
        else:
            url = f"{base_url}?page={page}"
        
        response = get_content_with_retry(url)
        if not response:
            continue
            
        content = response.content if hasattr(response, 'content') else response.text
        soup = safe_soup_parsing(content)
        if not soup:
            continue
        
        page_articles = []  # Track articles from this page separately like businesstimes.py
        
        # Find all story containers
        story_divs = soup.find_all('div', class_='story')
        
        for story in story_divs:
            # Look for the title link within h3 tags
            h3_tag = story.find('h3')
            if not h3_tag:
                continue
            
            # Find the link within the h3
            link = h3_tag.find('a', href=True)
            if not link:
                continue
            
            href = link.get('href', '')
            
            # Filter for Singapore section articles
            if not href.startswith('/singapore/'):
                continue
            
            # Get headline - exact same logic as businesstimes.py
            headline_span = link.find('span', class_='inline-block hover:underline')
            if headline_span:
                headline = headline_span.get_text(strip=True)
            else:
                # Fallback to link text or title attribute (note the order difference)
                headline = link.get('title', '') or link.get_text(strip=True)
            
            # Skip if no meaningful headline
            if not headline or len(headline) < 10:
                continue
            
            # Exact same filtering logic as businesstimes.py
            skip_words = ['read more', 'click here', 'subscribe', 'login', 'sign up', 'menu']
            skip_exact_phrases = [
                'economy & policy', 'economy and policy', 'singapore news', 'latest news', 
                'breaking news', 'top stories', 'singapore', 'economy', 'policy', 'sgsme'
            ]
            
            headline_lower = headline.lower().strip()
            
            # Skip navigation elements
            if any(word in headline_lower for word in skip_words):
                continue
            
            # Skip section headers and category names
            if headline_lower in skip_exact_phrases:
                continue
            
            # Skip very short headlines that are likely navigation
            if len(headline) < 15:
                continue
            
            # Build full URL
            full_url = urljoin("https://www.businesstimes.com.sg", href)
            
            # Check if article already exists - match businesstimes.py logic exactly  
            if not any(art['link'] == full_url for art in articles + page_articles):
                page_articles.append({
                    "site": "Business Times Singapore",
                    "headline": headline,
                    "link": full_url
                })
        
        articles.extend(page_articles)
    
    return articles

def fetch_straits_times_articles(max_pages=3):
    """Fetch Straits Times Singapore articles - Clean version using only working selector"""
    base_url = "https://www.straitstimes.com/singapore/latest"
    
    # Use working headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    articles = []
    
    for page in range(max_pages):
        url = f"{base_url}?page={page}"
        
        print(f"    Trying Straits Times page {page}: {url}")
        
        try:
            # Use direct requests - this is what works
            import requests
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            page_articles = []
            
            # Use the working selector: links containing "/singapore/"
            singapore_links = soup.select('a[href*="/singapore/"]')
            print(f"    Found {len(singapore_links)} Singapore links")
            
            for link in singapore_links:
                href = link.get('href', '')
                headline = link.get_text(strip=True)
                
                # Filter out navigation, short headlines, and generic terms
                if (not headline or len(headline) < 15 or 
                    any(skip in headline.lower() for skip in [
                        'singapore', 'latest', 'news', 'more', 'section',
                        'read more', 'subscribe', 'sign in', 'menu'
                    ])):
                    continue
                
                # Build full URL
                if href.startswith('http'):
                    full_url = href
                else:
                    full_url = urljoin("https://www.straitstimes.com", href)
                
                # Add if not duplicate
                if not any(art['link'] == full_url for art in articles + page_articles):
                    page_articles.append({
                        "site": "Straits Times",
                        "headline": headline,
                        "link": full_url
                    })
            
            print(f"    ✓ Found {len(page_articles)} articles on page {page}")
            
            # Show sample articles for verification
            for i, article in enumerate(page_articles[:3], 1):
                print(f"      {i}. {article['headline'][:60]}...")
            
            articles.extend(page_articles)
            
            # If no articles found, stop pagination
            if len(page_articles) == 0:
                print(f"    No articles found on page {page}, stopping pagination")
                break
            
            # Add delay between requests
            if page < max_pages - 1:
                time.sleep(1)
                
        except Exception as e:
            print(f"    ❌ Error fetching page {page}: {e}")
            continue
    
    print(f"    ✓ Total Straits Times articles: {len(articles)}")
    return articles
   
def fetch_yahoo_finance_singapore_articles():
    """Fetch Yahoo Finance Singapore articles - Fixed config access"""
    # Use the correct key from updated config.py
    url = SOURCES['yahoo_finance_sg']['urls'][0]  # Get first URL from the list
    articles = []
    
    print(f"    Trying Yahoo Finance URL: {url}")
    
    response = get_content_with_retry(url)
    if not response:
        print(f"    ❌ Failed to fetch Yahoo Finance Singapore")
        return articles
        
    content = response.content if hasattr(response, 'content') else response.text
    soup = safe_soup_parsing(content)
    if not soup:
        print(f"    ❌ Failed to parse Yahoo Finance HTML")
        return articles
    
    all_links = soup.find_all('a', href=True)
    print(f"    Found {len(all_links)} total links on Yahoo Finance page")
    
    yahoo_news_links = 0
    for link in all_links:
        href = link.get('href', '')
        
        # Only process Yahoo Finance news URLs
        if 'sg.finance.yahoo.com/news/' not in href:
            continue
        
        yahoo_news_links += 1
        
        # Get headline from multiple possible sources
        headline = None
        
        # Method 1: Get from aria-label attribute
        aria_label = link.get('aria-label', '')
        if aria_label and len(aria_label) > 10:
            headline = aria_label
        
        # Method 2: Get from title attribute
        if not headline:
            title_attr = link.get('title', '')
            if title_attr and len(title_attr) > 10:
                headline = title_attr
        
        # Method 3: Get from h3 element
        if not headline:
            h3_element = link.find('h3')
            if h3_element:
                headline = h3_element.get_text(strip=True)
        
        # Method 4: Fallback to link text
        if not headline:
            headline = link.get_text(strip=True)
        
        # Skip if no meaningful headline
        if not headline or len(headline) < 10:
            continue
            
        # Skip navigation and common UI elements
        skip_words = ['yahoo', 'finance', 'sign in', 'subscribe', 'watchlist', 'portfolio']
        if any(word in headline.lower() for word in skip_words) and len(headline) < 30:
            continue
        
        # Clean up the headline
        headline = headline.strip()
        
        # Ensure we have a full URL
        if href.startswith('http'):
            full_url = href
        else:
            full_url = urljoin(url, href)
        
        # Add to articles if not duplicate
        if not any(art['link'] == full_url for art in articles):
            articles.append({
                "site": "Yahoo Finance Singapore",
                "headline": headline,
                "link": full_url
            })
    
    print(f"    Found {yahoo_news_links} Yahoo Finance news links, extracted {len(articles)} articles")
    return articles

def fetch_all():
    """Fetch all Singapore news sources"""
    print("Fetching Singapore news...")
    all_articles = []
    
    # Fetch from all Singapore sources
    print("  Fetching The Edge Singapore...")
    edge_articles = fetch_edge_singapore_articles()
    all_articles.extend(edge_articles)
    print(f"    ✓ The Edge Singapore: {len(edge_articles)} articles")
    
    print("  Fetching Business Times Singapore...")
    bt_articles = fetch_business_times_articles()
    all_articles.extend(bt_articles)
    print(f"    ✓ Business Times Singapore: {len(bt_articles)} articles")
    
    print("  Fetching Straits Times...")
    st_articles = fetch_straits_times_articles()
    all_articles.extend(st_articles)
    print(f"    ✓ Straits Times: {len(st_articles)} articles")
    
    print("  Fetching Yahoo Finance Singapore...")
    yf_sg_articles = fetch_yahoo_finance_singapore_articles()
    all_articles.extend(yf_sg_articles)
    print(f"    ✓ Yahoo Finance Singapore: {len(yf_sg_articles)} articles")
    
    print(f"  ✓ Singapore total: {len(all_articles)} articles")
    return all_articles

if __name__ == "__main__":
    # Test the scraper independently
    test_articles = fetch_all()
    print(f"\nTest Results: {len(test_articles)} Singapore articles found")