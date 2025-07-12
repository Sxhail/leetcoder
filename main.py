"""
main.py - Orchestrator for LeetCode Enforcer Bot.
Parses CLI flags and coordinates all modules.
"""

import argparse
import asyncio
import sys
from datetime import datetime, time
from typing import Optional

from auth_manager import AuthManager
from progress_tracker import ProgressTracker
from blocker import Blocker
from workflow_manager import WorkflowManager
from logger import Logger
from notifier import Notifier
from tray_ui import TrayUI
import config

class LeetCodeEnforcer:
    """Main orchestrator for the LeetCode Enforcer Bot."""
    
    def __init__(self):
        self.auth_manager = AuthManager()
        self.blocker = Blocker()
        self.notifier = Notifier()
        self.workflow_manager = WorkflowManager()
        self.logger = None
        self.progress_tracker = None
        self.tray_ui = None
        
        # Initialize components that need credentials
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize components that require credentials."""
        # Get credentials
        leetcode_session = self.auth_manager.get_leetcode_session()
        google_path = self.auth_manager.get_google_service_account_path()
        
        if leetcode_session:
            self.progress_tracker = ProgressTracker(leetcode_session)
        
        if google_path:
            self.logger = Logger(google_path)
    
    async def run_check(self, check_type: str) -> bool:
        """Run a specific check (morning, midday, evening)."""
        print(f"🔍 Running {check_type} check...")
        
        if not self.progress_tracker:
            print("❌ Progress tracker not initialized. Check credentials.")
            return False
        
        try:
            # Determine target and required count based on check type
            if check_type == "morning":
                # Check yesterday's progress
                progress = await self.progress_tracker.check_yesterday_progress()
                required_count = config.MIDDAY_TARGET
                target_date = "yesterday"
            elif check_type == "midday":
                # Check today's progress so far
                progress = await self.progress_tracker.check_today_progress()
                required_count = config.MIDDAY_TARGET
                target_date = "today"
            elif check_type == "evening":
                # Check today's total progress
                progress = await self.progress_tracker.check_today_progress()
                required_count = config.DAILY_TARGET
                target_date = "today"
            else:
                print(f"❌ Unknown check type: {check_type}")
                return False
            
            actual_count = progress.get('blind75_solved', 0)
            solved_problems = progress.get('solved_problems', [])
            success = progress.get('success', False)
            
            if not success:
                print("❌ Failed to get progress data")
                return False
            
            # Determine status
            if actual_count >= required_count:
                status = "on_track"
                print(f"✅ {check_type.title()} check passed: {actual_count}/{required_count} problems solved")
            else:
                status = "behind"
                print(f"⚠️ {check_type.title()} check failed: {actual_count}/{required_count} problems solved")
            
            # Log the check
            if self.logger:
                self.logger.log_check(
                    check_type=check_type,
                    required_count=required_count,
                    actual_count=actual_count,
                    status=status,
                    solved_problems=solved_problems,
                    notes=f"Check for {target_date}"
                )
            
            # Handle being behind on goals
            if status == "behind":
                await self._handle_behind_on_goals(check_type, required_count, actual_count, solved_problems)
            else:
                # If on track and it's evening, unblock distractions
                if check_type == "evening" and status == "on_track":
                    self._unblock_distractions()
                    self.notifier.notify_daily_goal_met()
            
            return True
            
        except Exception as e:
            print(f"❌ Error running {check_type} check: {e}")
            if self.logger:
                self.logger.log_check(
                    check_type=check_type,
                    required_count=0,
                    actual_count=0,
                    status="error",
                    notes=f"Error: {str(e)}"
                )
            return False
    
    async def _handle_behind_on_goals(self, check_type: str, required: int, actual: int, solved_problems: list):
        """Handle being behind on goals."""
        print(f"🚫 Behind on goals. Blocking distractions and opening next problem...")
        
        # Block distractions
        if self.blocker.block_distractions():
            self.notifier.notify_system_blocked()
        
        # Send notification
        self.notifier.notify_behind_on_goals(check_type, required, actual, solved_problems)
        
        # Open next problem
        if self.workflow_manager:
            next_problem = self.workflow_manager.open_next_problem(solved_problems)
            if next_problem:
                print(f"📝 Opened next problem: {next_problem['title']}")
    
    def _unblock_distractions(self):
        """Unblock distractions when goals are met."""
        if self.blocker.unblock_distractions():
            self.notifier.notify_system_unblocked()
    
    async def run_poll(self):
        """Run polling mode (check every 10 minutes when behind)."""
        print("🔄 Starting polling mode...")
        
        if not self.progress_tracker:
            print("❌ Progress tracker not initialized. Check credentials.")
            return
        
        while True:
            try:
                # Check current progress
                progress = await self.progress_tracker.check_today_progress()
                actual_count = progress.get('blind75_solved', 0)
                
                if actual_count >= config.DAILY_TARGET:
                    print("✅ Daily target met. Stopping polling.")
                    self._unblock_distractions()
                    break
                
                print(f"⏰ Polling: {actual_count}/{config.DAILY_TARGET} problems solved")
                
                # Wait for next poll
                await asyncio.sleep(config.POLL_INTERVAL)
                
            except Exception as e:
                print(f"❌ Error in polling: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    def mark_completed(self):
        """Handle manual completion marking."""
        print("✅ Manual completion marked. Re-checking progress...")
        
        # This would typically re-check progress and unblock if needed
        # For now, just unblock distractions
        self._unblock_distractions()
    
    def open_next_problem(self):
        """Handle opening next problem from tray."""
        print("🔗 Opening next problem from tray...")
        
        if self.progress_tracker:
            # Get current progress to determine solved problems
            # This is a simplified version - in practice, you'd get the actual solved problems
            solved_problems = []  # This should be retrieved from progress tracker
            self.workflow_manager.open_next_problem(solved_problems)
    
    def view_logs(self):
        """Handle viewing logs from tray."""
        print("📊 Opening logs...")
        import webbrowser
        webbrowser.open("https://sheets.google.com")
    
    def start_tray_ui(self):
        """Start the system tray interface."""
        if not self.tray_ui:
            self.tray_ui = TrayUI(
                on_mark_completed=self.mark_completed,
                on_open_next_problem=self.open_next_problem,
                on_view_logs=self.view_logs
            )
        
        if self.tray_ui.is_available():
            self.tray_ui.start()
        else:
            print("⚠️ System tray not available")
    
    def setup_credentials(self):
        """Interactive setup for credentials."""
        return self.auth_manager.setup_credentials()

async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="LeetCode Enforcer Bot")
    parser.add_argument("--check", choices=["morning", "midday", "evening"], 
                       help="Run a specific check")
    parser.add_argument("--poll", action="store_true", 
                       help="Run in polling mode")
    parser.add_argument("--setup", action="store_true", 
                       help="Setup credentials")
    parser.add_argument("--tray", action="store_true", 
                       help="Start system tray interface")
    
    args = parser.parse_args()
    
    # Create enforcer instance
    enforcer = LeetCodeEnforcer()
    
    # Handle different modes
    if args.setup:
        enforcer.setup_credentials()
    elif args.check:
        await enforcer.run_check(args.check)
    elif args.poll:
        await enforcer.run_poll()
    elif args.tray:
        enforcer.start_tray_ui()
    else:
        # Default: run appropriate check based on current time
        current_time = datetime.now().time()
        
        if config.MORNING_CHECK_START <= current_time <= config.MORNING_CHECK_END:
            await enforcer.run_check("morning")
        elif current_time.hour == config.MIDDAY_CHECK.hour:
            await enforcer.run_check("midday")
        elif current_time.hour == config.EVENING_CHECK.hour:
            await enforcer.run_check("evening")
        else:
            print("⏰ No scheduled check at this time.")
            print("Use --check, --poll, --setup, or --tray options.")

if __name__ == "__main__":
    asyncio.run(main()) 