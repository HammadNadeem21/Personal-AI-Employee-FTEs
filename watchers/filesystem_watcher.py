#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File System Watcher - Monitors a drop folder for new files.

This is the simplest Watcher implementation, perfect for Bronze tier.
It watches a designated "drop folder" and creates action files when
new files are added.

Usage:
    python filesystem_watcher.py /path/to/vault /path/to/drop_folder

Or with default paths:
    python filesystem_watcher.py  # Uses vault and drop folder from config
"""

import os
import sys
import shutil
import hashlib
import time
from pathlib import Path
from typing import List, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from base_watcher import BaseWatcher


class FileDropHandler(FileSystemEventHandler):
    """Handler for file drop events."""
    
    def __init__(self, watcher: 'FileSystemWatcher'):
        self.watcher = watcher
        self.logger = watcher.logger
    
    def on_created(self, event):
        """Handle file creation events."""
        if event.is_directory:
            return
        
        source_path = Path(event.src_path)
        self.logger.info(f"File detected: {source_path.name}")
        
        # Wait a moment for file to be fully written
        import time
        time.sleep(0.5)
        
        # Process the file
        self.watcher.process_file(source_path)


class FileSystemWatcher(BaseWatcher):
    """
    Watcher that monitors a drop folder for new files.
    
    When a file is added to the drop folder, it:
    1. Copies the file to the vault
    2. Creates a metadata .md file in Needs_Action
    3. Logs the action
    """
    
    def __init__(self, vault_path: str, drop_folder: Optional[str] = None, check_interval: int = 30):
        """
        Initialize the File System Watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root directory
            drop_folder: Path to the folder to monitor (default: vault/Drop)
            check_interval: Seconds between checks (default: 30)
        """
        super().__init__(vault_path, check_interval)
        
        # Setup drop folder
        if drop_folder:
            self.drop_folder = Path(drop_folder).expanduser().resolve()
        else:
            self.drop_folder = self.vault_path / 'Drop'
        
        self.drop_folder.mkdir(parents=True, exist_ok=True)
        
        # Track file hashes to detect duplicates
        self.processed_hashes: set = set()
        
        self.logger.info(f"Drop folder: {self.drop_folder}")
    
    def _calculate_hash(self, filepath: Path) -> str:
        """Calculate MD5 hash of a file."""
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def check_for_updates(self) -> List[Path]:
        """
        Check for new files in the drop folder.
        
        Returns:
            List of Path objects for new files
        """
        new_files = []
        
        if not self.drop_folder.exists():
            return new_files
        
        for filepath in self.drop_folder.iterdir():
            if filepath.is_file() and not filepath.name.startswith('.'):
                # Calculate hash to check if already processed
                try:
                    file_hash = self._calculate_hash(filepath)
                    if file_hash not in self.processed_hashes:
                        new_files.append(filepath)
                        self.processed_hashes.add(file_hash)
                except Exception as e:
                    self.logger.warning(f"Could not hash {filepath}: {e}")
        
        return new_files
    
    def process_file(self, source_path: Path):
        """
        Process a newly detected file.
        
        Args:
            source_path: Path to the source file
        """
        try:
            # Calculate hash
            file_hash = self._calculate_hash(source_path)
            
            # Check if already processed
            if file_hash in self.processed_hashes:
                self.logger.info(f"File already processed: {source_path.name}")
                return
            
            # Create destination path
            dest_path = self.vault_path / 'Files' / source_path.name
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(source_path, dest_path)
            self.logger.info(f"Copied file to: {dest_path}")
            
            # Create action file
            self.create_action_file({
                'source': source_path,
                'destination': dest_path,
                'hash': file_hash
            })
            
            # Remove from drop folder after processing
            source_path.unlink()
            self.logger.info(f"Removed from drop folder: {source_path.name}")
            
        except Exception as e:
            self.logger.error(f"Error processing file {source_path}: {e}")
    
    def create_action_file(self, item: dict) -> Optional[Path]:
        """
        Create a .md action file in the Needs_Action folder.
        
        Args:
            item: Dict with 'source', 'destination', and 'hash' keys
            
        Returns:
            Path to created file, or None if creation failed
        """
        try:
            source_path = item['source']
            dest_path = item['destination']
            file_hash = item['hash']
            
            # Get file metadata
            file_size = dest_path.stat().st_size
            file_ext = source_path.suffix.lower()
            
            # Determine file type category
            type_mapping = {
                '.pdf': 'document',
                '.doc': 'document',
                '.docx': 'document',
                '.txt': 'document',
                '.md': 'document',
                '.xls': 'spreadsheet',
                '.xlsx': 'spreadsheet',
                '.csv': 'spreadsheet',
                '.jpg': 'image',
                '.jpeg': 'image',
                '.png': 'image',
                '.gif': 'image',
                '.zip': 'archive',
                '.rar': 'archive',
            }
            file_type = type_mapping.get(file_ext, 'unknown')
            
            # Create action file content
            timestamp = self.get_timestamp()
            content = f"""---
type: file_drop
source: {source_path.name}
destination: {dest_path}
file_type: {file_type}
size: {file_size}
size_human: {self._format_size(file_size)}
received: {timestamp}
priority: normal
status: pending
hash: {file_hash}
---

# File Drop: {source_path.name}

A new file has been dropped for processing.

## File Details

- **Type**: {file_type}
- **Size**: {self._format_size(file_size)}
- **Received**: {timestamp}
- **Location**: `{dest_path}`

## Suggested Actions

- [ ] Review file content
- [ ] Categorize appropriately
- [ ] Take necessary action
- [ ] Move to archive when complete

## Notes

<!-- Add notes about this file here -->

---
*Created by FileSystemWatcher*
"""
            
            # Create action file
            safe_name = self.sanitize_filename(source_path.stem)
            action_file = self.needs_action / f'FILE_{safe_name}_{timestamp[:10]}.md'
            action_file.write_text(content)
            
            self.processed_hashes.add(file_hash)
            return action_file
            
        except Exception as e:
            self.logger.error(f"Could not create action file: {e}")
            return None
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
    
    def run(self):
        """
        Run the watcher using watchdog for real-time monitoring.
        """
        self.logger.info(f"Starting {self.__class__.__name__}")
        self.logger.info(f"Vault path: {self.vault_path}")
        self.logger.info(f"Drop folder: {self.drop_folder}")
        
        # Setup watchdog observer
        event_handler = FileDropHandler(self)
        observer = Observer()
        observer.schedule(event_handler, str(self.drop_folder), recursive=False)
        observer.start()
        
        self.logger.info("Watchdog observer started - monitoring for file drops")
        
        try:
            while True:
                # Also do periodic checks in case watchdog misses something
                try:
                    items = self.check_for_updates()
                    if items:
                        self.logger.info(f"Periodic check found {len(items)} file(s)")
                        for item in items:
                            self.process_file(item)
                    
                    # Save state
                    self._save_state()
                    
                except Exception as e:
                    self.logger.error(f"Error in periodic check: {e}")
                
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info("Watcher stopped by user")
            observer.stop()
            self._save_state()
        except Exception as e:
            self.logger.error(f"Fatal error: {e}", exc_info=True)
            observer.stop()
            self._save_state()
            raise
        finally:
            observer.join()


if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python filesystem_watcher.py <vault_path> [drop_folder]")
        print("\nExample:")
        print("  python filesystem_watcher.py ~/AI_Employee_Vault")
        print("  python filesystem_watcher.py ~/AI_Employee_Vault ~/Drop_Folder")
        sys.exit(1)
    
    vault_path = Path(sys.argv[1]).expanduser()
    drop_folder = Path(sys.argv[2]).expanduser() if len(sys.argv) > 2 else None
    
    # Validate vault path
    if not vault_path.exists():
        print(f"Error: Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    # Create and run watcher
    watcher = FileSystemWatcher(str(vault_path), str(drop_folder) if drop_folder else None)
    watcher.run()
