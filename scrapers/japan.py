# scrapers/japan.py - Nikkei Asia News Scraper

import requests
import sys
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import re

# Add parent directory to path so we can import config and utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import SOURCES, HEADERS, CONFIG
from utils import get_content_with_retry, safe_soup_parsing

def fetch_nikkei_news(base_url):
    """Function to fetch Nikkei Asia news articles"""
    
    print(f"Fetching Nikkei Asia news from: {base_url}")
    
    try:
        # Make HTTP GET request to fetch the webpage
        response = get_content_with_retry(base_url, HEADERS)
        if not response:
            return []
        
        # Parse the HTML content using BeautifulSoup
        soup = safe_soup_parsing(response.content)
        if not soup:
            return []
        
        articles = []
        
        # METHOD 1: TARGET DIRECT HEADLINE LINKS
        # Look for anchor tags with data-trackable="headline" and class="Link_link__qPD1b"
        headline_links = soup.find_all('a', {
            'class': 'Link_link__qPD1b',
            'data-trackable': 'headline'
        })
        
        print(f"  Found {len(headline_links)} direct headline links")
        
        # Define URL patterns that indicate Nikkei Asia article categories
        article_patterns = [
            r'/Economy/',
            r'/Politics/',
            r'/Business/',
            r'/Technology/',
            r'/Markets/',
            r'/Companies/',
            r'/Startups/',
            r'/Editor-s-Picks/',
            r'/Opinion/',
            r'/Asia300/',
            r'/Location/East-Asia/Japan',
            r'/Location/East-Asia/China',
            r'/Location/East-Asia/South-Korea',
            r'/Location/Southeast-Asia/',
            r'/Location/South-Asia/',
            r'/Spotlight/'
        ]
        
        # Process direct headline links
        for link in headline_links:
            href = link.get('href', '')
            headline = link.get_text(strip=True)
            
            # Skip if headline is too short
            if len(headline) < 10:
                continue
            
            # Convert relative URLs to absolute URLs
            if href.startswith('http'):
                full_url = href
            else:
                full_url = urljoin('https://asia.nikkei.com', href)
            
            # Extract category from URL pattern
            category = "General"
            for pattern in article_patterns:
                if re.search(pattern, href):
                    # Clean up category name
                    if '/Economy/' in pattern:
                        category = "Economy"
                    elif '/Politics/' in pattern:
                        category = "Politics"
                    elif '/Business/' in pattern:
                        category = "Business"
                    elif '/Technology/' in pattern:
                        category = "Technology"
                    elif '/Markets/' in pattern:
                        category = "Markets"
                    elif '/Companies/' in pattern:
                        category = "Companies"
                    elif '/Startups/' in pattern:
                        category = "Startups"
                    elif '/Editor-s-Picks/' in pattern:
                        category = "Editor's Picks"
                    elif '/Opinion/' in pattern:
                        category = "Opinion"
                    elif '/Asia300/' in pattern:
                        category = "Asia300"
                    elif '/Location/East-Asia/Japan' in pattern:
                        category = "Japan"
                    elif '/Location/East-Asia/China' in pattern:
                        category = "China"
                    elif '/Location/East-Asia/South-Korea' in pattern:
                        category = "South Korea"
                    elif '/Location/Southeast-Asia/' in pattern:
                        category = "Southeast Asia"
                    elif '/Location/South-Asia/' in pattern:
                        category = "South Asia"
                    elif '/Spotlight/' in pattern:
                        category = "Spotlight"
                    break
            
            # Add to articles list if not duplicate
            if not any(art['link'] == full_url for art in articles):
                articles.append({
                    'site': 'Nikkei Asia',
                    'headline': f"[{category}] {headline}",
                    'link': full_url
                })
        
        # METHOD 2: SPOTLIGHT ARTICLE CARD PARSING (FALLBACK)
        if len(articles) < 5:
            print("  Trying spotlight article card parsing...")
            # Target the specific h2 elements with class "SpotlightArticleCard_spotlightArticleCardHeadline__dQZAA"
            spotlight_headlines = soup.find_all('h2', class_='SpotlightArticleCard_spotlightArticleCardHeadline__dQZAA')
            
            print(f"  Found {len(spotlight_headlines)} spotlight article headlines")
            
            # Iterate through spotlight headline elements to extract article information
            for headline_elem in spotlight_headlines:
                # Find the anchor tag within the h2 element
                link = headline_elem.find('a', class_='Link_link__qPD1b')
                
                if not link:
                    continue
                    
                href = link.get('href', '')
                headline = link.get_text(strip=True)
                
                # Skip if headline is too short
                if len(headline) < 10:
                    continue
                
                # Convert relative URLs to absolute URLs
                if href.startswith('http'):
                    full_url = href
                else:
                    full_url = urljoin('https://asia.nikkei.com', href)
                
                # Extract category from URL pattern
                category = "General"
                for pattern in article_patterns:
                    if re.search(pattern, href):
                        # Use same category extraction logic as above
                        if '/Economy/' in pattern:
                            category = "Economy"
                        elif '/Politics/' in pattern:
                            category = "Politics"
                        elif '/Business/' in pattern:
                            category = "Business"
                        elif '/Technology/' in pattern:
                            category = "Technology"
                        elif '/Markets/' in pattern:
                            category = "Markets"
                        elif '/Companies/' in pattern:
                            category = "Companies"
                        elif '/Startups/' in pattern:
                            category = "Startups"
                        elif '/Editor-s-Picks/' in pattern:
                            category = "Editor's Picks"
                        elif '/Opinion/' in pattern:
                            category = "Opinion"
                        elif '/Asia300/' in pattern:
                            category = "Asia300"
                        elif '/Location/East-Asia/Japan' in pattern:
                            category = "Japan"
                        elif '/Location/East-Asia/China' in pattern:
                            category = "China"
                        elif '/Location/East-Asia/South-Korea' in pattern:
                            category = "South Korea"
                        elif '/Location/Southeast-Asia/' in pattern:
                            category = "Southeast Asia"
                        elif '/Location/South-Asia/' in pattern:
                            category = "South Asia"
                        elif '/Spotlight/' in pattern:
                            category = "Spotlight"
                        break
                
                # Add to articles list if not duplicate
                if not any(art['link'] == full_url for art in articles):
                    articles.append({
                        'site': 'Nikkei Asia',
                        'headline': f"[{category}] {headline}",
                        'link': full_url
                    })
        
        # METHOD 3: ALTERNATIVE HEADLINE PARSING (ADDITIONAL FALLBACK)
        if len(articles) < 5:
            print("  Trying alternative headline parsing methods...")
            
            # Try other possible headline selectors
            alternative_selectors = [
                'a[data-trackable="headline"]',  # Any link with data-trackable="headline"
                'h2 a[data-trackable="headline"]',
                'h3 a[data-trackable="headline"]',
                '.headline a',
                '.article-title a',
                'h2.headline',
                'h3.headline'
            ]
            
            for selector in alternative_selectors:
                elements = soup.select(selector)
                print(f"  Found {len(elements)} elements with selector: {selector}")
                
                for elem in elements:
                    if elem.name == 'a':
                        link_elem = elem
                        headline = elem.get_text(strip=True)
                    else:
                        link_elem = elem.find('a')
                        headline = elem.get_text(strip=True)
                    
                    if not link_elem:
                        continue
                    
                    href = link_elem.get('href', '')
                    
                    if len(headline) < 10:
                        continue
                    
                    # Convert relative URLs to absolute URLs
                    if href.startswith('http'):
                        full_url = href
                    else:
                        full_url = urljoin('https://asia.nikkei.com', href)
                    
                    # Extract category from URL
                    category = "General"
                    for pattern in article_patterns:
                        if re.search(pattern, href):
                            category = pattern.strip('/').split('/')[-1].replace('-', ' ').title()
                            break
                    
                    # Add if not already found
                    if not any(art['headline'].endswith(headline) for art in articles):
                        articles.append({
                            'site': 'Nikkei Asia',
                            'headline': f"[{category}] {headline}",
                            'link': full_url
                        })
        
        # METHOD 4: GENERAL LINK PARSING (LAST RESORT)
        if len(articles) < 3:
            print("  Trying general link parsing...")
            
            # Find all links that look like article URLs
            all_links = soup.find_all('a', href=True)
            
            for link in all_links:
                href = link.get('href', '')
                headline = link.get_text(strip=True)
                
                # Filter for article-like URLs and meaningful headlines
                if (len(headline) > 15 and len(headline) < 200 and
                    ('/' in href) and
                    not href.startswith('#') and
                    not href.startswith('mailto:') and
                    not href.startswith('tel:') and
                    not href.endswith('.pdf') and
                    not href.endswith('.jpg') and
                    not href.endswith('.png')):
                    
                    # Convert relative URLs to absolute URLs
                    if href.startswith('http'):
                        full_url = href
                    else:
                        full_url = urljoin('https://asia.nikkei.com', href)
                    
                    # Only include nikkei.com URLs
                    if 'nikkei.com' not in full_url:
                        continue
                    
                    # Extract category from URL
                    category = "General"
                    for pattern in article_patterns:
                        if re.search(pattern, href):
                            category = pattern.strip('/').split('/')[-1].replace('-', ' ').title()
                            break
                    
                    # Add if not already found
                    if not any(art['headline'].endswith(headline) for art in articles):
                        articles.append({
                            'site': 'Nikkei Asia',
                            'headline': f"[{category}] {headline}",
                            'link': full_url
                        })
        
        # DEDUPLICATION
        # Remove duplicate articles based on headline and URL
        seen_items = set()
        unique_articles = []
        for article in articles:
            item_key = (article['headline'], article['link'])
            if item_key not in seen_items:
                seen_items.add(item_key)
                unique_articles.append(article)
        
        return unique_articles
        
    except Exception as e:
        print(f"  Error fetching Nikkei Asia news: {e}")
        return []

def fetch_articles():
    """Main function to fetch Japan news articles from Nikkei Asia"""
    print("Fetching Japan news...")
    articles = []
    
    # Fetch from multiple pages
    for i, page_url in enumerate(SOURCES['nikkei_japan']['urls'], 1):
        print(f"  Trying page {i}/{len(SOURCES['nikkei_japan']['urls'])}: {page_url}")
        
        page_articles = fetch_nikkei_news(page_url)
        articles.extend(page_articles)
        
        print(f"  ✓ Page {i}: {len(page_articles)} articles collected")
        
        # Rate limiting between pages
        time.sleep(CONFIG['request_delay'])
    
    print(f"  ✓ Nikkei Asia Japan: {len(articles)} articles collected total")
    
    # Debug: Print first few articles if any found
    if articles:
        print("  Sample articles:")
        for i, art in enumerate(articles[:3]):
            print(f"    {i+1}. {art['headline'][:60]}...")
    else:
        print("  ⚠️  No articles found - this might indicate a parsing issue")
    
    return articles

if __name__ == "__main__":
    # Test the scraper independently
    test_articles = fetch_articles()
    print(f"\nTest Results: {len(test_articles)} articles found")