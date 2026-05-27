# ⚡ TerminalPulse

> **Short-term memory for AI agents. Captures your coding context in real time — silently.**

TerminalPulse runs in the background and watches your terminal, editor, and filesystem. When something goes wrong, type `pulse fix` — no copy-pasting, no explaining. **It already knows what happened.**

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![PyPI](https://img.shields.io/pypi/v/terminalpulse?style=flat-square&logo=pypi)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-WSL%20%7C%20Linux-orange?style=flat-square)
![Downloads](https://img.shields.io/pypi/dm/terminalpulse?style=flat-square)

---

## 📋 Table of Contents

- [The Problem](#-the-problem)
- [The Solution](#-the-solution)
- [How It Works](#-how-it-works)
- [Installation](#-installation)
- [Setup](#-setup-one-time)
- [Commands](#-commands)
- [Auto-Suggest on Error](#-auto-suggest-on-error)
- [pulse context — Works With Any AI](#-pulse-context--works-with-any-ai)
- [pulse report — Daily Summary](#-pulse-report--daily-summary)
- [pulse insights — Pattern Detection](#-pulse-insights--pattern-detection)
- [Real World Usage](#-real-world-usage)
- [MCP Integration](#-mcp-integration)
- [Test Results](#-test-results)
- [Language Support](#-language-support)
- [API Key Setup](#-api-key-setup-all-platforms)
- [Security & Privacy](#-security--privacy)
- [Requirements](#-requirements)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🔥 The Problem

Every AI tool today requires you to:

1. Notice the error
2. Copy the traceback
3. Switch to AI chat
4. Paste and explain context
5. Wait for answer
6. Switch back to terminal

**That's 30 seconds of friction, every single time.**

---

## ✅ The Solution

```bash
# Something breaks
python3 app.py
# KeyError: 'user_id'

# One command — no copy-pasting
pulse fix

# TerminalMind already knows:
# → what command failed
# → the full error output
# → which file you were editing
# → your git branch
# → the actual file contents
# → precise fix in seconds
```

---

## 🏗️ How It Works

Three silent streams feed a time-decaying knowledge graph:

| Stream | Source | What It Captures |
|---|---|---|
| **Focus** | VS Code window title (Windows) | Which file is active in your editor |
| **Activity** | Filesystem watchdog (WSL) | Which files were just saved |
| **Distress** | Bash hook (WSL) | Which terminal commands just failed |

Every event gets a **heat score** that decays over time:

```
heat = e^(-λ × seconds_since_event) × severity
```

Older events fade automatically — the AI always gets current context, not noise from this morning.

### Data Flow

```
VS Code (Windows) → HTTP:7077  ─┐
Terminal errors   → Unix socket ─┼→ pulsed daemon → ~/.devpulse_state.json
File saves        → watchdog   ─┘                         ↓
                                              pulse fix → TerminalMind → Auto-fix
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

Install TerminalPulse from PyPI:

```bash
pip install terminalpulse
```

Also install TerminalMind to enable the `pulse fix` command:

```bash
pip install terminalmind
tmind auth
```

---

## ⚙️ Setup (One Time)

### Step 1 — Inject the shell hook

```bash
pulse init
source ~/.bashrc
```

### Step 2 — Start watching your project

```bash
cd your-project
pulse watch
```

### Step 3 — Windows focus tracking (optional)

For VS Code file detection, open **Windows PowerShell** and run:

```powershell
python \\wsl.localhost\Ubuntu-22.04\home\username\terminalpulse\terminalpulse\windows_tracker.py
```

Or get exact instructions with:

```bash
pulse init-windows
```

---

## 🛠️ Commands

| Command | What It Does |
|---|---|
| `pulse watch` | Auto-detect project type and start daemon |
| `pulse start --watch .` | Start daemon manually |
| `pulse fix` | Send hottest error + full context to AI |
| `pulse context` | Generate formatted context block for any AI |
| `pulse state` | Show current context as JSON |
| `pulse history` | Show 30-minute activity timeline |
| `pulse report` | Daily summary of errors, saves, and focus |
| `pulse insights` | Pattern detection across your session |
| `pulse init` | Inject shell hook into `.bashrc` |
| `pulse init-windows` | Windows setup instructions |
| `pulse install-deps` | Install all system dependencies |
| `pulse mcp` | Start MCP server for Claude Desktop / Cursor |
| `pulse_run <cmd>` | Run command with full stderr capture |

---

## ⚡ Auto-Suggest on Error

After every failed command, TerminalPulse automatically prints:

```
⚡ Error detected. Run 'pulse fix' to auto-fix.
```

Zero friction — you see it immediately after the error.

---

## 📋 `pulse context` — Works With Any AI

Don't use TerminalMind? No problem. `pulse context` generates a formatted block you paste into **any AI**:

```bash
pulse context
```

Output:

```
=== TerminalPulse Context ===
Project:      React + TypeScript
Language:     typescript
Active file:  src/middleware/auth.ts
Git branch:   feature/auth
Last commit:  add JWT middleware

Changed files:
  src/middleware/auth.ts
  src/api/login.ts

Last error:
  Command:   npm run build
  Exit code: 1
  Output:    TypeError: Cannot read property 'userId'

File contents (auth.ts):
  [your actual code here]
```

Paste this into Claude, ChatGPT, Cursor, or any AI. No explaining needed.

---

## 📊 `pulse report` — Daily Summary

```bash
pulse report
```

Output:

```
📊 TerminalPulse Daily Report
Branch: feature/auth

• Files saved:    12
• Errors hit:      5
• Focus changes:   8

Most edited file:  auth.ts (4 saves)
Most focused file: login.ts
Most common error: npm run build (3x)

Rough session — 5 errors. Run pulse insights for patterns.
```

---

## 🔍 `pulse insights` — Pattern Detection

```bash
pulse insights
```

Output:

```
⚡ TerminalPulse Insights
Project: React + TypeScript | Branch: feature/auth

Session activity:
  • 12 file saves recorded
  • 5 errors detected
  • 20 total events

Most active file:   auth.ts (4 saves)
Recurring failure:  npm run build failed 3 times
  → Suggestion: run pulse fix to investigate root cause
High error rate:    41%
  → Consider running tests more frequently
```

---

## 🛠️ First Time Setup

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

---

### `pulse fix` — the star of the show

```bash
pulse fix
```

No input needed. It already knows what broke, which file is open, and what you were running. Sends the full context snapshot to TerminalMind and returns a precise, targeted fix.

---

### `pulse_run` — for large projects

Use this prefix for large build commands to capture full stderr:

```bash
pulse_run npm run build
pulse_run ./gradlew build
pulse_run pytest

# Then fix whatever broke:
pulse fix
```

---

### `pulse state` — see what the AI sees

```bash
pulse state
```

Example output:

```json
{
  "hottest": [
    {
      "heat": 1.0,
      "type": "command_failed",
      "cmd": "python3 app.py",
      "exit_code": 1,
      "stderr_tail": "KeyError: 'user_id'"
    },
    {
      "heat": 0.3,
      "type": "focus_changed",
      "path": "app.py"
    }
  ]
}
```

---

## 🧑‍💻 Real World Usage

### Scenario: Building a Repo Intelligence Tool

You're developing a Python tool that analyzes public GitHub repos. Here's how TerminalPulse fits into your workflow:

**Install once:**
```bash
pip install terminalpulse terminalmind
tmind auth
pulse install-deps
pulse init
source ~/.bashrc
```

**Every coding session:**
```bash
cd your-project
pulse watch
```

**When you hit an error:**
```bash
# Error appears in terminal automatically:
# ⚡ Error detected. Run 'pulse fix' to auto-fix.

pulse fix        # auto-fix with TerminalMind
# OR
pulse context    # copy context for Claude / ChatGPT / Cursor
```

**Understand your session:**
```bash
pulse insights   # detect recurring patterns
pulse report     # end of day summary
pulse history    # 30-minute timeline
```

**Connect to Claude Desktop:**
```bash
pulse mcp        # start MCP server
# add to claude_desktop_config.json and Claude knows your context
```

### The Difference

| Without TerminalPulse | With TerminalPulse |
|---|---|
| Error appears | Error appears |
| You read the traceback | Auto-suggest appears |
| You copy the error | You type `pulse fix` |
| You switch to AI chat | AI already has full context |
| You explain your project | Fix appears in seconds |
| You explain your git branch | |
| You paste file contents | |
| You wait for answer | |
| ⏱️ **~2 minutes** | ⚡ **~5 seconds** |

---

## 🔌 MCP Integration

Connect **Claude Desktop** or **Cursor** directly to your pulse state.

Start the MCP server:

```bash
pulse mcp
```

Add to your `claude_desktop_config.json`:

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

Available MCP tools:

| Tool | Returns |
|---|---|
| `get_pulse_state` | Full current coding context |
| `get_hottest_error` | Most recent error with full stderr |
| `get_active_context` | Active file, language, git branch |
| `get_history` | Last 30 minutes activity timeline |

---

## 🧪 Test Results

All tests run against real broken files using `pulse fix`:

| # | Error Type | Captured | Fixed | Verified |
|---|---|---|---|---|
| 1 | `ZeroDivisionError` | ✅ | ✅ | ✅ |
| 2 | `SyntaxError` | ✅ | ✅ | ✅ |
| 3 | `ModuleNotFoundError` | ✅ | ✅ | ✅ |
| 4 | `KeyError` | ✅ | ✅ | ✅ |
| 5 | Large project stderr | ✅ via `pulse_run` | ✅ | ✅ |

**Time from error to AI fix: ~1 second** (vs ~30 seconds copy-pasting manually)

---

## 🌍 Language Support

| Language | Detection | Error Capture | Fix |
|---|---|---|---|
| Python | ✅ | ✅ | ✅ |
| JavaScript | ✅ | ✅ | ✅ |
| TypeScript | ✅ | ✅ | ✅ |
| React / Next.js | ✅ | ✅ | ✅ |
| Rust | ✅ | ✅ | ✅ |
| Go | ✅ | ✅ | ✅ |
| Java | ✅ | ✅ | ✅ |

---

## 🔑 API Key Setup (All Platforms)

| Platform | Method | Command |
|---|---|---|
| **Any** | Run once | `tmind auth` |
| **Linux/Mac** | Environment variable | `export GROQ_API_KEY="your_key"` |
| **Windows** | PowerShell | `$env:GROQ_API_KEY="your_key"` |
| **Permanent** | Add to shell config | `echo 'export GROQ_API_KEY="key"' >> ~/.bashrc` |

---

## 🛡️ Security & Privacy

TerminalPulse is designed with a **local-first** philosophy:

- **Local State:** Your context graph (`~/.devpulse_state.json`) lives entirely on your machine — nothing is streamed to a cloud service.
- **Targeted Context:** Only the specific error and active file are sent to the AI, never your full codebase.
- **Secure Key Storage:** API keys are stored in your OS Keyring (Windows/Mac) or a protected local file (Linux/WSL), never in plain `.env` files.

---

## 📋 Requirements

- Python 3.10+
- WSL Ubuntu
- `netcat` (`nc`) — pre-installed on Ubuntu
- `terminalmind` — required for `pulse fix`
- Windows 11 + VS Code — for focus tracking (optional)

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add some amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
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
