"""
notifier.py - Sends notifications to the user if behind on goals.
"""

import platform
from typing import Optional
import config

class Notifier:
    """Sends notifications using Windows Toast or plyer fallback."""
    
    def __init__(self):
        self.title = config.NOTIFICATION_TITLE
        self.icon = config.NOTIFICATION_ICON
        self.system = platform.system()
    
    def send_notification(self, message: str, title: Optional[str] = None, 
                         notification_type: str = "info") -> bool:
        """Send a notification to the user."""
        if title is None:
            title = self.title
        
        try:
            if self.system == "Windows":
                return self._send_windows_notification(message, title, notification_type)
            else:
                return self._send_plyer_notification(message, title, notification_type)
        except Exception as e:
            print(f"❌ Error sending notification: {e}")
            return False
    
    def _send_windows_notification(self, message: str, title: str, 
                                  notification_type: str) -> bool:
        """Send Windows Toast notification."""
        try:
            # Try to use winrt for Windows Toast notifications
            import winrt.windows.ui.notifications as notifications
            import winrt.windows.data.xml.dom as dom
            
            # Create toast notification
            toast_xml = f"""
            <toast>
                <visual>
                    <binding template="ToastGeneric">
                        <text>{title}</text>
                        <text>{message}</text>
                    </binding>
                </visual>
            </toast>
            """
            
            # Parse XML
            xml_doc = dom.XmlDocument()
            xml_doc.load_xml(toast_xml)
            
            # Create notification
            toast = notifications.ToastNotification(xml_doc)
            
            # Show notification
            notifier = notifications.ToastNotificationManager.create_toast_notifier("LeetCode Enforcer")
            notifier.show(toast)
            
            print(f"✅ Windows notification sent: {title} - {message}")
            return True
            
        except ImportError:
            # Fall back to plyer if winrt is not available
            print("⚠️ winrt not available, falling back to plyer")
            return self._send_plyer_notification(message, title, notification_type)
        except Exception as e:
            print(f"❌ Windows notification failed: {e}")
            return self._send_plyer_notification(message, title, notification_type)
    
    def _send_plyer_notification(self, message: str, title: str, 
                                notification_type: str) -> bool:
        """Send notification using plyer."""
        try:
            from plyer import notification
            
            notification.notify(
                title=title,
                message=message,
                app_icon=self.icon if self.icon and self.system == "Windows" else None,
                timeout=10
            )
            
            print(f"✅ Plyer notification sent: {title} - {message}")
            return True
            
        except ImportError:
            print("❌ plyer not available for notifications")
            return False
        except Exception as e:
            print(f"❌ Plyer notification failed: {e}")
            return False
    
    def notify_behind_on_goals(self, check_type: str, required: int, actual: int, 
                              solved_problems: Optional[list] = None) -> bool:
        """Send notification when behind on goals."""
        if solved_problems is None:
            solved_problems = []
        
        if check_type == "morning":
            message = f"Morning check: You solved {actual}/{required} problems yesterday. "
            if actual < required:
                message += f"Need to solve {required - actual} more problems today to catch up!"
            else:
                message += "Great job! Keep up the momentum!"
        
        elif check_type == "midday":
            message = f"Midday check: You've solved {actual}/{required} problems today. "
            if actual < required:
                message += f"Need to solve {required - actual} more problems by 6 PM!"
            else:
                message += "On track! Keep going!"
        
        elif check_type == "evening":
            message = f"Evening check: You solved {actual}/{required} problems today. "
            if actual < required:
                message += f"Still need {required - actual} more problems to meet daily goal!"
            else:
                message += "Daily goal achieved! 🎉"
        
        else:
            message = f"Progress check: {actual}/{required} problems solved. "
            if actual < required:
                message += f"Need {required - actual} more to meet target!"
        
        if solved_problems:
            message += f" Recent: {', '.join(solved_problems[-3:])}"
        
        return self.send_notification(message, f"LeetCode {check_type.title()} Check")
    
    def notify_problem_completed(self, problem_title: str) -> bool:
        """Send notification when a problem is completed."""
        message = f"✅ Completed: {problem_title}"
        return self.send_notification(message, "Problem Solved!")
    
    def notify_daily_goal_met(self) -> bool:
        """Send notification when daily goal is met."""
        message = "🎉 Daily goal achieved! Distractions unblocked."
        return self.send_notification(message, "Goal Met!")
    
    def notify_system_blocked(self) -> bool:
        """Send notification when system is blocked."""
        message = "🚫 Distractions blocked. Focus on LeetCode problems!"
        return self.send_notification(message, "Focus Mode Activated")
    
    def notify_system_unblocked(self) -> bool:
        """Send notification when system is unblocked."""
        message = "✅ Distractions unblocked. Great work today!"
        return self.send_notification(message, "Focus Mode Deactivated")
    
    def notify_error(self, error_message: str) -> bool:
        """Send notification for errors."""
        message = f"❌ Error: {error_message}"
        return self.send_notification(message, "System Error", "error")
    
    def notify_reminder(self, hours_remaining: int) -> bool:
        """Send reminder notification."""
        message = f"⏰ {hours_remaining} hours remaining to meet daily goal!"
        return self.send_notification(message, "Daily Goal Reminder")

# Example usage
if __name__ == "__main__":
    notifier = Notifier()
    
    # Test different notification types
    notifier.notify_behind_on_goals("morning", 2, 1, ["two-sum"])
    notifier.notify_problem_completed("Valid Parentheses")
    notifier.notify_daily_goal_met()
    notifier.notify_system_blocked()
    notifier.notify_reminder(3) 