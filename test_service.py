#!/usr/bin/env python3
"""
test_service.py - Test the LeetCode Enforcer service functionality.
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import LeetCodeEnforcer
import config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def test_service():
    """Test the service functionality."""
    print("🧪 Testing LeetCode Enforcer Service")
    print("=" * 40)
    
    try:
        # Create enforcer instance (same as service would)
        print("🔧 Initializing LeetCode Enforcer...")
        enforcer = LeetCodeEnforcer()
        
        # Test tray UI
        print("🎨 Testing system tray...")
        enforcer.start_tray_ui()
        
        # Test a check
        print("📊 Testing morning check...")
        await enforcer.run_check("morning")
        
        # Run for a short time to test
        print("⏱️ Running for 30 seconds...")
        await asyncio.sleep(30)
        
        print("✅ Service test completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⏹️ Service test interrupted by user")
    except Exception as e:
        print(f"❌ Service test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_service()) 