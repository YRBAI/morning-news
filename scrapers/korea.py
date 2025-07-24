# scrapers/korea.py - SEdaily Korea News

import sys
import os
import requests
import time
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator

# Add parent directory to path so we can import config and utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import SOURCES, KOREAN_HEADERS

def _is_korean_text(text):
    """Helper function to detect if text contains Korean characters"""
    korean_pattern = re.compile(r'[가-힣]')
    return bool(korean_pattern.search(text))

def fetch_sedaily_news(base_url, translate_to_english=True):
    """Function to fetch SEdaily news articles with optional translation"""
    
    # Initialize Google Translator using deep_translator
    translator = GoogleTranslator(source='ko', target='en') if translate_to_english else None
    
    print(f"  Fetching SEdaily news from: {base_url}")
    if translate_to_english:
        print("  Translation: Korean → English enabled")
    
    try:
        # Make HTTP GET request to fetch the webpage - using requests directly like working version
        response = requests.get(base_url, headers=KOREAN_HEADERS, timeout=15)
        response.raise_for_status()
        
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        articles = []
        
        # METHOD 1: TARGET THE SPECIFIC STRUCTURE (same as working version)
        # Find all divs with class "sub_lv_tit" (headlines)
        headline_divs = soup.find_all('div', class_='sub_lv_tit')
        print(f"  Found {len(headline_divs)} sub_lv_tit headline elements")
        
        for headline_div in headline_divs:
            # Get the parent anchor tag
            parent_link = headline_div.find_parent('a')
            if not parent_link:
                continue
            
            href = parent_link.get('href', '')
            headline_korean = headline_div.get_text(strip=True)
            
            # Skip if headline is too short
            if len(headline_korean) < 5:
                continue
            
            # Translate headline if requested
            if translate_to_english and translator:
                try:
                    headline_english = translator.translate(headline_korean)
                except Exception as e:
                    print(f"  Translation failed for: {headline_korean[:50]}... Error: {e}")
                    headline_english = headline_korean  # Keep original if translation fails
            else:
                headline_english = headline_korean
            
            # Convert relative URLs to absolute URLs
            if href.startswith('http'):
                full_url = href
            else:
                # Handle sedaily.com URLs
                full_url = urljoin('https://www.sedaily.com', href)
            
            # Find category information
            category_korean = "General"
            category_english = "General"
            
            # Look for the text_info div that should follow
            next_sibling = parent_link.find_next_sibling('div', class_='text_info')
            if next_sibling:
                sec_span = next_sibling.find('span', class_='sec')
                if sec_span:
                    category_korean = sec_span.get_text(strip=True)
                    
                    # Translate category if requested
                    if translate_to_english and translator:
                        try:
                            category_english = translator.translate(category_korean)
                        except Exception as e:
                            print(f"  Category translation failed: {category_korean}")
                            category_english = category_korean
                    else:
                        category_english = category_korean
            
            # Add to articles list if not duplicate
            if not any(art['link'] == full_url for art in articles):
                articles.append({
                    'site': 'SEdaily Korea',
                    'headline': f"[{category_english}] {headline_english}",
                    'link': full_url,
                    'category_korean': category_korean,
                    'category_english': category_english,
                    'headline_korean': headline_korean,
                    'headline_english': headline_english
                })
        
        # METHOD 2: ALTERNATIVE PARSING FOR SEDAILY SITE (same as working version)
        if len(articles) < 5:
            print("  Trying alternative SEdaily parsing methods...")
            
            # Common Korean news site selectors
            alternative_selectors = [
                '.news_tit a',
                '.title a',
                '.headline a',
                '.article-title a',
                '.news-title a',
                'h2 a',
                'h3 a',
                '.sub_tit a',
                '.main_tit a'
            ]
            
            for selector in alternative_selectors:
                elements = soup.select(selector)
                print(f"  Found {len(elements)} elements with selector: {selector}")
                
                for elem in elements:
                    href = elem.get('href', '')
                    headline = elem.get_text(strip=True)
                    
                    if len(headline) < 10:
                        continue
                    
                    # Convert relative URLs to absolute URLs
                    if href.startswith('http'):
                        full_url = href
                    else:
                        full_url = urljoin('https://www.sedaily.com', href)
                    
                    # Only include sedaily.com URLs
                    if 'sedaily.com' not in full_url:
                        continue
                    
                    # Translate if needed
                    if translate_to_english and translator and _is_korean_text(headline):
                        try:
                            headline_english = translator.translate(headline)
                        except:
                            headline_english = headline
                    else:
                        headline_english = headline
                    
                    category = "General"
                    
                    # Add if not already found
                    if not any(art['headline'].endswith(headline_english) for art in articles):
                        articles.append({
                            'site': 'SEdaily Korea',
                            'headline': f"[{category}] {headline_english}",
                            'link': full_url
                        })
        
        # METHOD 3: GENERAL ARTICLE LINK PARSING (same as working version)
        if len(articles) < 3:
            print("  Trying general article link parsing...")
            
            # Find all links that look like article URLs
            all_links = soup.find_all('a', href=True)
            
            for link in all_links:
                href = link.get('href', '')
                headline = link.get_text(strip=True)
                
                # Filter for SEdaily article-like URLs and meaningful headlines
                if (len(headline) > 10 and len(headline) < 200 and
                    ('NewsView' in href or 'news' in href) and
                    not href.startswith('#') and
                    not href.startswith('mailto:') and
                    not href.startswith('tel:')):
                    
                    # Convert relative URLs to absolute URLs
                    if href.startswith('http'):
                        full_url = href
                    else:
                        full_url = urljoin('https://www.sedaily.com', href)
                    
                    # Only include sedaily.com URLs
                    if 'sedaily.com' not in full_url:
                        continue
                    
                    # Translate if needed
                    if translate_to_english and translator and _is_korean_text(headline):
                        try:
                            headline_english = translator.translate(headline)
                        except:
                            headline_english = headline
                    else:
                        headline_english = headline
                    
                    category = "General"
                    
                    # Add if not already found
                    if not any(art['headline'].endswith(headline_english) for art in articles):
                        articles.append({
                            'site': 'SEdaily Korea',
                            'headline': f"[{category}] {headline_english}",
                            'link': full_url
                        })
        
        # DEDUPLICATION (same as working version)
        seen_items = set()
        unique_articles = []
        for article in articles:
            item_key = (article['headline'], article['link'])
            if item_key not in seen_items:
                seen_items.add(item_key)
                unique_articles.append(article)
        
        articles = unique_articles
        
        return articles
        
    except Exception as e:
        print(f"  Error fetching SEdaily news: {e}")
        return []

def fetch_articles():
    """Main function to fetch Korea news articles from SEdaily Korea"""
    print("Fetching Korea news...")
    
    url = SOURCES['sedaily_korea']['url']
    print(f"  Using URL: {url}")
    
    # Use the working function with translation enabled
    articles = fetch_sedaily_news(url, translate_to_english=True)
    
    print(f"  ✓ SEdaily Korea: {len(articles)} articles collected")
    
    # Debug: Print first few articles if any found
    if articles:
        print("  Sample articles:")
        for i, art in enumerate(articles[:3]):
            print(f"    {i+1}. {art['headline'][:60]}...")
    else:
        print("  ⚠️  No articles found - this might indicate a parsing issue")
    
    return articles

if __name__ == "__main__":
    # Test the scraper independently - use the working URL and method
    print("=== SEdaily Korea News Scraper with Translation ===")
    test_articles = fetch_articles()
    print(f"\nTest Results: {len(test_articles)} Korea articles found")
    
    # Also test the direct function like the working version
    print("\n=== Direct Function Test ===")
    sedaily_url = "https://www.sedaily.com/v/NewsMain/GC"
    direct_articles = fetch_sedaily_news(sedaily_url, translate_to_english=True)
    print(f"Direct test results: {len(direct_articles)} articles found")