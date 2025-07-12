"""
logger.py - Logs check results to Google Sheets and handles offline caching.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import gspread
from google.oauth2.service_account import Credentials
import config

class Logger:
    """Logs check results to Google Sheets with offline caching."""
    
    def __init__(self, google_service_account_path: str):
        self.google_service_account_path = google_service_account_path
        self.sheet_name = config.SHEET_NAME
        self.worksheet_name = config.WORKSHEET_NAME
        self.offline_cache_file = config.OFFLINE_CACHE_FILE
        self.scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        self.credentials: Optional[Credentials] = None
        self.client: Optional[gspread.Client] = None
        self.worksheet: Optional[gspread.Worksheet] = None
    
    def _load_credentials(self) -> bool:
        """Load Google service account credentials."""
        try:
            self.credentials = Credentials.from_service_account_file(
                self.google_service_account_path, 
                scopes=self.scope
            )
            return True
        except Exception as e:
            print(f"❌ Error loading Google credentials: {e}")
            return False
    
    def _connect_to_sheets(self) -> bool:
        """Connect to Google Sheets."""
        try:
            if not self._load_credentials():
                return False
            
            self.client = gspread.authorize(self.credentials)
            
            # Try to open existing sheet, create if not exists
            try:
                self.worksheet = self.client.open(self.sheet_name).worksheet(self.worksheet_name)
            except gspread.SpreadsheetNotFound:
                # Create new spreadsheet
                spreadsheet = self.client.create(self.sheet_name)
                self.worksheet = spreadsheet.add_worksheet(title=self.worksheet_name, rows=1000, cols=10)
                self._setup_headers()
            except gspread.WorksheetNotFound:
                # Create new worksheet
                spreadsheet = self.client.open(self.sheet_name)
                self.worksheet = spreadsheet.add_worksheet(title=self.worksheet_name, rows=1000, cols=10)
                self._setup_headers()
            
            return True
        except Exception as e:
            print(f"❌ Error connecting to Google Sheets: {e}")
            return False
    
    def _setup_headers(self):
        """Set up column headers in the worksheet."""
        if self.worksheet is None:
            return
            
        headers = [
            'Date',
            'Check Type',
            'Required Count',
            'Actual Count',
            'Status',
            'Solved Problems',
            'Timestamp',
            'Notes'
        ]
        self.worksheet.update('A1:H1', [headers])
    
    def _load_offline_cache(self) -> List[Dict]:
        """Load offline cache from file."""
        try:
            if os.path.exists(self.offline_cache_file):
                with open(self.offline_cache_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"❌ Error loading offline cache: {e}")
            return []
    
    def _save_offline_cache(self, cache: List[Dict]):
        """Save offline cache to file."""
        try:
            with open(self.offline_cache_file, 'w') as f:
                json.dump(cache, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving offline cache: {e}")
    
    def _add_to_offline_cache(self, log_entry: Dict):
        """Add a log entry to offline cache."""
        cache = self._load_offline_cache()
        cache.append(log_entry)
        self._save_offline_cache(cache)
    
    def _sync_offline_cache(self) -> bool:
        """Sync offline cache to Google Sheets."""
        cache = self._load_offline_cache()
        if not cache:
            return True
        
        try:
            if not self._connect_to_sheets():
                return False
            
            # Convert cache entries to rows
            rows = []
            for entry in cache:
                row = [
                    entry.get('date', ''),
                    entry.get('check_type', ''),
                    entry.get('required_count', ''),
                    entry.get('actual_count', ''),
                    entry.get('status', ''),
                    ', '.join(entry.get('solved_problems', [])),
                    entry.get('timestamp', ''),
                    entry.get('notes', '')
                ]
                rows.append(row)
            
            # Append to worksheet
            if rows and self.worksheet is not None:
                self.worksheet.append_rows(rows)
                print(f"✅ Synced {len(rows)} offline entries to Google Sheets")
            
            # Clear offline cache
            self._save_offline_cache([])
            return True
            
        except Exception as e:
            print(f"❌ Error syncing offline cache: {e}")
            return False
    
    def log_check(self, check_type: str, required_count: int, actual_count: int, 
                  status: str, solved_problems: Optional[List[str]] = None, notes: str = "") -> bool:
        """Log a check result."""
        if solved_problems is None:
            solved_problems = []
        
        log_entry = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'check_type': check_type,
            'required_count': required_count,
            'actual_count': actual_count,
            'status': status,
            'solved_problems': solved_problems,
            'timestamp': datetime.now().isoformat(),
            'notes': notes
        }
        
        # Try to connect to Google Sheets
        if self._connect_to_sheets():
            try:
                # Append to worksheet
                row = [
                    log_entry['date'],
                    log_entry['check_type'],
                    log_entry['required_count'],
                    log_entry['actual_count'],
                    log_entry['status'],
                    ', '.join(log_entry['solved_problems']),
                    log_entry['timestamp'],
                    log_entry['notes']
                ]
                
                if self.worksheet is not None:
                    self.worksheet.append_row(row)
                    print(f"✅ Logged {check_type} check to Google Sheets")
                
                # Sync any offline cache
                self._sync_offline_cache()
                return True
                
            except Exception as e:
                print(f"❌ Error logging to Google Sheets: {e}")
                # Fall back to offline cache
                self._add_to_offline_cache(log_entry)
                print(f"📝 Logged to offline cache (will sync when online)")
                return False
        else:
            # Store in offline cache
            self._add_to_offline_cache(log_entry)
            print(f"📝 Logged to offline cache (will sync when online)")
            return False
    
    def get_recent_logs(self, days: int = 7) -> List[Dict]:
        """Get recent logs from Google Sheets."""
        try:
            if not self._connect_to_sheets():
                return []
            
            # Get all data
            all_records = self.worksheet.get_all_records()
            
            # Filter by date
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            recent_logs = [
                record for record in all_records 
                if record.get('Date', '') >= cutoff_date
            ]
            
            return recent_logs
            
        except Exception as e:
            print(f"❌ Error getting recent logs: {e}")
            return []
    
    def get_today_logs(self) -> List[Dict]:
        """Get today's logs."""
        today = datetime.now().strftime('%Y-%m-%d')
        
        try:
            if not self._connect_to_sheets():
                return []
            
            # Get all data
            all_records = self.worksheet.get_all_records()
            
            # Filter by today's date
            today_logs = [
                record for record in all_records 
                if record.get('Date', '') == today
            ]
            
            return today_logs
            
        except Exception as e:
            print(f"❌ Error getting today's logs: {e}")
            return []
    
    def get_offline_cache_count(self) -> int:
        """Get the number of entries in offline cache."""
        cache = self._load_offline_cache()
        return len(cache)

# Example usage
if __name__ == "__main__":
    from auth_manager import AuthManager
    
    auth_manager = AuthManager()
    google_path = auth_manager.get_google_service_account_path()
    
    if google_path:
        logger = Logger(google_path)
        
        # Example log entry
        logger.log_check(
            check_type="morning",
            required_count=2,
            actual_count=1,
            status="behind",
            solved_problems=["two-sum"],
            notes="Need to solve one more problem"
        )
    else:
        print("❌ Google service account path not found") 