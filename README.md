# ⚡ TerminalPulse

> **Short-term memory for AI agents. Captures your coding context in real time — silently.**

TerminalPulse runs in the background and watches your terminal, editor, and filesystem. When something breaks, type `pulse fix` — no copy-pasting, no explaining. **It already knows what happened.**

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![PyPI](https://img.shields.io/pypi/v/terminalpulse?style=flat-square&logo=pypi)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-WSL%20%7C%20Linux-orange?style=flat-square)
![Downloads](https://img.shields.io/pypi/dm/terminalpulse?style=flat-square)

---

## 📋 Table of Contents

- [The Problem](#-the-problem-every-developer-knows)
- [The Solution](#-the-solution)
- [How It Works](#-how-it-works)
- [Installation](#-installation)
- [Setup](#-setup-one-time)
- [Commands](#-commands)
- [Real World Scenarios](#-real-world-scenarios)
- [Auto-Suggest on Error](#-auto-suggest-on-error)
- [MCP Integration](#-mcp-integration-claude-desktop--cursor)
- [Language & Project Support](#-language--project-support)
- [The Difference](#-the-difference)
- [Security & Privacy](#-security--privacy)
- [Requirements](#-requirements)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🔥 The Problem Every Developer Knows

You're deep in a feature. Your build breaks. Now you have to:

1. Read the traceback
2. Copy the error
3. Switch to Claude / ChatGPT / Cursor
4. Explain your project, your git branch, which file you were editing
5. Paste the file contents
6. Wait for the answer
7. Switch back to terminal
8. Apply the fix manually

**That's 2 minutes of context-switching friction. Every. Single. Time.**

The worst part? The AI doesn't know anything about what you were doing. You have to re-explain everything from scratch.

---

## ✅ The Solution

```bash
# Your Next.js build breaks at 2am
npm run build
# TypeError: Cannot read properties of undefined (reading 'userId')
# ⚡ Error detected. Run 'pulse fix' to auto-fix.

pulse fix
# TerminalMind already knows:
# → Project: Next.js + TypeScript
# → Branch: feature/auth
# → Last commit: "add JWT middleware"
# → Active file: src/middleware/auth.ts
# → Full build error output
# → Actual file contents
# → Precise fix in seconds
```

No switching tabs. No explaining. No copy-pasting.

---

## 🏗️ How It Works

Three silent streams feed a time-decaying knowledge graph:

| Stream | Source | What It Captures |
|---|---|---|
| **Focus** | VS Code window title | Which file is active in your editor |
| **Activity** | Filesystem watchdog | Which files were just saved |
| **Distress** | Bash hook | Which terminal commands just failed |

Every event gets a heat score that decays over time:

```
heat = e^(-λ × seconds_since_event) × severity
```

Older events fade automatically. The AI always gets what's relevant **right now** — not noise from this morning's work.

### Data Flow

```
VS Code (Windows) → HTTP:7077  ─┐
Terminal errors   → Unix socket ─┼→ pulsed daemon → ~/.devpulse_state.json
File saves        → watchdog   ─┘                         ↓
                                          pulse fix → TerminalMind → Fix
```

### Technology Stack

| Layer | Technology | Role |
|---|---|---|
| **Daemon** | Python asyncio | Long-lived background process |
| **Graph** | NetworkX + Pydantic | Time-decaying knowledge graph |
| **CLI** | Typer + Rich | Commands and formatted output |
| **AI Bridge** | TerminalMind | Auto-fix powered by live context |

---

## 🚀 Installation

```bash
pip install terminalpulse
pip install terminalmind
tmind auth
```

---

## ⚙️ Setup (One Time)

```bash
# Install system dependencies
pulse install-deps

# Inject shell hook
pulse init
source ~/.bashrc

# Start watching your project
cd your-project
pulse watch
```

That's it. TerminalPulse runs silently in the background from now on.

---

## 🛠️ Commands

| Command | What It Does |
|---|---|
| `pulse watch` | Auto-detect project type and start daemon |
| `pulse fix` | Send full context to AI — no input needed |
| `pulse context` | Copy formatted context block for any AI |
| `pulse insights` | Detect recurring failure patterns |
| `pulse report` | End of day coding summary |
| `pulse history` | 30-minute activity timeline |
| `pulse state` | Show raw JSON context |
| `pulse init` | Inject shell hook into `.bashrc` |
| `pulse install-deps` | Install system dependencies |
| `pulse mcp` | Start MCP server for Claude Desktop / Cursor |
| `pulse_run <cmd>` | Capture full stderr for large builds |

---

## 🧑‍💻 Real World Scenarios

### Scenario 1 — Full-Stack Developer (Next.js + TypeScript)

```bash
cd ~/my-saas
pulse watch
# Project detected: Next.js + TypeScript
# Watching: /home/user/my-saas

# Later — build breaks
npm run build
# Module not found: Can't resolve '@/components/AuthGuard'
# ⚡ Error detected. Run 'pulse fix' to auto-fix.

pulse fix
# Sends to TerminalMind:
# → Project: Next.js + TypeScript
# → Branch: feature/dashboard
# → Changed files: components/AuthGuard.tsx, pages/dashboard.tsx
# → Full webpack error
# → File contents of dashboard.tsx
# → Precise fix instantly
```

---

### Scenario 2 — Backend Developer (Python / FastAPI)

```bash
cd ~/api-server
pulse watch
# Project detected: Python

# Server crashes
python3 main.py
# sqlalchemy.exc.OperationalError: no such table: users
# ⚡ Error detected. Run 'pulse fix' to auto-fix.

pulse fix
# AI knows you just edited models.py and ran a migration
# Gives exact Alembic fix, not a generic answer
```

---

### Scenario 3 — You Use Claude, Not TerminalMind

```bash
pulse context
# Copies to clipboard:
# === TerminalPulse Context ===
# Project:      React + TypeScript
# Branch:       fix/payment-flow
# Active file:  src/checkout/PaymentForm.tsx
# Last error:   npm run build (exit 1)
# Changed files: PaymentForm.tsx, useStripe.ts
# File contents: [actual code]
# =============================

# Paste into Claude — full context in one paste
```

---

### Scenario 4 — Recurring Bug Pattern

```bash
# After hitting the same error 4 times today
pulse insights

# ⚡ TerminalPulse Insights
# Project: Python | Branch: feature/auth
#
# Recurring failure: python3 server.py failed 4 times
# → All failures occurred after editing config.py
# → Suggestion: run pulse fix to investigate root cause
# High error rate: 80%
# → Consider adding input validation to config.py
```

---

### Scenario 5 — End of Day Standup

```bash
pulse report

# 📊 TerminalPulse Daily Report
# Branch: feature/payment-integration
#
# • Files saved:      23
# • Errors hit:        6
# • Focus changes:    14
#
# Most edited file:   PaymentForm.tsx (6 saves)
# Most common error:  npm run build (4x)
#
# Rough session — 6 errors. Run pulse insights for patterns.
```

---

## ⚡ Auto-Suggest on Error

Every time a command fails, TerminalPulse prints:

```
⚡ Error detected. Run 'pulse fix' to auto-fix.
```

You never have to remember to use it.

---

## 🔌 MCP Integration (Claude Desktop / Cursor)

```bash
pulse mcp
```

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "terminalpulse": {
      "command": "pulse",
      "args": ["mcp"]
    }
  }
}
```

Claude Desktop now has live access to your coding context. Ask it:
- *"What was I working on?"*
- *"What errors did I hit today?"*
- *"Which file is causing the most problems?"*

Available tools:

| Tool | Returns |
|---|---|
| `get_pulse_state` | Full current coding context |
| `get_hottest_error` | Most recent error with full stderr |
| `get_active_context` | Active file, language, git branch |
| `get_history` | Last 30 minutes timeline |

---

## 🌍 Language & Project Support

| Stack | Detection | Error Capture | Fix |
|---|---|---|---|
| Python / FastAPI / Django | ✓ | ✓ | ✓ |
| React / Next.js | ✓ | ✓ | ✓ |
| TypeScript / Node.js | ✓ | ✓ | ✓ |
| Rust | ✓ | ✓ | ✓ |
| Go | ✓ | ✓ | ✓ |
| Java / Spring | ✓ | ✓ | ✓ |
| Large builds (webpack, gradle, pytest) | ✓ via `pulse_run` | ✓ | ✓ |

---

## 📊 The Difference

| Without TerminalPulse | With TerminalPulse |
|---|---|
| Copy error manually | Auto-captured |
| Switch to AI chat | Already connected |
| Explain your project | Auto-detected |
| Explain git branch | Auto-detected |
| Paste file contents | Auto-read |
| Wait for response | Instant |
| Apply fix manually | One keypress |
| **~2 minutes every time** | **~5 seconds** |

---

## 🛡️ Security & Privacy

- **Local first** — your context graph lives entirely on your machine
- **No telemetry** — nothing is sent anywhere without your command
- **Targeted context** — only the specific error and active file go to the AI
- **Secure keys** — API keys stored in OS keyring, never in plain files

---

## 📋 Requirements

- Python 3.10+
- WSL Ubuntu (Linux daemon)
- `netcat` — pre-installed on Ubuntu
- `terminalmind` — for `pulse fix`
- Windows 11 + VS Code — for focus tracking (optional)

---

## 🤝 Contributing

1. Fork the repository
2. Create your branch: `git checkout -b feature/your-feature`
3. Commit: `git commit -m 'Add your feature'`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

MIT © 2026 Prajwal Hulle — See **[LICENSE](https://github.com/prajwal-2509/terminalpulse/blob/main/LICENSE)** for full details.

---

<p align="center">
  Built for developers who are tired of copy-pasting errors into AI.
  <br/><br/>
  <a href="https://pypi.org/project/terminalpulse">PyPI</a> •
  <a href="https://github.com/prajwal-2509/terminalpulse">GitHub</a> •
  <a href="https://github.com/prajwal-2509/terminalpulse/issues">Issues</a>
</p>
