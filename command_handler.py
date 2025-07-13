"""
command_handler.py - Handles inter-process communication between tray UI and service.
"""

import os
import json
import time
import threading
from typing import Optional, Dict, Any

class CommandHandler:
    """Handles communication between tray UI and service."""
    
    def __init__(self, command_file: str = "C:\\leetcoder_commands.json"):
        self.command_file = command_file
        self.last_processed = 0
        self.is_running = False
        self.callbacks: Dict[str, Any] = {}
    
    def register_callback(self, command: str, callback):
        """Register a callback for a specific command."""
        self.callbacks[command] = callback
    
    def send_command(self, command: str, data: Optional[Dict[str, Any]] = None) -> bool:
        """Send a command to the service."""
        try:
            command_data = {
                "command": command,
                "data": data or {},
                "timestamp": time.time(),
                "id": f"{int(time.time() * 1000)}"
            }
            
            # Write command to file
            with open(self.command_file, 'w') as f:
                json.dump(command_data, f)
            
            return True
        except Exception as e:
            print(f"❌ Error sending command: {e}")
            return False
    
    def start_listening(self):
        """Start listening for commands."""
        self.is_running = True
        
        def listener():
            while self.is_running:
                try:
                    if os.path.exists(self.command_file):
                        # Read command file
                        with open(self.command_file, 'r') as f:
                            command_data = json.load(f)
                        
                        # Check if this is a new command
                        if command_data.get("timestamp", 0) > self.last_processed:
                            self._process_command(command_data)
                            self.last_processed = command_data.get("timestamp", 0)
                            
                            # Delete the command file after processing
                            try:
                                os.remove(self.command_file)
                            except:
                                pass
                    
                    time.sleep(1)  # Check every second
                    
                except Exception as e:
                    print(f"❌ Error in command listener: {e}")
                    time.sleep(5)  # Wait longer on error
        
        # Start listener in background thread
        listener_thread = threading.Thread(target=listener, daemon=True)
        listener_thread.start()
    
    def stop_listening(self):
        """Stop listening for commands."""
        self.is_running = False
    
    def _process_command(self, command_data: Dict[str, Any]):
        """Process a received command."""
        command = command_data.get("command")
        data = command_data.get("data", {})
        
        print(f"📡 Processing command: {command}")
        
        if command in self.callbacks:
            try:
                self.callbacks[command](data)
            except Exception as e:
                print(f"❌ Error executing command {command}: {e}")
        else:
            print(f"⚠️ No callback registered for command: {command}")

# Global command handler instance
command_handler = CommandHandler()

def send_command(command: str, data: Optional[Dict[str, Any]] = None) -> bool:
    """Send a command to the service."""
    return command_handler.send_command(command, data)

def register_callback(command: str, callback):
    """Register a callback for a specific command."""
    command_handler.register_callback(command, callback)

def start_listening():
    """Start listening for commands."""
    command_handler.start_listening()

def stop_listening():
    """Stop listening for commands."""
    command_handler.stop_listening() 