#!/usr/bin/env python3
"""
test_simple.py - Simple test of LeetCode Enforcer functionality.
"""

import asyncio
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import LeetCodeEnforcer

async def test_simple():
    """Simple test of the enforcer functionality."""
    print("🧪 Simple LeetCode Enforcer Test")
    print("=" * 35)
    
    try:
        # Create enforcer instance
        print("🔧 Initializing LeetCode Enforcer...")
        enforcer = LeetCodeEnforcer()
        
        # Test morning check
        print("\n📊 Testing morning check...")
        await enforcer.run_check("morning")
        
        print("\n✅ Test completed successfully!")
        print("🎯 The enforcer is working correctly!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_simple()) 