# app.py - Flask Web Application for News Scraper
import os
import json
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
import logging

from flask import Flask, render_template, jsonify, request, send_file, redirect, url_for
from flask_socketio import SocketIO, emit
import eventlet

# Import your existing scraper modules
from main import collect_all_news
from excel_generator import create_excel_file
from utils import get_collection_hours, get_output_directory
from config import get_sources_by_country

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app setup
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Global state for scraping status
scraping_state = {
    'running': False,
    'progress': 0,
    'current_source': '',
    'results': {},
    'total_articles': 0,
    'errors': [],
    'start_time': None,
    'last_excel_path': None
}

def emit_progress(progress, message, source_results=None):
    """Emit progress updates to connected clients"""
    scraping_state['progress'] = progress
    scraping_state['current_source'] = message
    
    if source_results:
        scraping_state['results'].update(source_results)
        scraping_state['total_articles'] = sum(len(articles) for articles in scraping_state['results'].values())
    
    socketio.emit('progress_update', {
        'progress': progress,
        'message': message,
        'results': scraping_state['results'],
        'total_articles': scraping_state['total_articles'],
        'running': scraping_state['running']
    })

def run_scraping_task():
    """Background task to run the news scraping"""
    try:
        scraping_state['running'] = True
        scraping_state['start_time'] = datetime.now()
        scraping_state['results'] = {}
        scraping_state['total_articles'] = 0
        scraping_state['errors'] = []
        
        emit_progress(0, "Initializing scrapers...")
        
        # Get collection parameters
        hours = get_collection_hours()
        
        # Track individual source progress
        sources = ['Singapore', 'Japan', 'India', 'Korea', 'Yahoo Finance', 'Others']
        total_sources = len(sources)
        
        # Import scrapers with progress tracking
        from scrapers import singapore, japan, india, korea, yahoo, others
        
        news_by_source = {}
        
        # 1. Singapore
        emit_progress(10, "Collecting Singapore news...")
        try:
            singapore_articles = singapore.fetch_all()
            news_by_source['Singapore'] = singapore_articles
            emit_progress(20, f"Singapore: {len(singapore_articles)} articles collected", {'Singapore': singapore_articles})
        except Exception as e:
            logger.error(f"Singapore collection failed: {e}")
            scraping_state['errors'].append(f"Singapore: {str(e)}")
            news_by_source['Singapore'] = []
            emit_progress(20, "Singapore: Failed to collect articles")
        
        # 2. Japan
        emit_progress(30, "Collecting Japan news...")
        try:
            japan_articles = japan.fetch_articles()
            news_by_source['Japan'] = japan_articles
            emit_progress(40, f"Japan: {len(japan_articles)} articles collected", {'Japan': japan_articles})
        except Exception as e:
            logger.error(f"Japan collection failed: {e}")
            scraping_state['errors'].append(f"Japan: {str(e)}")
            news_by_source['Japan'] = []
            emit_progress(40, "Japan: Failed to collect articles")
        
        # 3. India
        emit_progress(50, "Collecting India news...")
        try:
            india_articles = india.fetch_articles()
            news_by_source['India'] = india_articles
            emit_progress(60, f"India: {len(india_articles)} articles collected", {'India': india_articles})
        except Exception as e:
            logger.error(f"India collection failed: {e}")
            scraping_state['errors'].append(f"India: {str(e)}")
            news_by_source['India'] = []
            emit_progress(60, "India: Failed to collect articles")
        
        # 4. Korea
        emit_progress(70, "Collecting Korea news...")
        try:
            korea_articles = korea.fetch_articles()
            news_by_source['Korea'] = korea_articles
            emit_progress(80, f"Korea: {len(korea_articles)} articles collected", {'Korea': korea_articles})
        except Exception as e:
            logger.error(f"Korea collection failed: {e}")
            scraping_state['errors'].append(f"Korea: {str(e)}")
            news_by_source['Korea'] = []
            emit_progress(80, "Korea: Failed to collect articles")
        
        # 5. Yahoo Finance
        emit_progress(85, "Collecting Yahoo Finance news...")
        try:
            yahoo_articles = yahoo.fetch_articles()
            news_by_source['Yahoo Finance'] = yahoo_articles
            emit_progress(90, f"Yahoo Finance: {len(yahoo_articles)} articles collected", {'Yahoo Finance': yahoo_articles})
        except Exception as e:
            logger.error(f"Yahoo Finance collection failed: {e}")
            scraping_state['errors'].append(f"Yahoo Finance: {str(e)}")
            news_by_source['Yahoo Finance'] = []
            emit_progress(90, "Yahoo Finance: Failed to collect articles")
        
        # 6. Other sources
        emit_progress(95, "Collecting international news...")
        try:
            current_time = datetime.now()
            target_dates = []
            current_date = current_time.date()
            cutoff_time = current_time - timedelta(hours=hours)
            cutoff_date = cutoff_time.date()
            
            target_dates.append(current_date)
            check_date = current_date - timedelta(days=1)
            while check_date >= cutoff_date:
                target_dates.append(check_date)
                check_date -= timedelta(days=1)
            
            other_sources = others.fetch_all_others(hours, target_dates)
            news_by_source.update(other_sources)
            emit_progress(98, f"International sources: {sum(len(articles) for articles in other_sources.values())} articles collected", other_sources)
        except Exception as e:
            logger.error(f"Other sources collection failed: {e}")
            scraping_state['errors'].append(f"Others: {str(e)}")
        
        # Generate Excel file
        emit_progress(99, "Generating Excel file...")
        try:
            success, excel_path = create_excel_file(news_by_source, hours)
            if success:
                scraping_state['last_excel_path'] = excel_path
                emit_progress(100, "Collection completed successfully!")
            else:
                emit_progress(100, "Collection completed with Excel generation error")
                scraping_state['errors'].append("Excel generation failed")
        except Exception as e:
            logger.error(f"Excel generation failed: {e}")
            scraping_state['errors'].append(f"Excel generation: {str(e)}")
            emit_progress(100, "Collection completed with Excel generation error")
        
    except Exception as e:
        logger.error(f"Scraping task failed: {e}")
        scraping_state['errors'].append(f"General error: {str(e)}")
        emit_progress(100, f"Collection failed: {str(e)}")
    
    finally:
        scraping_state['running'] = False
        
        # Final status update
        socketio.emit('scraping_complete', {
            'success': len(scraping_state['errors']) == 0,
            'total_articles': scraping_state['total_articles'],
            'errors': scraping_state['errors'],
            'excel_available': scraping_state['last_excel_path'] is not None,
            'duration': (datetime.now() - scraping_state['start_time']).total_seconds() if scraping_state['start_time'] else 0
        })

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/status')
def api_status():
    """Get current scraping status"""
    return jsonify({
        'running': scraping_state['running'],
        'progress': scraping_state['progress'],
        'current_source': scraping_state['current_source'],
        'results': {k: len(v) for k, v in scraping_state['results'].items()},
        'total_articles': scraping_state['total_articles'],
        'errors': scraping_state['errors'],
        'excel_available': scraping_state['last_excel_path'] is not None
    })

@app.route('/api/start', methods=['POST'])
def api_start_scraping():
    """Start the scraping process"""
    if scraping_state['running']:
        return jsonify({'error': 'Scraping already in progress'}), 400
    
    # Start scraping in background thread
    thread = threading.Thread(target=run_scraping_task)
    thread.daemon = True
    thread.start()
    
    return jsonify({'message': 'Scraping started'})

@app.route('/api/stop', methods=['POST'])
def api_stop_scraping():
    """Stop the scraping process"""
    if not scraping_state['running']:
        return jsonify({'error': 'No scraping in progress'}), 400
    
    scraping_state['running'] = False
    emit_progress(scraping_state['progress'], "Stopping collection...")
    
    return jsonify({'message': 'Scraping stopped'})

@app.route('/api/download')
def api_download_excel():
    """Download the latest Excel file"""
    if not scraping_state['last_excel_path'] or not os.path.exists(scraping_state['last_excel_path']):
        return jsonify({'error': 'No Excel file available'}), 404
    
    try:
        return send_file(
            scraping_state['last_excel_path'],
            as_attachment=True,
            download_name=f"daily_news_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

@app.route('/api/logs')
def api_get_logs():
    """Get recent log entries"""
    try:
        log_entries = []
        
        # Add errors as log entries
        for error in scraping_state['errors']:
            log_entries.append({
                'timestamp': datetime.now().isoformat(),
                'level': 'error',
                'message': error
            })
        
        # Add status updates
        if scraping_state['running']:
            log_entries.append({
                'timestamp': datetime.now().isoformat(),
                'level': 'info',
                'message': f"Progress: {scraping_state['progress']}% - {scraping_state['current_source']}"
            })
        
        # Add results summary
        for source, articles in scraping_state['results'].items():
            log_entries.append({
                'timestamp': datetime.now().isoformat(),
                'level': 'success',
                'message': f"{source}: {len(articles)} articles collected"
            })
        
        return jsonify(log_entries[-20:])  # Return last 20 entries
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info('Client connected')
    emit('status_update', {
        'running': scraping_state['running'],
        'progress': scraping_state['progress'],
        'total_articles': scraping_state['total_articles']
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info('Client disconnected')

if __name__ == '__main__':
    # Ensure output directory exists
    output_dir = get_output_directory()
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 60)
    print("📰 NEWS SCRAPER WEB APPLICATION")
    print("=" * 60)
    print(f"🌐 Dashboard: http://localhost:5000")
    print(f"📁 Output Directory: {output_dir}")
    print("=" * 60)
    
    # Run the Flask app
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)