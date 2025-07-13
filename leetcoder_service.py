#!/usr/bin/env python3
"""
leetcoder_service.py - Windows service that runs LeetCode Enforcer Bot continuously in background.
"""

import asyncio
import time
import logging
import sys
import os
import threading
from datetime import datetime, time as dt_time
from typing import Optional
import win32serviceutil
import win32service
import win32event
import servicemanager

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import LeetCodeEnforcer
import config
from command_handler import register_callback, start_listening, stop_listening

class LeetCodeEnforcerService(win32serviceutil.ServiceFramework):
    """Windows service for LeetCode Enforcer Bot."""
    
    _svc_name_ = "LeetCodeEnforcer"
    _svc_display_name_ = "LeetCode Enforcer Bot"
    _svc_description_ = "Automated LeetCode progress tracking and distraction blocking service"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.enforcer = None
        self.tray_ui = None
        self.is_running = False
        
        # Setup logging
        logging.basicConfig(
            filename='C:\\leetcoder_service.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def SvcStop(self):
        """Stop the service."""
        logging.info("Service stop requested")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.is_running = False
    
    def SvcDoRun(self):
        """Run the service."""
        logging.info("Service starting")
        self.is_running = True
        self._run_service()
    
    def _run_service(self):
        """Main service loop."""
        try:
            # Initialize the enforcer
            self.enforcer = LeetCodeEnforcer()
            logging.info("LeetCode Enforcer initialized")
            
            # Register command callbacks
            self._register_commands()
            
            # Start command listener
            start_listening()
            logging.info("Command listener started")
            
            # Start system tray in background thread
            self._start_tray_ui()
            
            # Run the main loop
            asyncio.run(self._main_loop())
            
        except Exception as e:
            logging.error(f"Service error: {e}")
            self.is_running = False
        finally:
            stop_listening()
    
    def _register_commands(self):
        """Register command callbacks."""
        register_callback("mark_completed", self._mark_completed)
        register_callback("open_next_problem", self._open_next_problem)
        register_callback("view_logs", self._view_logs)
    
    def _start_tray_ui(self):
        """Start the system tray interface in background."""
        try:
            import threading
            from tray_ui import TrayUI
            
            def tray_worker():
                try:
                    self.tray_ui = TrayUI(
                        on_mark_completed=self._mark_completed,
                        on_open_next_problem=self._open_next_problem,
                        on_view_logs=self._view_logs
                    )
                    
                    if self.tray_ui.is_available():
                        logging.info("System tray started")
                        self.tray_ui.start()
                    else:
                        logging.warning("System tray not available")
                        
                except Exception as e:
                    logging.error(f"Tray UI error: {e}")
            
            # Start tray in background thread
            tray_thread = threading.Thread(target=tray_worker, daemon=True)
            tray_thread.start()
            
        except Exception as e:
            logging.error(f"Error starting tray UI: {e}")
    
    def _mark_completed(self, data=None):
        """Handle manual completion marking from tray."""
        logging.info("Manual completion marked from tray")
        try:
            if self.enforcer:
                self.enforcer.mark_completed()
            else:
                logging.warning("Enforcer not initialized")
        except Exception as e:
            logging.error(f"Error in mark completed: {e}")
    
    def _open_next_problem(self, data=None):
        """Handle opening next problem from tray."""
        logging.info("Opening next problem from tray")
        try:
            if self.enforcer:
                # Run in a new thread to handle async
                def run_async():
                    try:
                        if self.enforcer:
                            asyncio.run(self.enforcer.open_next_problem())
                    except Exception as e:
                        logging.error(f"Error in async open_next_problem: {e}")
                
                threading.Thread(target=run_async, daemon=True).start()
            else:
                logging.warning("Enforcer not initialized")
        except Exception as e:
            logging.error(f"Error opening next problem: {e}")
    
    def _view_logs(self, data=None):
        """Handle viewing logs from tray."""
        logging.info("View logs requested from tray")
        print("📊 Logs functionality removed (Google Sheets integration disabled)")
    
    async def _main_loop(self):
        """Main service loop that runs continuously."""
        logging.info("Starting main service loop")
        
        while self.is_running:
            try:
                current_time = datetime.now().time()
                
                # Check if it's time for scheduled checks
                if self._should_run_morning_check(current_time):
                    logging.info("Running morning check")
                    if self.enforcer:
                        await self.enforcer.run_check("morning")
                    await asyncio.sleep(60)  # Wait 1 minute after check
                
                elif self._should_run_midday_check(current_time):
                    logging.info("Running midday check")
                    if self.enforcer:
                        await self.enforcer.run_check("midday")
                    await asyncio.sleep(60)  # Wait 1 minute after check
                
                elif self._should_run_evening_check(current_time):
                    logging.info("Running evening check")
                    if self.enforcer:
                        await self.enforcer.run_check("evening")
                    await asyncio.sleep(60)  # Wait 1 minute after check
                
                # Check if we should run polling (when behind on goals)
                elif self._should_run_polling(current_time):
                    logging.info("Running polling mode")
                    await self._run_polling_mode()
                
                # Sleep for a short interval
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logging.error(f"Error in main loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    def _should_run_morning_check(self, current_time: dt_time) -> bool:
        """Check if morning check should run."""
        return (config.MORNING_CHECK_START <= current_time <= config.MORNING_CHECK_END and 
                current_time.minute == 0)  # Run at the hour
    
    def _should_run_midday_check(self, current_time: dt_time) -> bool:
        """Check if midday check should run."""
        return (current_time.hour == config.MIDDAY_CHECK.hour and 
                current_time.minute == 0)  # Run at the hour
    
    def _should_run_evening_check(self, current_time: dt_time) -> bool:
        """Check if evening check should run."""
        return (current_time.hour == config.EVENING_CHECK.hour and 
                current_time.minute == 0)  # Run at the hour
    
    def _should_run_polling(self, current_time: dt_time) -> bool:
        """Check if polling should run (when behind on goals)."""
        # This would need to be implemented based on current progress
        # For now, return False
        return False
    
    async def _run_polling_mode(self):
        """Run polling mode when behind on goals."""
        try:
            if self.enforcer:
                await self.enforcer.run_poll()
        except Exception as e:
            logging.error(f"Error in polling mode: {e}")

def install_service():
    """Install the Windows service."""
    try:
        win32serviceutil.InstallService(
            LeetCodeEnforcerService._svc_name_,
            LeetCodeEnforcerService._svc_display_name_,
            LeetCodeEnforcerService._svc_description_
        )
        print("✅ Service installed successfully")
        print("🚀 To start the service, run as administrator:")
        print("   python leetcoder_service.py start")
    except Exception as e:
        print(f"❌ Error installing service: {e}")

def uninstall_service():
    """Uninstall the Windows service."""
    try:
        win32serviceutil.RemoveService(LeetCodeEnforcerService._svc_name_)
        print("✅ Service uninstalled successfully")
    except Exception as e:
        print(f"❌ Error uninstalling service: {e}")

if __name__ == '__main__':
    if len(sys.argv) == 1:
        # Run as service
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(LeetCodeEnforcerService)
        servicemanager.StartServiceCtrlDispatcher()
    elif sys.argv[1] == 'install':
        install_service()
    elif sys.argv[1] == 'uninstall':
        uninstall_service()
    else:
        # Handle other service commands
        win32serviceutil.HandleCommandLine(LeetCodeEnforcerService) 