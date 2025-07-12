"""
config.py - Stores configuration variables such as domains, check times, and other settings.
"""

import os
from datetime import time

# Check times
MORNING_CHECK_START = time(9, 0)  # 9:00 AM
MORNING_CHECK_END = time(11, 0)   # 11:00 AM
MIDDAY_CHECK = time(12, 0)        # 12:00 PM
EVENING_CHECK = time(18, 0)       # 6:00 PM

# Daily targets
DAILY_TARGET = 2  # problems per day (unblock after 2)
MIDDAY_TARGET = 1  # problems by midday

# Distracting domains to block
DISTRACTING_DOMAINS = [
    "facebook.com",
    "instagram.com",
    "twitter.com",
    "x.com",
    "tiktok.com",
    "youtube.com",
    "reddit.com",
    "netflix.com",
    "hulu.com",
    "disneyplus.com",
    "amazon.com",
    "ebay.com",
    "etsy.com",
    "pinterest.com",
    "snapchat.com",
    "discord.com",
    "twitch.tv",
    "spotify.com",
    "apple.com",
    "microsoft.com"
]

# LeetCode settings
LEETCODE_BASE_URL = "https://leetcode.com"
NEETCODE_BASE_URL = "https://neetcode.io"

# File paths
HOSTS_FILE = r"C:\Windows\System32\drivers\etc\hosts"
PROBLEMS_FILE = "problems.json"

# Notification settings
NOTIFICATION_TITLE = "LeetCode Enforcer"
NOTIFICATION_ICON = "icon.ico"  # You'll need to add this icon file

# Polling interval (seconds) when behind on goals
POLL_INTERVAL = 600  # 10 minutes 