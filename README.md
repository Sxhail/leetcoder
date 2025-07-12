# LeetCode Enforcer Bot

A lightweight Python-based productivity tool that ensures you solve at least **4 LeetCode Blind 75 series** questions every day. If you haven't met your daily target by the morning check, it blocks distractions and guides you through your pending problems—with **adaptive micro-goals** and **smart reminders** to keep you on track.

## 📖 Overview

Each day the bot:

1. **Adaptive micro-goal checks** (half-day targets)  
2. **Morning check** between 9 AM–11 AM: did you solve at least 2 problems yesterday?  
3. **Midday check** at 12 PM: did you solve at least 2 problems so far today?  
4. **Evening check** at 6 PM: did you solve a total of 4 problems today?  
5. If any check fails, it blocks distractions and guides you through the next pending Blind 75 problem until you hit the daily target.

## ⚙️ Key Features

- **Adaptive Scheduling & Smart Reminders**  
  - **Micro-goals:** 1 problem by 12 PM, then 2 total by 6 PM.  
  - **Dynamic nudges:** Desktop or phone push notifications at each check if you're behind.

- **System-wide blocking** of distracting domains via hosts-file edits  
- **Guided problem workflow:** opens NeetCode → LeetCode for each pending Blind 75 question  
- **Progress polling** every 10 minutes until the micro-goal or daily target is met  
  
- **Manual "Completed" button** to finalize and re-verify via LeetCode API  

## 🏗️ Architecture

### Core Components

1. **Scheduler (Windows Task Scheduler)**
   - Triggers main.py with flags:
     • `--check=morning` at 09:00
     • `--check=midday` at 12:00
     • `--check=evening` at 18:00
     • `--poll` every 10 minutes when behind

2. **Orchestrator (main.py)**
   - Parses CLI flags and coordinates all modules
   - Calls AuthManager, ProgressTracker, then either Logger or Blocker+Workflow+Notifier

3. **AuthManager**
   - Securely stores and retrieves LeetCode session cookie
   - Uses keyring for secure credential storage

4. **ProgressTracker**
   - Uses Playwright to query LeetCode GraphQL API
   - Tracks Blind 75 progress and submission timestamps
   - Compares against problems.json (Blind 75 list)

5. **Blocker**
   - Edits C:\Windows\System32\drivers\etc\hosts to block distracting domains
   - Removes entries when target is met

6. **WorkflowManager**
   - Opens next unsolved problem on NeetCode.io and LeetCode.com
   - Provides progress summaries and problem suggestions



8. **Notifier**
   - Uses Windows Toast notifications with plyer fallback
   - Sends contextual notifications based on progress

7. **TrayUI**
   - System tray icon with menu for manual actions
   - Mark Completed, Open Next Problem, View Logs

## 🚀 Installation

### Prerequisites

- Python 3.8+
- Windows 10/11 (for hosts file editing and Windows Task Scheduler)
- LeetCode account

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/leetcoder.git
   cd leetcoder
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers**
   ```bash
   playwright install chromium
   ```

4. **Setup credentials**
   ```bash
   python main.py --setup
   ```

### Credential Setup

#### LeetCode Session
1. Go to https://leetcode.com and log in
2. Open Developer Tools (F12)
3. Go to Application/Storage tab
4. Find 'LEETCODE_SESSION' cookie and copy its value
5. Enter it when prompted during setup



## 📋 Usage

### Command Line Options

```bash
# Setup credentials
python main.py --setup

# Run specific checks
python main.py --check=morning
python main.py --check=midday
python main.py --check=evening

# Run polling mode (when behind on goals)
python main.py --poll

# Start system tray interface
python main.py --tray

# Run appropriate check based on current time
python main.py
```

### Windows Task Scheduler Setup

1. Open Task Scheduler
2. Create Basic Task
3. Set triggers:
   - Morning: 09:00 daily
   - Midday: 12:00 daily
   - Evening: 18:00 daily
4. Action: Start a program
   - Program: `python`
   - Arguments: `main.py --check=morning` (adjust for each task)
5. Enable "Run with highest privileges"
6. Enable "Run as soon as possible after a missed start"

### System Tray

Right-click the system tray icon for:
- **Mark Completed**: Re-check progress and unblock if goals met
- **Open Next Problem**: Open next unsolved Blind 75 problem
- **View Logs**: Logs functionality removed (Google Sheets integration disabled)
- **Exit**: Stop the bot

## 📊 Configuration

Edit `config.py` to customize:

- Check times and targets
- Distracting domains to block
- Polling intervals
- File paths and settings

## 📈 Progress Tracking

The bot tracks your progress through:

1. **LeetCode API Integration**: Queries your submission history
2. **Blind 75 List**: Complete list of 75 essential problems
3. **Console Logging**: Progress logged to console output

## 🔧 Troubleshooting

### Common Issues

1. **"No write permission for hosts file"**
   - Run as administrator or check file permissions

2. **"LeetCode session not found"**
   - Re-run setup: `python main.py --setup`



3. **"Progress tracker not initialized"**
   - Verify LeetCode session is valid and not expired

### Debug Mode

Run individual modules for testing:

```bash
# Test progress tracking
python progress_tracker.py

# Test blocking
python blocker.py

# Test notifications
python notifier.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [LeetCode](https://leetcode.com) for the problem platform
- [NeetCode](https://neetcode.io) for the Blind 75 list
- [Playwright](https://playwright.dev) for browser automation


## 📞 Support

If you encounter any issues or have questions:

1. Check the troubleshooting section
2. Search existing issues
3. Create a new issue with detailed information

---
