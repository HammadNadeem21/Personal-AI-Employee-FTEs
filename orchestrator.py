#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orchestrator - Master process for the AI Employee system.

The Orchestrator:
1. Monitors the Needs_Action folder for new items
2. Triggers Qwen Code to process pending tasks
3. Updates the Dashboard with current status
4. Manages the overall workflow

Usage:
    python orchestrator.py /path/to/vault

Or with default path:
    python orchestrator.py  # Uses ./AI_Employee_Vault
"""

import os
import sys
import subprocess
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
import time


class Orchestrator:
    """
    Main orchestrator for the AI Employee system.

    Coordinates between Watchers, Qwen Code, and the Obsidian vault.
    """

    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the Orchestrator.

        Args:
            vault_path: Path to the Obsidian vault root directory
            check_interval: Seconds between checks (default: 60)
        """
        self.vault_path = Path(vault_path).expanduser().resolve()
        self.check_interval = check_interval

        # Core folders
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans = self.vault_path / 'Plans'
        self.done = self.vault_path / 'Done'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.logs = self.vault_path / 'Logs'
        self.dashboard = self.vault_path / 'Dashboard.md'

        # Ensure directories exist
        for folder in [self.needs_action, self.plans, self.done,
                       self.pending_approval, self.approved, self.rejected, self.logs]:
            folder.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self.logger = self._setup_logging()

        # Track processed files
        self.processed_files: set = set()

        # Qwen Code state
        self.qwen_session: Optional[subprocess.Popen] = None
        self.max_iterations = 10  # Max Ralph Wiggum loop iterations

        self.logger.info(f"Orchestrator initialized")
        self.logger.info(f"Vault path: {self.vault_path}")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging to both file and console."""
        logger = logging.getLogger('Orchestrator')
        logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)
        
        # File handler
        log_file = self.logs / f'orchestrator_{datetime.now().strftime("%Y-%m-%d")}.log'
        try:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_format = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_format)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Could not create log file: {e}")
        
        return logger
    
    def count_files(self, folder: Path) -> int:
        """Count .md files in a folder."""
        if not folder.exists():
            return 0
        return len([f for f in folder.iterdir() if f.suffix == '.md' and not f.name.startswith('.')])
    
    def get_pending_items(self) -> List[Path]:
        """Get list of unprocessed files in Needs_Action."""
        if not self.needs_action.exists():
            return []
        
        pending = []
        for f in self.needs_action.iterdir():
            if f.suffix == '.md' and f not in self.processed_files:
                pending.append(f)
        
        return sorted(pending, key=lambda x: x.stat().st_mtime)
    
    def update_dashboard(self):
        """Update the Dashboard.md with current status."""
        try:
            if not self.dashboard.exists():
                self.logger.warning("Dashboard.md not found")
                return
            
            # Count items in each folder
            pending_count = self.count_files(self.needs_action)
            plans_count = self.count_files(self.plans)
            approval_count = self.count_files(self.pending_approval)
            done_today = 0
            
            # Count items moved to Done today
            today = datetime.now().strftime('%Y-%m-%d')
            if self.done.exists():
                for f in self.done.iterdir():
                    if today in f.name:
                        done_today += 1
            
            # Read current dashboard
            content = self.dashboard.read_text()
            
            # Update Quick Stats section
            stats_lines = []
            stats_lines.append("## 📊 Quick Stats")
            stats_lines.append("")
            stats_lines.append("| Metric | Value | Status |")
            stats_lines.append("|--------|-------|--------|")
            
            # Pending tasks status
            pending_status = "✅ Clear" if pending_count == 0 else f"⚠️ {pending_count} item(s)"
            stats_lines.append(f"| Pending Tasks | {pending_count} | {pending_status} |")
            
            # Approval status
            approval_status = "✅ Clear" if approval_count == 0 else f"⏳ {approval_count} awaiting"
            stats_lines.append(f"| Awaiting Approval | {approval_count} | {approval_status} |")
            
            # Tasks completed today
            today_status = f"📈 {done_today} done" if done_today > 0 else "📊 No activity"
            stats_lines.append(f"| Tasks Completed Today | {done_today} | {today_status} |")
            
            stats_lines.append("")
            stats_lines.append("---")
            
            # Replace Quick Stats section in content
            lines = content.split('\n')
            new_lines = []
            in_stats = False
            stats_replaced = False
            
            for line in lines:
                if line.strip() == "## 📊 Quick Stats":
                    in_stats = True
                    continue
                if in_stats and line.strip() == "---" and stats_replaced == False:
                    new_lines.extend(stats_lines)
                    in_stats = False
                    stats_replaced = True
                    continue
                if not in_stats:
                    new_lines.append(line)
            
            if not stats_replaced:
                # Insert stats after first ---
                for i, line in enumerate(new_lines):
                    if line.strip() == "---" and i > 5:
                        new_lines = new_lines[:i+1] + stats_lines + new_lines[i+1:]
                        break
            
            self.dashboard.write_text('\n'.join(new_lines))
            self.logger.debug("Dashboard updated")
            
        except Exception as e:
            self.logger.error(f"Could not update dashboard: {e}")
    
    def trigger_qwen(self, prompt: str) -> bool:
        """
        Trigger Qwen Code to process tasks.

        Args:
            prompt: The prompt/instruction for Qwen

        Returns:
            True if Qwen completed successfully, False otherwise
        """
        try:
            self.logger.info("Triggering Qwen Code...")

            # Change to vault directory
            original_dir = os.getcwd()
            os.chdir(self.vault_path)

            # Build Qwen command
            # Qwen Code uses -p for prompt, doesn't support --append-system-prompt
            # So we prepend the system instructions to the prompt
            # Using -y (YOLO mode) to allow automatic tool execution
            full_prompt = f"""{self._get_system_prompt()}

{prompt}
"""
            qwen_cmd = [
                'qwen',
                '-p', full_prompt,
                '-y'  # YOLO mode: auto-approve tool calls
            ]

            # Run Qwen Code
            result = subprocess.run(
                qwen_cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            os.chdir(original_dir)

            # Log output
            if result.stdout:
                self.logger.info(f"Qwen output: {result.stdout[:500]}...")
            if result.stderr:
                self.logger.warning(f"Qwen errors: {result.stderr[:500]}...")
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            self.logger.error("Qwen Code timed out after 5 minutes")
            return False
        except FileNotFoundError:
            self.logger.error("Qwen Code not found. Is it installed?")
            return False
        except Exception as e:
            self.logger.error(f"Error triggering Qwen: {e}")
            return False

    def _get_system_prompt(self) -> str:
        """Get the system prompt for Qwen Code."""
        return """
You are an AI Employee assistant. Your task is to:

1. Read all files in /Needs_Action folder
2. Process each item according to the Company Handbook rules
3. Create action plans in /Plans folder for multi-step tasks
4. Move completed items to /Done folder
5. Create approval requests in /Pending_Approval for sensitive actions
6. Update Dashboard.md with current status

Always follow the Rules of Engagement in Company_Handbook.md.
Be proactive but cautious. When in doubt, request approval.
"""

    def process_pending_items(self):
        """Process all pending items in Needs_Action."""
        pending = self.get_pending_items()

        if not pending:
            self.logger.debug("No pending items to process")
            return

        self.logger.info(f"Found {len(pending)} pending item(s)")

        # Build prompt for Qwen
        file_list = "\n".join([f"- {f.name}" for f in pending])
        prompt = f"""
I have {len(pending)} new item(s) to process in /Needs_Action:

{file_list}

Please:
1. Read each file carefully
2. Determine the appropriate action based on Company_Handbook.md
3. Create a plan in /Plans if multiple steps are needed
4. Execute simple tasks directly
5. Create approval requests in /Pending_Approval for sensitive actions
6. Move completed items to /Done
7. Update Dashboard.md

Start processing now.
"""

        # Trigger Qwen
        success = self.trigger_qwen(prompt)

        if success:
            # Mark files as processed
            for f in pending:
                self.processed_files.add(f)
            self.logger.info(f"Processed {len(pending)} item(s)")
        else:
            self.logger.warning("Qwen processing failed - items remain pending")
    
    def check_approvals(self):
        """Check for approved items that need action."""
        if not self.approved.exists():
            return
        
        approved_items = [f for f in self.approved.iterdir() if f.suffix == '.md']
        
        for item in approved_items:
            self.logger.info(f"Approved item ready: {item.name}")
            # In Bronze tier, we just log this
            # Higher tiers would trigger MCP actions here
    
    def run(self):
        """Main run loop."""
        self.logger.info("=" * 50)
        self.logger.info("AI Employee Orchestrator Starting")
        self.logger.info("=" * 50)
        
        try:
            while True:
                try:
                    # Update dashboard
                    self.update_dashboard()
                    
                    # Process pending items
                    self.process_pending_items()
                    
                    # Check for approved actions
                    self.check_approvals()
                    
                    # Wait before next cycle
                    time.sleep(self.check_interval)
                    
                except Exception as e:
                    self.logger.error(f"Error in orchestration cycle: {e}", exc_info=True)
                    time.sleep(10)  # Brief pause before retry
                    
        except KeyboardInterrupt:
            self.logger.info("Orchestrator stopped by user")
        except Exception as e:
            self.logger.error(f"Fatal error: {e}", exc_info=True)
            raise
    
    def run_once(self):
        """Run a single orchestration cycle (for testing)."""
        self.update_dashboard()
        self.process_pending_items()
        self.check_approvals()
        self.update_dashboard()


def main():
    """Main entry point."""
    # Parse arguments
    if len(sys.argv) < 2:
        # Try default path
        vault_path = Path(__file__).parent / 'AI_Employee_Vault'
        if not vault_path.exists():
            print("Usage: python orchestrator.py <vault_path>")
            print("\nExample:")
            print("  python orchestrator.py ~/AI_Employee_Vault")
            sys.exit(1)
    else:
        vault_path = Path(sys.argv[1]).expanduser()
    
    # Validate vault path
    if not vault_path.exists():
        print(f"Error: Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    # Check for Qwen Code
    try:
        result = subprocess.run(['qwen', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("Warning: Qwen Code not working. Some features will be limited.")
    except FileNotFoundError:
        print("Warning: Qwen Code not found.")

    # Create and run orchestrator
    orchestrator = Orchestrator(str(vault_path))
    
    # Check for --once flag (for testing)
    if '--once' in sys.argv:
        print("Running single cycle...")
        orchestrator.run_once()
    else:
        orchestrator.run()


if __name__ == "__main__":
    main()
