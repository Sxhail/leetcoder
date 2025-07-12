"""
auth_manager.py - Handles secure retrieval of credentials (LeetCode session, Google service account).
"""

import keyring
import json
import os
from typing import Optional

class AuthManager:
    """Manages secure storage and retrieval of credentials."""
    
    def __init__(self):
        self.service_name = "leetcoder_bot"
        self.leetcode_key = "leetcode_session"
        self.google_key = "google_service_account_path"
    
    def get_leetcode_session(self) -> Optional[str]:
        """Retrieve LeetCode session cookie from secure storage."""
        try:
            session = keyring.get_password(self.service_name, self.leetcode_key)
            if not session:
                print("❌ LeetCode session not found. Please set it using set_leetcode_session().")
                return None
            return session
        except Exception as e:
            print(f"❌ Error retrieving LeetCode session: {e}")
            return None
    
    def set_leetcode_session(self, session: str) -> bool:
        """Store LeetCode session cookie securely."""
        try:
            keyring.set_password(self.service_name, self.leetcode_key, session)
            print("✅ LeetCode session stored successfully.")
            return True
        except Exception as e:
            print(f"❌ Error storing LeetCode session: {e}")
            return False
    
    def get_google_service_account_path(self) -> Optional[str]:
        """Retrieve path to Google service account JSON file."""
        try:
            path = keyring.get_password(self.service_name, self.google_key)
            if not path:
                print("❌ Google service account path not found. Please set it using set_google_service_account_path().")
                return None
            
            if not os.path.exists(path):
                print(f"❌ Google service account file not found at: {path}")
                return None
            
            return path
        except Exception as e:
            print(f"❌ Error retrieving Google service account path: {e}")
            return None
    
    def set_google_service_account_path(self, file_path: str) -> bool:
        """Store path to Google service account JSON file."""
        try:
            if not os.path.exists(file_path):
                print(f"❌ File not found: {file_path}")
                return False
            
            keyring.set_password(self.service_name, self.google_key, file_path)
            print("✅ Google service account path stored successfully.")
            return True
        except Exception as e:
            print(f"❌ Error storing Google service account path: {e}")
            return False
    
    def validate_credentials(self) -> bool:
        """Validate that all required credentials are available."""
        leetcode_session = self.get_leetcode_session()
        google_path = self.get_google_service_account_path()
        
        if not leetcode_session:
            print("❌ LeetCode session is required.")
            return False
        
        if not google_path:
            print("❌ Google service account path is required.")
            return False
        
        print("✅ All credentials are available.")
        return True
    
    def setup_credentials(self) -> bool:
        """Interactive setup for credentials."""
        print("🔧 Setting up LeetCode Enforcer Bot credentials...")
        
        # LeetCode session setup
        print("\n📝 LeetCode Session Setup:")
        print("1. Go to https://leetcode.com and log in")
        print("2. Open Developer Tools (F12)")
        print("3. Go to Application/Storage tab")
        print("4. Find 'LEETCODE_SESSION' cookie and copy its value")
        
        # For testing, you can hardcode the session here temporarily
        # session = "your_session_token_here"
        session = input("Enter your LeetCode session value: ").strip()
        if session:
            self.set_leetcode_session(session)
        
        # Google service account setup
        print("\n📝 Google Service Account Setup:")
        print("1. Go to https://console.cloud.google.com")
        print("2. Create a new project or select existing one")
        print("3. Enable Google Sheets API")
        print("4. Create a service account and download the JSON key file")
        
        json_path = input("Enter the path to your Google service account JSON file: ").strip()
        if json_path:
            self.set_google_service_account_path(json_path)
        
        return self.validate_credentials()

# Example usage
if __name__ == "__main__":
    auth_manager = AuthManager()
    auth_manager.setup_credentials() 