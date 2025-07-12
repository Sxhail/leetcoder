"""
blocker.py - Edits the system hosts file to block or unblock distracting domains.
"""

import os
import shutil
from typing import List
import config

class Blocker:
    """Manages blocking and unblocking of distracting domains."""
    
    def __init__(self):
        self.hosts_file = config.HOSTS_FILE
        self.distracting_domains = config.DISTRACTING_DOMAINS
        self.block_marker = "# LeetCode Enforcer Bot - Blocked Domains"
        self.end_marker = "# End LeetCode Enforcer Bot"
    
    def _backup_hosts_file(self) -> bool:
        """Create a backup of the hosts file."""
        try:
            backup_path = f"{self.hosts_file}.backup"
            shutil.copy2(self.hosts_file, backup_path)
            print(f"✅ Hosts file backed up to {backup_path}")
            return True
        except Exception as e:
            print(f"❌ Error backing up hosts file: {e}")
            return False
    
    def _read_hosts_file(self) -> List[str]:
        """Read the current hosts file content."""
        try:
            with open(self.hosts_file, 'r', encoding='utf-8') as f:
                return f.readlines()
        except Exception as e:
            print(f"❌ Error reading hosts file: {e}")
            return []
    
    def _write_hosts_file(self, lines: List[str]) -> bool:
        """Write content to the hosts file."""
        try:
            with open(self.hosts_file, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            return True
        except Exception as e:
            print(f"❌ Error writing hosts file: {e}")
            return False
    
    def _remove_existing_blocks(self, lines: List[str]) -> List[str]:
        """Remove existing block entries from hosts file."""
        filtered_lines = []
        in_block_section = False
        
        for line in lines:
            if self.block_marker in line:
                in_block_section = True
                continue
            elif self.end_marker in line:
                in_block_section = False
                continue
            elif in_block_section:
                continue
            else:
                filtered_lines.append(line)
        
        return filtered_lines
    
    def _add_block_entries(self, lines: List[str]) -> List[str]:
        """Add block entries to the hosts file."""
        # Remove trailing newlines and add block entries
        while lines and lines[-1].strip() == '':
            lines.pop()
        
        lines.append(f"\n{self.block_marker}\n")
        for domain in self.distracting_domains:
            lines.append(f"127.0.0.1 {domain}\n")
            lines.append(f"127.0.0.1 www.{domain}\n")
        lines.append(f"{self.end_marker}\n")
        
        return lines
    
    def block_distractions(self) -> bool:
        """Block all distracting domains."""
        print("🚫 Blocking distracting domains...")
        
        # Check if we have write permissions
        if not os.access(self.hosts_file, os.W_OK):
            print("❌ No write permission for hosts file. Run as administrator.")
            return False
        
        # Create backup
        if not self._backup_hosts_file():
            return False
        
        # Read current hosts file
        lines = self._read_hosts_file()
        if not lines:
            return False
        
        # Remove existing blocks
        lines = self._remove_existing_blocks(lines)
        
        # Add new block entries
        lines = self._add_block_entries(lines)
        
        # Write back to hosts file
        if self._write_hosts_file(lines):
            print(f"✅ Blocked {len(self.distracting_domains)} distracting domains")
            return True
        else:
            return False
    
    def unblock_distractions(self) -> bool:
        """Unblock all distracting domains."""
        print("✅ Unblocking distracting domains...")
        
        # Check if we have write permissions
        if not os.access(self.hosts_file, os.W_OK):
            print("❌ No write permission for hosts file. Run as administrator.")
            return False
        
        # Read current hosts file
        lines = self._read_hosts_file()
        if not lines:
            return False
        
        # Remove existing blocks
        lines = self._remove_existing_blocks(lines)
        
        # Write back to hosts file
        if self._write_hosts_file(lines):
            print("✅ Unblocked all distracting domains")
            return True
        else:
            return False
    
    def is_blocked(self) -> bool:
        """Check if distractions are currently blocked."""
        lines = self._read_hosts_file()
        return any(self.block_marker in line for line in lines)
    
    def get_blocked_domains(self) -> List[str]:
        """Get list of currently blocked domains."""
        lines = self._read_hosts_file()
        blocked_domains = []
        in_block_section = False
        
        for line in lines:
            if self.block_marker in line:
                in_block_section = True
                continue
            elif self.end_marker in line:
                break
            elif in_block_section and line.strip().startswith('127.0.0.1'):
                domain = line.strip().split()[1]
                if not domain.startswith('www.'):
                    blocked_domains.append(domain)
        
        return blocked_domains
    
    def restore_backup(self) -> bool:
        """Restore hosts file from backup."""
        backup_path = f"{self.hosts_file}.backup"
        if not os.path.exists(backup_path):
            print("❌ No backup file found")
            return False
        
        try:
            shutil.copy2(backup_path, self.hosts_file)
            print("✅ Hosts file restored from backup")
            return True
        except Exception as e:
            print(f"❌ Error restoring backup: {e}")
            return False

# Example usage
if __name__ == "__main__":
    blocker = Blocker()
    
    print("Current status:")
    print(f"Blocked: {blocker.is_blocked()}")
    print(f"Blocked domains: {blocker.get_blocked_domains()}")
    
    # Uncomment to test blocking/unblocking
    # blocker.block_distractions()
    # blocker.unblock_distractions() 