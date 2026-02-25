# Personal AI Employee FTEs - Project Context

## Project Overview

This is a **documentation and knowledge base project** for building **Personal AI Employees** (Digital FTEs - Full-Time Equivalents). It serves as an architectural blueprint and hackathon guide for creating autonomous AI agents that manage personal and business affairs 24/7.

### Core Concept

The project enables building a "Digital FTE" using:
- **Claude Code** as the reasoning engine and executor
- **Obsidian** (local Markdown) as the dashboard and long-term memory
- **Python Sentinel Scripts** ("Watchers") for monitoring Gmail, WhatsApp, filesystems
- **MCP (Model Context Protocol) Servers** for external actions (email, browser automation, payments)

### Key Architecture: Perception → Reasoning → Action

| Layer | Component | Purpose |
|-------|-----------|---------|
| **Perception** | Gmail/WhatsApp/File Watchers | Monitor inputs, create `.md` files in `/Needs_Action` |
| **Reasoning** | Claude Code | Read tasks, create plans, decide actions |
| **Action** | MCP Servers | Send emails, automate browser, process payments |
| **Persistence** | Ralph Wiggum Loop | Keep Claude working until task completion |

## Directory Structure

```
Personal-AI-Employee-FTEs/
├── Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md  # Main documentation (1201 lines)
├── skills-lock.json          # Skill version tracking
├── .gitignore                # Python/Node.js/IDE exclusions
├── QWEN.md                   # This file
└── .qwen/
    └── skills/
        └── browsing-with-playwright/   # Browser automation skill
            ├── SKILL.md                # Skill documentation
            ├── scripts/
            │   ├── mcp-client.py       # Universal MCP client (HTTP + stdio)
            │   ├── start-server.sh     # Start Playwright MCP server
            │   ├── stop-server.sh      # Stop Playwright MCP server
            │   └── verify.py           # Server health check
            └── references/
                └── playwright-tools.md # Complete MCP tool reference (22 tools)
```

## Key Files

| File | Purpose |
|------|---------|
| `Personal AI Employee Hackathon 0_...md` | Comprehensive hackathon guide with architecture, templates, code examples |
| `.qwen/skills/browsing-with-playwright/SKILL.md` | Browser automation setup and usage guide |
| `.qwen/skills/browsing-with-playwright/scripts/mcp-client.py` | Universal MCP client supporting HTTP and stdio transports |
| `.qwen/skills/browsing-with-playwright/references/playwright-tools.md` | Complete reference for 22 Playwright MCP tools |

## Usage

### For Hackathon Participants

1. **Read the main hackathon document** for architecture and implementation guidance
2. **Set up prerequisites**: Claude Code, Obsidian, Python 3.13+, Node.js 24+, GitHub Desktop
3. **Choose your tier**: Bronze (8-12h), Silver (20-30h), Gold (40+h), Platinum (60+h)
4. **Use the browsing-with-playwright skill** for web automation tasks

### Playwright MCP Server Commands

```bash
# Start server (shared browser context for stateful sessions)
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh

# Verify server is running
python3 .qwen/skills/browsing-with-playwright/scripts/verify.py

# Stop server (closes browser first)
bash .qwen/skills/browsing-with-playwright/scripts/stop-server.sh

# Call tools via mcp-client.py
python3 .qwen/skills/browsing-with-playwright/scripts/mcp-client.py call \
  -u http://localhost:8808 -t browser_navigate -p '{"url": "https://example.com"}'
```

### MCP Client Usage

```bash
# List tools from HTTP server
python3 scripts/mcp-client.py list --url http://localhost:8808

# List tools from stdio server
python3 scripts/mcp-client.py list --stdio "npx -y @modelcontextprotocol/server-github"

# Call a tool
python3 scripts/mcp-client.py call --url http://localhost:8808 \
  --tool browser_click --params '{"element": "Submit", "ref": "e42"}'

# Emit tool schemas as markdown
python3 scripts/mcp-client.py emit --url http://localhost:8808
```

## Development Conventions

- **Local-first**: All data stored in local Obsidian vault (Markdown files)
- **Human-in-the-loop**: Sensitive actions require approval via file movement (`/Pending_Approval` → `/Approved`)
- **Claim-by-move rule**: First agent to move task to `/In_Progress/<agent>/` owns it
- **Secrets isolation**: `.env`, tokens, WhatsApp sessions never sync via vault

## Hackathon Tiers

| Tier | Requirements | Time |
|------|-------------|------|
| **Bronze** | Obsidian dashboard, 1 Watcher, Claude reading/writing | 8-12h |
| **Silver** | 2+ Watchers, MCP server, HITL approval, scheduling | 20-30h |
| **Gold** | Full integration, Odoo accounting, Ralph Wiggum loop, audit logging | 40+h |
| **Platinum** | Cloud deployment, Work-Zone specialization, Odoo on VM | 60+h |

## Important Patterns

### Ralph Wiggum Loop (Persistence)
A Stop hook pattern that intercepts Claude's exit and re-injects prompts until tasks are complete:
1. Orchestrator creates state file with prompt
2. Claude works on task
3. Claude tries to exit
4. Stop hook checks: Is task file in `/Done`?
5. If NO → Block exit, re-inject prompt (loop continues)

### Watcher Pattern
All Watchers follow a base class structure:
```python
class BaseWatcher(ABC):
    def check_for_updates(self) -> list:  # Return new items to process
    def create_action_file(self, item) -> Path:  # Create .md in Needs_Action
    def run(self):  # Infinite loop with check_interval
```

### Human-in-the-Loop Approval
For sensitive actions, Claude writes an approval request file instead of acting directly:
- File: `/Vault/Pending_Approval/<ACTION>_<ID>.md`
- Approval: Move to `/Approved`
- Rejection: Move to `/Rejected`

## Resources

- **Wednesday Research Meetings**: Wed 10:00 PM PKT on Zoom (see hackathon doc for link)
- **Ralph Wiggum Reference**: https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum
- **Agent Skills**: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- **MCP Servers**: https://github.com/AlanOgic/mcp-odoo-adv (Odoo integration example)
