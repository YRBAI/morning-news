# main.py - Enhanced Main Entry Point for News Scraper

import sys
from datetime import datetime, timedelta
from config import SELENIUM_AVAILABLE
from utils import get_collection_hours, get_executable_dir, get_output_directory, log_scraping_success, measure_performance, ensure_utf8_environment

# Import all scrapers
from scrapers import singapore, japan, india, korea, others, yahoo  # Added yahoo import
from excel_generator import create_excel_file

@measure_performance
def collect_all_news():
    """Main function to collect news from all sources with enhanced error handling"""
    print("NEWS SCRAPER - Starting enhanced collection...")
    print("=" * 50)
    
    hours = get_collection_hours()
    current_time = datetime.now()
    cutoff_time = current_time - timedelta(hours=hours)
    
    # Calculate target dates
    target_dates = []
    current_date = current_time.date()
    cutoff_date = cutoff_time.date()
    
    target_dates.append(current_date)
    check_date = current_date - timedelta(days=1)
    while check_date >= cutoff_date:
        target_dates.append(check_date)
        check_date -= timedelta(days=1)
    
    print(f"Collection period: {hours} hours")
    print(f"Target dates: {len(target_dates)} days")
    print("-" * 50)
    
    # Collect articles by source - ORDERED: Singapore, Japan, India, Korea, Yahoo Finance, others
    news_by_source = {}
    collection_stats = {}
    
    # 1. Singapore (1st sheet) - All Singapore sources combined
    print("🇸🇬 Collecting Singapore news...")
    try:
        singapore_articles = singapore.fetch_all()
        news_by_source['Singapore'] = singapore_articles
        collection_stats['Singapore'] = len(singapore_articles)
        log_scraping_success('Singapore Combined', 'Multiple URLs', len(singapore_articles))
    except Exception as e:
        print(f"❌ Singapore collection failed: {e}")
        news_by_source['Singapore'] = []
        collection_stats['Singapore'] = 0
    
    # 2. Japan (2nd sheet) - Nikkei Asia
    print("🇯🇵 Collecting Japan news...")
    try:
        japan_articles = japan.fetch_articles()
        news_by_source['Japan'] = japan_articles
        collection_stats['Japan'] = len(japan_articles)
        log_scraping_success('Nikkei Asia', 'Japan section', len(japan_articles))
    except Exception as e:
        print(f"❌ Japan collection failed: {e}")
        news_by_source['Japan'] = []
        collection_stats['Japan'] = 0
    
    # 3. India (3rd sheet) - Enhanced Hindustan Times
    print("🇮🇳 Collecting India news...")
    try:
        india_articles = india.fetch_articles()
        news_by_source['India'] = india_articles
        collection_stats['India'] = len(india_articles)
        log_scraping_success('Hindustan Times India', 'India News section', len(india_articles))
    except Exception as e:
        print(f"❌ India collection failed: {e}")
        news_by_source['India'] = []
        collection_stats['India'] = 0
    
    # 4. Korea (4th sheet) - SEdaily Korea
    print("🇰🇷 Collecting Korea news...")
    try:
        korea_articles = korea.fetch_articles()
        news_by_source['Korea'] = korea_articles
        collection_stats['Korea'] = len(korea_articles)
        log_scraping_success('SEdaily Korea', 'Main section', len(korea_articles))
    except Exception as e:
        print(f"❌ Korea collection failed: {e}")
        news_by_source['Korea'] = []
        collection_stats['Korea'] = 0
    
    # 5. Yahoo Finance (5th sheet) - Financial news
    print("💰 Collecting Yahoo Finance news...")
    try:
        yahoo_articles = yahoo.fetch_articles()
        news_by_source['Yahoo Finance'] = yahoo_articles
        collection_stats['Yahoo Finance'] = len(yahoo_articles)
        log_scraping_success('Yahoo Finance', 'Multiple topics', len(yahoo_articles))
    except Exception as e:
        print(f"❌ Yahoo Finance collection failed: {e}")
        news_by_source['Yahoo Finance'] = []
        collection_stats['Yahoo Finance'] = 0
    
    # 6. Other sources (6th+ sheets)
    print("🌍 Collecting international news...")
    try:
        other_sources = others.fetch_all_others(hours, target_dates)
        news_by_source.update(other_sources)
        for source_name, articles in other_sources.items():
            collection_stats[source_name] = len(articles)
            log_scraping_success(source_name, 'Various URLs', len(articles))
    except Exception as e:
        print(f"❌ International sources collection failed: {e}")
    
    # Print collection summary
    print("\n" + "=" * 50)
    print("COLLECTION SUMMARY")
    print("=" * 50)
    total_articles = sum(len(articles) for articles in news_by_source.values())
    print(f"📊 Total articles collected: {total_articles}")
    print(f"⏱️ Collection period: {hours} hours")
    print()
    
    print("📋 Articles by source:")
    for source_name, count in collection_stats.items():
        status = "✓" if count > 0 else "⚠"
        print(f"  {status} {source_name}: {count} articles")
    
    if total_articles == 0:
        print("\n⚠️ No articles collected from any source!")
        print("This might be due to:")
        print("- Network connectivity issues")
        print("- Website structure changes")
        print("- Rate limiting or blocking")
        print("- Selenium not properly configured")
    
    return news_by_source, hours

def check_system_requirements():
    """Check if all required components are available"""
    print("🔍 Checking system requirements...")
    
    requirements = {
        'requests': False,
        'beautifulsoup4': False,
        'pandas': False,
        'openpyxl': False,
        'deep_translator': False,
        'selenium': SELENIUM_AVAILABLE
    }
    
    # Check required packages
    try:
        import requests
        requirements['requests'] = True
    except ImportError:
        pass
    
    try:
        from bs4 import BeautifulSoup
        requirements['beautifulsoup4'] = True
    except ImportError:
        pass
    
    try:
        import pandas
        requirements['pandas'] = True
    except ImportError:
        pass
    
    try:
        import openpyxl
        requirements['openpyxl'] = True
    except ImportError:
        pass
    
    try:
        from deep_translator import GoogleTranslator
        requirements['deep_translator'] = True
    except ImportError:
        pass
    
    # Report results
    missing_packages = [pkg for pkg, available in requirements.items() if not available]
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Install missing packages with:")
        for pkg in missing_packages:
            if pkg == 'selenium':
                print(f"  pip install {pkg} webdriver-manager")
            else:
                print(f"  pip install {pkg}")
        return False
    else:
        print("✓ All required packages available")
        return True

def main():
    """Enhanced main entry point for the application"""
    try:
        # Show startup info
        ensure_utf8_environment()
        print("NEWS SCRAPER v4.0 - Enhanced Multi-Country Edition with Yahoo Finance")
        print("=" * 80)
        print(f"Executable location: {get_executable_dir()}")
        print(f"Output directory: {get_output_directory()}")
        print()
        
        # Check system requirements
        if not check_system_requirements():
            print("\n❌ System requirements not met. Please install missing packages.")
            if not getattr(sys, 'frozen', False):
                input("Press Enter to exit...")
            return
        
        # Check Selenium availability with detailed info
        if SELENIUM_AVAILABLE:
            print("✓ Selenium available - Enhanced scraping enabled for India and Singapore")
            print("  - India: Hindustan Times with dynamic content loading")
            print("  - Singapore: Edge Singapore with JavaScript rendering")
        else:
            print("⚠ Selenium not available - Using fallback methods")
            print("  - India: Hindustan Times (requests-based fallback)")
            print("  - Singapore: Edge Singapore scraping disabled")
            print("  📝 Install selenium with: pip install selenium webdriver-manager")
        print()
        
        # Verify all scraper modules with enhanced error handling
        missing_functions = []
        try:
            if not hasattr(singapore, 'fetch_all'):
                missing_functions.append('singapore.fetch_all')
        except Exception as e:
            missing_functions.append(f'singapore module: {e}')
            
        try:
            if not hasattr(japan, 'fetch_articles'):
                missing_functions.append('japan.fetch_articles')
        except Exception as e:
            missing_functions.append(f'japan module: {e}')
            
        try:
            if not hasattr(india, 'fetch_articles'):
                missing_functions.append('india.fetch_articles')
        except Exception as e:
            missing_functions.append(f'india module: {e}')
            
        try:
            if not hasattr(korea, 'fetch_articles'):
                missing_functions.append('korea.fetch_articles')
        except Exception as e:
            missing_functions.append(f'korea module: {e}')
            
        try:
            if not hasattr(yahoo, 'fetch_articles'):
                missing_functions.append('yahoo.fetch_articles')
        except Exception as e:
            missing_functions.append(f'yahoo module: {e}')
            
        try:
            if not hasattr(others, 'fetch_all_others'):
                missing_functions.append('others.fetch_all_others')
        except Exception as e:
            missing_functions.append(f'others module: {e}')
        
        if missing_functions:
            print(f"❌ Missing scraper functions: {', '.join(missing_functions)}")
            print("\n🔧 Troubleshooting:")
            print("1. Make sure all scraper files are in the 'scrapers' folder")
            print("2. Check that __init__.py exists in the scrapers folder")
            print("3. Verify each scraper file has the required function")
            print("4. Check for syntax errors in scraper files")
            
            # Try to provide more specific guidance
            if 'others.fetch_all_others' in missing_functions:
                print("\n📝 For others.py:")
                print("- Make sure fetch_all_others function is defined")
                print("- Check for syntax errors in others.py")
                print("- Verify the file is saved properly")
            
            if 'yahoo.fetch_articles' in missing_functions:
                print("\n📝 For yahoo.py:")
                print("- Make sure fetch_articles function is defined")
                print("- Check for syntax errors in yahoo.py")
                print("- Verify the file is saved properly")
            
            if not getattr(sys, 'frozen', False):
                input("Press Enter to exit...")
            return
        else:
            print("✓ All scraper modules verified and loaded")
        
        print("\n📋 Collection Strategy:")
        print("Sheet Order and Sources:")
        print("1. 🇸🇬 Singapore (Edge Singapore + Business Times + Straits Times + Yahoo Finance SG)")
        print("2. 🇯🇵 Japan (Nikkei Asia - Location/East-Asia/Japan)")
        print("3. 🇮🇳 India (Enhanced Hindustan Times with multiple scraping strategies)")
        print("4. 🇰🇷 Korea (SEdaily Korea with Korean→English translation)")
        print("5. 💰 Yahoo Finance (Investing, Stocks, Latest Financial News)")
        print("6+. 🌍 International (TradeWinds, Bloomberg, TrendForce, UDN, GMK Center)")
        print()
        
        print("🚀 Enhanced Features:")
        print("- Multi-strategy scraping for India news (Selenium + requests fallback)")
        print("- Yahoo Finance integration with multiple topics")
        print("- Advanced timestamp parsing and timeframe filtering")
        print("- Enhanced duplicate detection with fuzzy matching")
        print("- Improved error handling and recovery")
        print("- Performance monitoring and logging")
        print("- Korean-English translation for Korea news")
        print()
        
        # Collect news with enhanced monitoring
        print("🔄 Starting enhanced news collection...")
        news_by_source, hours = collect_all_news()
        
        # Save results with enhanced error handling
        print("\n💾 Saving results to Excel...")
        try:
            success, excel_path = create_excel_file(news_by_source, hours)
            
            if success:
                print("=" * 80)
                print("🎉 NEWS COLLECTION COMPLETED SUCCESSFULLY!")
                print("=" * 80)
                print()
                print("✨ Enhanced multi-country news collection completed!")
                print("📊 Excel file created with standardized country sheets:")
                print("• Singapore, Japan, India, Korea, Yahoo Finance as priority sheets")
                print("• Additional international sources following")
                print("• Enhanced India coverage with multiple scraping strategies")
                print("• Korean content automatically translated to English")
                print("• Yahoo Finance with investing, stocks, and latest news")
                print()
                print(f"📁 Results saved to: {excel_path}")
                print("🔗 Single-click hyperlinks for easy article access")
                print("📋 Organized by country/region for efficient reading")
                print()
                print("💡 Tips:")
                print("- Click 'Click to open' links to read full articles")
                print("- India sheet includes multiple categories (India News, Cities, Politics)")
                print("- Yahoo Finance sheet includes investing, stocks, and latest news")
                print("- All timestamps filtered for relevance")
                print("- Duplicates automatically removed")
                print()
                print("You can find your results in the 'news_collection' folder on your Desktop.")
                
            else:
                print("=" * 80)
                print("❌ NEWS COLLECTION FAILED!")
                print("=" * 80)
                print("Excel file creation failed. Check the error messages above.")
        
        except Exception as e:
            print(f"❌ Error during Excel generation: {e}")
            import traceback
            traceback.print_exc()
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Operation cancelled by user.")
        print("Partial results may have been saved.")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        print("Please check your internet connection and try again.")
        print("\n🔍 Debug information:")
        import traceback
        traceback.print_exc()
    
    # Exit handling
    if not getattr(sys, 'frozen', False):
        input("\nPress Enter to exit...")
    else:
        print("\n✅ Automation completed. Exiting in 3 seconds...")
        import time
        time.sleep(3)

if __name__ == "__main__":
    main() 