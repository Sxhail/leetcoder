#!/usr/bin/env python3
"""
unblock.py - Manual script to unblock distracting domains.
"""

from blocker import Blocker

def main():
    """Manually unblock distracting domains."""
    print("🔓 Manual Unblock Script")
    print("=" * 30)
    
    blocker = Blocker()
    
    # Check current status
    if blocker.is_blocked():
        print("🚫 Distractions are currently blocked")
        blocked_domains = blocker.get_blocked_domains()
        print(f"📋 Blocked domains: {', '.join(blocked_domains)}")
        
        # Ask for confirmation
        response = input("\n❓ Do you want to unblock distractions? (y/N): ").strip().lower()
        
        if response in ['y', 'yes']:
            if blocker.unblock_distractions():
                print("✅ Distractions unblocked successfully!")
                print("🌐 You can now access social media and other sites")
            else:
                print("❌ Failed to unblock distractions")
                print("💡 Try running as administrator")
        else:
            print("❌ Unblock cancelled")
    else:
        print("✅ Distractions are not currently blocked")
        print("🌐 All sites are accessible")

if __name__ == "__main__":
    main() 