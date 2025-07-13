"""
tray_ui.py - Provides a system tray interface for manual actions (mark completed, open next problem, view logs).
"""

import threading
import webbrowser
import os
import sys
from typing import Optional, Callable
import config
from command_handler import send_command

class TrayUI:
    """System tray interface for LeetCode Enforcer Bot."""
    
    def __init__(self, on_mark_completed: Optional[Callable] = None,
                 on_open_next_problem: Optional[Callable] = None,
                 on_view_logs: Optional[Callable] = None):
        self.on_mark_completed = on_mark_completed
        self.on_open_next_problem = on_open_next_problem
        self.on_view_logs = on_view_logs
        self.icon = None
        self.is_running = False
    
    def _create_icon(self):
        """Create the system tray icon."""
        try:
            import pystray
            from PIL import Image, ImageDraw
            
            # Create a simple icon (16x16 pixels) with LeetCode colors
            image = Image.new('RGB', (16, 16), color=(26, 26, 26))  # type: ignore
            draw = ImageDraw.Draw(image)
            
            # Draw a simple "LC" (LeetCode) text in LeetCode orange
            draw.text((2, 2), "LC", fill=(255, 161, 22), font=None)  # type: ignore
            
            # Create menu items
            menu = pystray.Menu(
                pystray.MenuItem("Mark Completed", self._mark_completed),
                pystray.MenuItem("Open Next Problem", self._open_next_problem),
                pystray.MenuItem("View Logs", self._view_logs),
                pystray.MenuItem("Exit", self._exit_tray)
            )
            
            self.icon = pystray.Icon("leetcoder", image, "LeetCode Enforcer", menu)
            return True
            
        except ImportError:
            print("❌ pystray or PIL not available for system tray")
            return False
        except Exception as e:
            print(f"❌ Error creating system tray icon: {e}")
            return False
    
    def _mark_completed(self, icon, item):
        """Handle mark completed action."""
        if self.on_mark_completed:
            threading.Thread(target=self.on_mark_completed, daemon=True).start()
        else:
            # Send command to service
            if send_command("mark_completed"):
                if self.icon:
                    self.icon.notify("LeetCode Enforcer", "Mark completed command sent")
            else:
                if self.icon:
                    self.icon.notify("LeetCode Enforcer", "Failed to send command")
    
    def _open_next_problem(self, icon, item):
        """Handle open next problem action."""
        if self.on_open_next_problem:
            # Handle async callback in a separate thread
            def run_async():
                import asyncio
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    if self.on_open_next_problem:  # type: ignore
                        loop.run_until_complete(self.on_open_next_problem())
                    loop.close()
                except Exception as e:
                    print(f"❌ Error in async callback: {e}")
            
            threading.Thread(target=run_async, daemon=True).start()
        else:
            # Send command to service
            if send_command("open_next_problem"):
                if self.icon:
                    self.icon.notify("LeetCode Enforcer", "Open next problem command sent")
            else:
                if self.icon:
                    self.icon.notify("LeetCode Enforcer", "Failed to send command")
    
    def _view_logs(self, icon, item):
        """Handle view logs action."""
        if self.on_view_logs:
            threading.Thread(target=self.on_view_logs, daemon=True).start()
        else:
            # Open the log file directly
            log_path = "C:\\leetcoder_service.log"
            if os.path.exists(log_path):
                try:
                    os.startfile(log_path)
                    if self.icon:
                        self.icon.notify("LeetCode Enforcer", "Log file opened")
                except Exception as e:
                    print(f"❌ Error opening log file: {e}")
                    if self.icon:
                        self.icon.notify("LeetCode Enforcer", "Failed to open log file")
            else:
                print("📊 Log file not found")
                if self.icon:
                    self.icon.notify("LeetCode Enforcer", "Log file not found")
    
    def _exit_tray(self, icon, item):
        """Handle exit action."""
        self.stop()
    
    def start(self) -> bool:
        """Start the system tray icon."""
        if not self._create_icon():
            return False
        
        try:
            self.is_running = True
            if self.icon:  # type: ignore
                self.icon.run()
            return True
        except Exception as e:
            print(f"❌ Error starting system tray: {e}")
            return False
    
    def stop(self):
        """Stop the system tray icon."""
        self.is_running = False
        if self.icon:
            self.icon.stop()
    
    def update_tooltip(self, text: str):
        """Update the tooltip text."""
        if self.icon:
            self.icon.title = text
    
    def show_notification(self, title: str, message: str):
        """Show a notification from the tray icon."""
        if self.icon:
            try:
                self.icon.notify(title, message)
            except Exception as e:
                print(f"❌ Error showing notification: {e}")
    
    def is_available(self) -> bool:
        """Check if system tray is available."""
        try:
            import pystray
            from PIL import Image
            return True
        except ImportError:
            return False

# Example usage
if __name__ == "__main__":
    def mark_completed_callback():
        print("✅ Mark completed callback executed")
    
    def open_next_problem_callback():
        print("🔗 Open next problem callback executed")
    
    def view_logs_callback():
        print("📊 View logs callback executed")
    
    # Create tray UI with callbacks
    tray = TrayUI(
        on_mark_completed=mark_completed_callback,
        on_open_next_problem=open_next_problem_callback,
        on_view_logs=view_logs_callback
    )
    
    if tray.is_available():
        print("🚀 Starting system tray...")
        tray.start()
    else:
        print("❌ System tray not available") 