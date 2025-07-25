"""
Browser history data collection module
Supports Chrome, Edge, and Firefox browsers
"""

import sqlite3
import shutil
import tempfile
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class BrowserActivity:
    """Represents a single browser activity"""
    timestamp: datetime
    url: str
    title: str
    visit_count: int
    browser: str
    domain: str


class BrowserCollector:
    """Collects browser history data from various browsers"""
    
    def __init__(self, settings):
        """Initialize browser collector with settings"""
        self.settings = settings
        self.browser_paths = {
            'chrome': self.settings.expand_path(
                self.settings.get('data_sources.browser.chrome_path')
            ),
            'edge': self.settings.expand_path(
                self.settings.get('data_sources.browser.edge_path')
            ),
            'firefox': self.settings.expand_path(
                self.settings.get('data_sources.browser.firefox_path')
            )
        }
    
    def collect(self, target_date: date) -> List[BrowserActivity]:
        """Collect browser history for the specified date"""
        if not self.settings.is_enabled('browser'):
            return []
        
        all_activities = []
        
        # Collect from each browser
        for browser_name, db_path in self.browser_paths.items():
            try:
                activities = self._collect_from_browser(browser_name, db_path, target_date)
                all_activities.extend(activities)
                print(f"   📱 {browser_name.title()}: {len(activities)} entries")
            except Exception as e:
                print(f"   ❌ {browser_name.title()}: Error - {str(e)}")
        
        return sorted(all_activities, key=lambda x: x.timestamp)
    
    def _collect_from_browser(self, browser: str, db_path: str, target_date: date) -> List[BrowserActivity]:
        """Collect history from a specific browser"""
        if not Path(db_path).exists():
            return []
        
        if browser == 'firefox':
            return self._collect_firefox_history(db_path, target_date)
        else:
            return self._collect_chromium_history(browser, db_path, target_date)
    
    def _collect_chromium_history(self, browser: str, db_path: str, target_date: date) -> List[BrowserActivity]:
        """Collect history from Chromium-based browsers (Chrome, Edge)"""
        activities = []
        
        # Create temporary copy to avoid locking issues
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            try:
                # Try multiple times with different methods
                copied = False
                temp_path = tmp_file.name
                
                # Method 1: Try direct copy
                try:
                    shutil.copy2(db_path, temp_path)
                    copied = True
                except (OSError, PermissionError) as e:
                    print(f"      🔄 {browser.title()} locked, trying alternative method...")
                
                # Method 2: Try reading in smaller chunks if direct copy fails
                if not copied:
                    try:
                        with open(db_path, 'rb') as src, open(temp_path, 'wb') as dst:
                            # Copy in small chunks to avoid locking issues
                            while True:
                                chunk = src.read(8192)  # 8KB chunks
                                if not chunk:
                                    break
                                dst.write(chunk)
                        copied = True
                    except (OSError, PermissionError) as e:
                        print(f"      ❌ {browser.title()}: Cannot access database (browser may be running)")
                        return activities
                
                if not copied:
                    return activities
                
                # Connect to the temporary database
                conn = sqlite3.connect(temp_path)
                cursor = conn.cursor()
                
                # Calculate timestamp range for target date
                start_time = datetime.combine(target_date, datetime.min.time())
                end_time = start_time + timedelta(days=1)
                
                # Chrome/Edge stores timestamps as microseconds since 1601-01-01
                chrome_epoch = datetime(1601, 1, 1)
                start_chrome_time = int((start_time - chrome_epoch).total_seconds() * 1000000)
                end_chrome_time = int((end_time - chrome_epoch).total_seconds() * 1000000)
                
                # Query history
                query = """
                    SELECT 
                        urls.url,
                        urls.title,
                        urls.visit_count,
                        visits.visit_time
                    FROM urls
                    JOIN visits ON urls.id = visits.url
                    WHERE visits.visit_time >= ? AND visits.visit_time < ?
                    ORDER BY visits.visit_time DESC
                """
                
                cursor.execute(query, (start_chrome_time, end_chrome_time))
                rows = cursor.fetchall()
                
                for url, title, visit_count, visit_time in rows:
                    # Convert Chrome timestamp to Python datetime
                    timestamp = chrome_epoch + timedelta(microseconds=visit_time)
                    domain = self._extract_domain(url)
                    
                    # Skip if URL should be excluded for privacy
                    if self._should_exclude_url(url, title):
                        continue
                    
                    activities.append(BrowserActivity(
                        timestamp=timestamp,
                        url=url,
                        title=title or "Untitled",
                        visit_count=visit_count,
                        browser=browser,
                        domain=domain
                    ))
                
                conn.close()
                
            finally:
                # Clean up temporary file
                Path(temp_path).unlink(missing_ok=True)
        
        return activities
    
    def _collect_firefox_history(self, profiles_path: str, target_date: date) -> List[BrowserActivity]:
        """Collect history from Firefox (places.sqlite)"""
        activities = []
        
        # Find Firefox profile directories
        profiles_dir = Path(profiles_path)
        if not profiles_dir.exists():
            return activities
        
        for profile_dir in profiles_dir.glob("*.default*"):
            places_db = profile_dir / "places.sqlite"
            if not places_db.exists():
                continue
            
            try:
                # Create temporary copy
                with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
                    shutil.copy2(places_db, tmp_file.name)
                    
                    conn = sqlite3.connect(tmp_file.name)
                    cursor = conn.cursor()
                    
                    # Calculate timestamp range (Firefox uses microseconds since Unix epoch)
                    start_time = datetime.combine(target_date, datetime.min.time())
                    end_time = start_time + timedelta(days=1)
                    start_firefox_time = int(start_time.timestamp() * 1000000)
                    end_firefox_time = int(end_time.timestamp() * 1000000)
                    
                    # Query Firefox history
                    query = """
                        SELECT 
                            moz_places.url,
                            moz_places.title,
                            moz_places.visit_count,
                            moz_historyvisits.visit_date
                        FROM moz_places
                        JOIN moz_historyvisits ON moz_places.id = moz_historyvisits.place_id
                        WHERE moz_historyvisits.visit_date >= ? AND moz_historyvisits.visit_date < ?
                        ORDER BY moz_historyvisits.visit_date DESC
                    """
                    
                    cursor.execute(query, (start_firefox_time, end_firefox_time))
                    rows = cursor.fetchall()
                    
                    for url, title, visit_count, visit_date in rows:
                        timestamp = datetime.fromtimestamp(visit_date / 1000000)
                        domain = self._extract_domain(url)
                        
                        if self._should_exclude_url(url, title):
                            continue
                        
                        activities.append(BrowserActivity(
                            timestamp=timestamp,
                            url=url,
                            title=title or "Untitled",
                            visit_count=visit_count,
                            browser="firefox",
                            domain=domain
                        ))
                    
                    conn.close()
                    Path(tmp_file.name).unlink(missing_ok=True)
            
            except Exception as e:
                print(f"   ⚠️  Firefox profile {profile_dir.name}: {str(e)}")
        
        return activities
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc.lower()
        except:
            return "unknown"
    
    def _should_exclude_url(self, url: str, title: str) -> bool:
        """Check if URL should be excluded for privacy reasons"""
        exclude_patterns = self.settings.get('processing.privacy.exclude_urls', [])
        
        url_lower = url.lower()
        title_lower = (title or "").lower()
        
        for pattern in exclude_patterns:
            pattern_lower = pattern.lower()
            if pattern_lower in url_lower or pattern_lower in title_lower:
                return True
        
        return False
