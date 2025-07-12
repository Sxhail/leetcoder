"""
auth_manager.py - Handles secure retrieval of LeetCode session credentials.
"""

import keyring
import json
import os
from typing import Optional

class AuthManager:
    """Manages secure storage and retrieval of LeetCode session credentials."""
    
    def __init__(self):
        self.service_name = "leetcoder_bot"
        self.leetcode_key = "leetcode_session"
    
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
    
    def validate_credentials(self) -> bool:
        """Validate that LeetCode session is available."""
        leetcode_session = self.get_leetcode_session()
        
        if not leetcode_session:
            print("❌ LeetCode session is required.")
            return False
        
        print("✅ LeetCode session is available.")
        return True
    
    def setup_credentials(self) -> bool:
        """Interactive setup for LeetCode session credentials."""
        print("🔧 Setting up LeetCode Enforcer Bot credentials...")
        
        # LeetCode session setup
        print("\n📝 LeetCode Session Setup:")
        print("1. Go to https://leetcode.com and log in")
        print("2. Open Developer Tools (F12)")
        print("3. Go to Application/Storage tab")
        print("4. Find 'LEETCODE_SESSION' cookie and copy its value")
        
        session = input("Enter your LeetCode session value: ").strip()
        if session:
            self.set_leetcode_session(session)
        
        return self.validate_credentials()

# Example usage
if __name__ == "__main__":
    auth_manager = AuthManager()
    auth_manager.setup_credentials() 