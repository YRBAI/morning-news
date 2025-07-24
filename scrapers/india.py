# scrapers/india.py - Enhanced Hindustan Times India News Scraper

import re
import time
import sys
import os
from urllib.parse import urljoin, urlparse
from datetime import datetime

# Add parent directory to path so we can import config and utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import SOURCES, CONFIG, SELENIUM_AVAILABLE, setup_chrome_driver
from utils import get_content_with_retry, safe_soup_parsing, extract_timestamp_from_element, is_within_timeframe

def extract_category_from_url(url):
    """Extract category from URL pattern"""
    article_patterns = {
        r'/india-news/': 'India News',
        r'/cities/': 'Cities',
        r'/politics/': 'Politics',
        r'/world-news/': 'World News',
        r'/business/': 'Business',
        r'/cricket/': 'Cricket',
        r'/sports/': 'Sports',
        r'/entertainment/': 'Entertainment',
        r'/lifestyle/': 'Lifestyle',
        r'/tech/': 'Technology',
        r'/education/': 'Education',
        r'/health/': 'Health',
        r'/opinion/': 'Opinion',
        r'/editorials/': 'Editorials',
        r'/analysis/': 'Analysis',
        r'/trending/': 'Trending',
        r'/astrology/': 'Astrology',
        r'/videos/': 'Videos',
        r'/photos/': 'Photos'
    }
    
    for pattern, category in article_patterns.items():
        if re.search(pattern, url):
            return category
    return "General"

def extract_articles_from_page(soup, base_url, hours):
    """Extract articles from a single page using multiple strategies"""
    articles = []
    
    if not soup:
        return articles
    
    # Strategy 1: Target elements with data-vars-section attributes (HT specific)
    india_news_containers = soup.find_all(attrs={'data-vars-section': 'India News'})
    print(f"   Found {len(india_news_containers)} containers with data-vars-section='India News'")
    
    for container in india_news_containers:
        # Look for h3 with class hdg3 inside this container
        h3_element = container.find('h3', class_='hdg3')
        if h3_element:
            link = h3_element.find('a')
            if link:
                href = link.get('href', '')
                headline = link.get_text(strip=True)
                article_id = link.get('data-articleid', '')
                
                if len(headline) > 10:
                    # Convert relative URLs to absolute URLs
                    if href.startswith('/'):
                        full_url = base_url.rstrip('/') + href
                    elif not href.startswith('http'):
                        full_url = urljoin(base_url, href)
                    else:
                        full_url = href
                    
                    # Extract timestamp if available
                    timestamp = extract_timestamp_from_element(container)
                    
                    # Check if within timeframe
                    if is_within_timeframe(timestamp, hours):
                        articles.append({
                            'site': 'Hindustan Times India',
                            'headline': headline,
                            'link': full_url,
                            'category': 'India News',
                            'article_id': article_id,
                            'timestamp': timestamp,
                            'source': 'data-vars-section'
                        })
        
        # Also check for direct links in the container
        direct_links = container.find_all('a', href=True)
        for link in direct_links:
            headline = link.get_text(strip=True)
            if len(headline) > 10 and len(headline) < 200:
                href = link.get('href', '')
                article_id = link.get('data-articleid', '')
                
                if href.startswith('/'):
                    full_url = base_url.rstrip('/') + href
                elif not href.startswith('http'):
                    full_url = urljoin(base_url, href)
                else:
                    full_url = href
                
                # Extract timestamp
                timestamp = extract_timestamp_from_element(link)
                
                # Check if within timeframe and avoid duplicates
                if (is_within_timeframe(timestamp, hours) and 
                    not any(art['link'] == full_url for art in articles)):
                    articles.append({
                        'site': 'Hindustan Times India',
                        'headline': headline,
                        'link': full_url,
                        'category': 'India News',
                        'article_id': article_id,
                        'timestamp': timestamp,
                        'source': 'data-vars-section-direct'
                    })
    
    # Strategy 2: Look for h3.hdg3 headlines (common HT pattern)
    hdg3_headlines = soup.find_all('h3', class_='hdg3')
    print(f"   Found {len(hdg3_headlines)} h3.hdg3 headline elements")
    
    for headline_elem in hdg3_headlines:
        link = headline_elem.find('a')
        if link:
            href = link.get('href', '')
            headline = link.get_text(strip=True)
            article_id = link.get('data-articleid', '')
            
            if len(headline) > 10 and len(headline) < 200:
                # Convert relative URLs to absolute URLs
                if href.startswith('/'):
                    full_url = base_url.rstrip('/') + href
                elif not href.startswith('http'):
                    full_url = urljoin(base_url, href)
                else:
                    full_url = href
                
                # Check for parent container with data-vars-section
                parent_with_section = headline_elem.find_parent(attrs={'data-vars-section': True})
                if parent_with_section:
                    category = parent_with_section.get('data-vars-section', 'General')
                else:
                    category = extract_category_from_url(href)
                
                # Extract timestamp
                timestamp = extract_timestamp_from_element(headline_elem)
                
                # Check if within timeframe and avoid duplicates
                if (is_within_timeframe(timestamp, hours) and 
                    not any(art['link'] == full_url for art in articles)):
                    articles.append({
                        'site': 'Hindustan Times India',
                        'headline': headline,
                        'link': full_url,
                        'category': category,
                        'article_id': article_id,
                        'timestamp': timestamp,
                        'source': 'hdg3'
                    })
    
    # Strategy 3: Other headline patterns (if we haven't found enough articles)
    if len(articles) < 5:
        headline_selectors = [
            'h1.hdg1 a',
            'h2.hdg2 a', 
            'h3.hdg4 a',
            'h3.hdg5 a',
            '.headline a',
            '.story-title a',
            '.bigStory a',
            '.leadStory a'
        ]
        
        for selector in headline_selectors:
            elements = soup.select(selector)
            
            for elem in elements[:10]:  # Limit to first 10
                href = elem.get('href', '')
                headline = elem.get_text(strip=True)
                article_id = elem.get('data-articleid', '')
                
                if len(headline) > 10 and len(headline) < 200:
                    # Convert relative URLs to absolute URLs
                    if href.startswith('/'):
                        full_url = base_url.rstrip('/') + href
                    elif not href.startswith('http'):
                        full_url = urljoin(base_url, href)
                    else:
                        full_url = href
                    
                    # Get data-vars-section or extract from URL
                    data_vars_section = elem.get('data-vars-section', '')
                    if data_vars_section:
                        category = data_vars_section
                    else:
                        category = extract_category_from_url(href)
                    
                    # Extract timestamp
                    timestamp = extract_timestamp_from_element(elem)
                    
                    # Filter out navigation and metadata
                    skip_phrases = ['subscribe', 'login', 'menu', 'newsletter', 'about us']
                    if (not any(skip in headline.lower() for skip in skip_phrases) and
                        is_within_timeframe(timestamp, hours) and
                        not any(art['link'] == full_url for art in articles)):
                        articles.append({
                            'site': 'Hindustan Times India',
                            'headline': headline,
                            'link': full_url,
                            'category': category,
                            'article_id': article_id,
                            'timestamp': timestamp,
                            'source': selector
                        })
            
            if len(articles) >= 10:
                break  # Found enough articles
    
    # Strategy 4: General article links (fallback)
    if len(articles) < 3:
        all_links = soup.find_all('a', href=True)
        article_patterns = ['/india-news/', '/cities/', '/politics/', '/world-news/', 
                          '/business/', '/cricket/', '/sports/', '/entertainment/']
        
        for link in all_links:
            href = link.get('href', '')
            headline = link.get_text(strip=True)
            article_id = link.get('data-articleid', '')
            
            # Filter for article-like URLs and meaningful headlines
            if (len(headline) > 15 and len(headline) < 200 and
                any(pattern.strip('/') in href for pattern in article_patterns) and
                not href.startswith('#') and
                not href.startswith('mailto:') and
                not href.startswith('tel:') and
                not href.endswith(('.pdf', '.jpg', '.png', '.gif'))):
                
                # Convert relative URLs to absolute URLs
                if href.startswith('/'):
                    full_url = base_url.rstrip('/') + href
                elif not href.startswith('http'):
                    full_url = urljoin(base_url, href)
                else:
                    full_url = href
                
                # Only include hindustantimes.com URLs
                if 'hindustantimes.com' not in full_url:
                    continue
                
                category = extract_category_from_url(href)
                
                # Extract timestamp
                timestamp = extract_timestamp_from_element(link)
                
                # Filter out non-news items
                skip_phrases = ['subscribe', 'login', 'sign up', 'register', 'newsletter',
                               'about us', 'contact us', 'privacy policy', 'terms',
                               'advertisement', 'sponsored', 'promoted']
                
                if (not any(phrase in headline.lower() for phrase in skip_phrases) and
                    is_within_timeframe(timestamp, hours) and
                    not any(art['link'] == full_url for art in articles)):
                    articles.append({
                        'site': 'Hindustan Times India',
                        'headline': headline,
                        'link': full_url,
                        'category': category,
                        'article_id': article_id,
                        'timestamp': timestamp,
                        'source': 'general-links'
                    })
                    
                    if len(articles) >= 20:  # Limit fallback articles
                        break
    
    print(f"   ✅ Extracted {len(articles)} articles from this page")
    return articles

def fetch_articles_selenium(hours):
    """Fetch articles using Selenium for dynamic content"""
    print("🔧 Using Selenium for enhanced scraping...")
    
    if not SELENIUM_AVAILABLE:
        print("❌ Selenium not available, falling back to requests")
        return fetch_articles_requests(hours)
    
    driver = setup_chrome_driver()
    if not driver:
        print("❌ Failed to setup Chrome driver, falling back to requests")
        return fetch_articles_requests(hours)
    
    all_articles = []
    
    try:
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By
        
        for i, page_url in enumerate(SOURCES['hindustantimes_india']['urls'], 1):
            print(f"  📍 Trying page {i}/{len(SOURCES['hindustantimes_india']['urls'])}: {page_url}")
            
            try:
                # Navigate and wait
                driver.get(page_url)
                WebDriverWait(driver, 15).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                time.sleep(3)
                
                # Parse content
                soup = safe_soup_parsing(driver.page_source)
                
                # Check for loading pages
                if soup and soup.title:
                    page_title = soup.title.string or ""
                    if any(indicator in page_title.lower() for indicator in 
                           ['just a moment', 'loading', 'please wait']):
                        time.sleep(5)
                        soup = safe_soup_parsing(driver.page_source)
                
                # Extract articles
                page_articles = extract_articles_from_page(soup, page_url, hours)
                
                if page_articles:
                    all_articles.extend(page_articles)
                    print(f"  ✅ Page {i}: {len(page_articles)} articles collected")
                else:
                    print(f"  ⚠️ Page {i}: No articles found")
                    
            except Exception as e:
                print(f"  ❌ Error with page {i} ({page_url}): {e}")
                continue
            
            # Rate limiting between pages
            time.sleep(CONFIG['request_delay'])
    
    finally:
        driver.quit()
    
    # Remove duplicates
    unique_articles = []
    seen_links = set()
    
    for article in all_articles:
        if article['link'] not in seen_links:
            seen_links.add(article['link'])
            unique_articles.append(article)
    
    return unique_articles

def fetch_articles_requests(hours):
    """Fetch articles using requests library (fallback method)"""
    print("🌐 Using requests library for scraping...")
    
    articles = []
    
    for i, page_url in enumerate(SOURCES['hindustantimes_india']['urls'], 1):
        print(f"  📍 Trying page {i}/{len(SOURCES['hindustantimes_india']['urls'])}: {page_url}")
        
        response = get_content_with_retry(page_url)
        if not response:
            print(f"  ❌ Failed to fetch page {i}")
            continue
            
        content = response.content if hasattr(response, 'content') else response.text
        soup = safe_soup_parsing(content)
        if not soup:
            print(f"  ❌ Failed to parse page {i}")
            continue
        
        page_articles = extract_articles_from_page(soup, page_url, hours)
        
        if page_articles:
            articles.extend(page_articles)
            print(f"  ✅ Page {i}: {len(page_articles)} articles collected")
        else:
            print(f"  ⚠️ Page {i}: No articles found")
        
        # Rate limiting between pages
        time.sleep(CONFIG['request_delay'])
    
    # Remove duplicates
    unique_articles = []
    seen_links = set()
    
    for article in articles:
        if article['link'] not in seen_links:
            seen_links.add(article['link'])
            unique_articles.append(article)
    
    return unique_articles

def fetch_articles():
    """Main function to fetch Hindustan Times India news articles"""
    print("📰 Fetching India news from Hindustan Times...")
    
    # Get collection hours from utils
    from utils import get_collection_hours
    hours = get_collection_hours()
    
    # Try Selenium first for better results, fallback to requests
    try:
        articles = fetch_articles_selenium(hours)
    except Exception as e:
        print(f"⚠️ Selenium method failed: {e}")
        articles = fetch_articles_requests(hours)
    
    # Filter to focus on India News
    india_articles = []
    for art in articles:
        # Prioritize India News category
        if 'India News' in art.get('category', ''):
            # Add India News tag to headline for better identification
            if not art['headline'].startswith('[India News]'):
                art['headline'] = f"[India News] {art['headline']}"
            india_articles.append(art)
        elif any(keyword in art.get('category', '').lower() for keyword in ['cities', 'politics']):
            # Include related categories with tags
            category_tag = art.get('category', 'General')
            if not art['headline'].startswith(f'[{category_tag}]'):
                art['headline'] = f"[{category_tag}] {art['headline']}"
            india_articles.append(art)
    
    # If we have India-specific articles, use those; otherwise use all
    final_articles = india_articles if india_articles else articles
    
    print(f"  ✅ Hindustan Times India: {len(final_articles)} articles collected total")
    
    # Debug: Print first few articles if any found
    if final_articles:
        print("  📋 Sample articles:")
        for i, art in enumerate(final_articles[:3]):
            print(f"    {i+1}. {art['headline'][:60]}...")
            if art.get('category'):
                print(f"       Category: {art['category']}")
            if art.get('timestamp'):
                print(f"       Time: {art['timestamp']}")
    else:
        print("  ⚠️  No articles found - this might indicate a parsing issue")
        print("      This could be due to:")
        print("      - Website structure changes")
        print("      - Network issues")
        print("      - Rate limiting")
        print("      - Content loading dynamically (try enabling Selenium)")
    
    return final_articles

if __name__ == "__main__":
    # Test the scraper independently
    print("🧪 Testing India scraper independently...")
    test_articles = fetch_articles()
    print(f"\n📊 Test Results: {len(test_articles)} India articles found")
    
    if test_articles:
        print("\n📋 Sample articles:")
        for i, article in enumerate(test_articles[:5]):
            print(f"{i+1}. {article['headline']}")
            print(f"   🔗 {article['link']}")
            print(f"   📂 Category: {article.get('category', 'N/A')}")
            print(f"   ⏰ Time: {article.get('timestamp', 'N/A')}")
            print(f"   🔍 Source: {article.get('source', 'N/A')}")
            print()
    else:
        print("❌ No articles found during testing")