# Personal AI Employee - Bronze Tier

> **Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.**

A minimum viable implementation of an autonomous AI Employee that monitors your files, processes tasks, and maintains a real-time dashboard using Qwen Code and Obsidian.

---

## 📋 Overview

This Bronze Tier implementation provides the foundation for a Personal AI Employee (Digital FTE - Full-Time Equivalent). It includes:

- **Obsidian Vault** with Dashboard, Company Handbook, and Business Goals
- **File System Watcher** that monitors a drop folder for new files
- **Orchestrator** that triggers Qwen Code to process pending tasks
- **Human-in-the-Loop** approval workflow via file movement

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PERSONAL AI EMPLOYEE                         │
│                       (Bronze Tier)                             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐     ┌─────────────────────────────────────────┐
│   Drop Folder   │────▶│         File System Watcher             │
│  (Files to      │     │  (Monitors for new files)               │
│   process)      │     └─────────────────────────────────────────┘
└─────────────────┘                  │
                                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OBSIDIAN VAULT                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Needs_Action │  │    Plans     │  │    Done      │          │
│  │   (Inbox)    │  │  (Multi-step)│  │  (Archive)   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │Pending_Appro.│  │   Approved   │  │   Dashboard  │          │
│  │ (HITL)       │  │  (Ready)     │  │   (Status)   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │      QWEN CODE          │
                    │   (Reasoning Engine)    │
                    └─────────────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │    ORCHESTRATOR         │
                    │   (Workflow Manager)    │
                    └─────────────────────────┘
```

---

## 📁 Folder Structure

```
Personal-AI-Employee-FTEs/
├── AI_Employee_Vault/           # Obsidian vault
│   ├── Dashboard.md             # Real-time status dashboard
│   ├── Company_Handbook.md      # Rules of Engagement
│   ├── Business_Goals.md        # Objectives and metrics
│   ├── Inbox/                   # Raw incoming items
│   ├── Needs_Action/            # Items requiring processing
│   ├── Plans/                   # Multi-step task plans
│   ├── Done/                    # Completed items archive
│   ├── Pending_Approval/        # Awaiting human decision
│   ├── Approved/                # Approved actions ready
│   ├── Rejected/                # Declined actions
│   ├── Logs/                    # System audit logs
│   ├── Accounting/              # Financial records
│   ├── Briefings/               # CEO briefings
│   └── Files/                   # Processed file attachments
│
├── watchers/
│   ├── base_watcher.py          # Abstract base class
│   ├── filesystem_watcher.py    # File drop watcher
│   └── requirements.txt         # Python dependencies
│
├── orchestrator.py              # Main orchestration script
├── README.md                    # This file
└── QWEN.md                      # Project context
```

---

## 🚀 Quick Start

### Prerequisites

| Software | Version | Purpose |
|----------|---------|---------|
| [Qwen Code](https://github.com/QwenLM/Qwen) | Latest | Reasoning engine |
| [Python](https://www.python.org/downloads/) | 3.13+ | Watcher scripts |
| [Node.js](https://nodejs.org/) | 24+ LTS | MCP servers (future) |
| [Obsidian](https://obsidian.md/download) | v1.10.6+ | Dashboard/Knowledge base |

### Installation

1. **Clone or navigate to the project:**
   ```bash
   cd /path/to/Personal-AI-Employee-FTEs
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r watchers/requirements.txt
   ```

3. **Verify Qwen Code installation:**
   ```bash
   qwen --version
   ```

4. **Open the Obsidian vault:**
   - Launch Obsidian
   - Click "Open folder as vault"
   - Select `AI_Employee_Vault` folder

---

## 📖 Usage

### Starting the File System Watcher

The File System Watcher monitors a "drop folder" for new files:

```bash
# Start watcher (uses default vault path)
python watchers/filesystem_watcher.py AI_Employee_Vault

# Or specify custom drop folder
python watchers/filesystem_watcher.py AI_Employee_Vault ~/Drop_Folder
```

**How it works:**
1. Drop a file into the `AI_Employee_Vault/Drop/` folder (or your custom folder)
2. Watcher detects the file
3. Creates a metadata `.md` file in `Needs_Action/`
4. Moves original file to `Files/` archive

### Starting the Orchestrator

The Orchestrator triggers Qwen Code to process pending items:

```bash
# Start orchestrator (continuous mode)
python orchestrator.py AI_Employee_Vault

# Run single cycle (for testing)
python orchestrator.py AI_Employee_Vault --once
```

### Running Both Together

For full automation, run both in separate terminals:

```bash
# Terminal 1: File Watcher
python watchers/filesystem_watcher.py AI_Employee_Vault

# Terminal 2: Orchestrator
python orchestrator.py AI_Employee_Vault
```

---

## 🔄 Workflow Example

### Processing a Dropped File

1. **Drop a file** into `AI_Employee_Vault/Drop/document.pdf`

2. **Watcher creates action file:**
   ```
   Needs_Action/FILE_document_2026-02-26.md
   ```

3. **Orchestrator triggers Qwen:**
   - Qwen reads the action file
   - Determines appropriate action based on `Company_Handbook.md`
   - Creates a plan or executes directly

4. **Qwen's output:**
   - Creates `Plans/PLAN_review_document.md` if multi-step
   - Or moves to `Done/` if simple
   - Updates `Dashboard.md`

5. **You review** the Dashboard to see what happened

---

## 🎯 Bronze Tier Deliverables

This implementation satisfies all Bronze Tier requirements:

| Requirement | Status | Location |
|-------------|--------|----------|
| Obsidian vault | ✅ | `AI_Employee_Vault/` |
| Dashboard.md | ✅ | `AI_Employee_Vault/Dashboard.md` |
| Company_Handbook.md | ✅ | `AI_Employee_Vault/Company_Handbook.md` |
| One working Watcher | ✅ | `watchers/filesystem_watcher.py` |
| Qwen Code integration | ✅ | `orchestrator.py` |
| Basic folder structure | ✅ | All folders created |

---

## ⚙️ Configuration

### Environment Variables (Optional)

Create a `.env` file for configuration:

```bash
# .env (add to .gitignore!)
VAULT_PATH=~/AI_Employee_Vault
DROP_FOLDER=~/Drop
CHECK_INTERVAL=60
DRY_RUN=true
```

### Watcher Configuration

Edit `filesystem_watcher.py` to customize:

```python
# Check interval (seconds)
watcher = FileSystemWatcher(vault_path, check_interval=30)

# Drop folder location
drop_folder = vault_path / 'Drop'  # Default
```

### Orchestrator Configuration

Edit `orchestrator.py` to customize:

```python
# Claude timeout (seconds)
timeout=300  # 5 minutes

# Max iterations
max_iterations=10
```

---

## 📊 Dashboard

The Dashboard provides real-time visibility:

| Section | Description |
|---------|-------------|
| Quick Stats | Pending tasks, approvals, completions |
| Needs Action | Current items requiring attention |
| Active Plans | Multi-step tasks in progress |
| Pending Approval | Items awaiting your decision |
| Recent Activity | Completed items log |
| System Status | Watcher/orchestrator health |

---

## 🔐 Security

### Best Practices

1. **Never commit credentials** - Add `.env` to `.gitignore`
2. **Use environment variables** for API keys
3. **Review approval items** before moving to `/Approved`
4. **Check logs regularly** in `/Logs`

### Human-in-the-Loop

For sensitive actions, Claude creates an approval request:

```markdown
---
type: approval_request
action: file_review
priority: normal
---

# Review Required

This file needs your approval before proceeding.

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder.
```

---

## 🐛 Troubleshooting

### Qwen Code not found

```bash
# Install Qwen Code
# Follow installation instructions at: https://github.com/QwenLM/Qwen

# Verify installation
qwen --version
```

### Watcher not detecting files

1. Check the drop folder path is correct
2. Ensure file isn't hidden (no `.` prefix)
3. Check logs: `AI_Employee_Vault/Logs/watcher_*.log`

### Orchestrator not processing

1. Verify Qwen Code is installed
2. Check logs: `AI_Employee_Vault/Logs/orchestrator_*.log`
3. Run with `--once` flag to test single cycle

### Permission errors

```bash
# Ensure proper permissions
chmod +x watchers/*.py
chmod +x orchestrator.py
```

---

## 📈 Next Steps (Silver Tier)

After mastering Bronze, consider adding:

1. **Gmail Watcher** - Monitor email for action items
2. **MCP Server** - Enable external actions (send emails)
3. **Approval Workflow** - Full HITL for sensitive actions
4. **Scheduled Tasks** - Cron-based daily briefings
5. **Plan.md Creation** - Claude creates multi-step plans

---

## 📚 Resources

- [Hackathon Document](./Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md) - Full architectural blueprint
- [QWEN.md](./QWEN.md) - Project context and conventions
- [Company Handbook](./AI_Employee_Vault/Company_Handbook.md) - Rules of Engagement
- [Qwen Code Docs](https://github.com/QwenLM/Qwen) - Qwen Code documentation
- [Obsidian Help](https://help.obsidian.md) - Obsidian documentation

---

## 🤝 Contributing

This is a hackathon project. Feel free to:

1. Fork and customize for your needs
2. Add new Watcher implementations
3. Improve the orchestration logic
4. Share your enhancements

---

*Built for the Personal AI Employee Hackathon 0 - Building Autonomous FTEs in 2026*
