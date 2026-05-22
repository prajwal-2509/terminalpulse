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
| `pulse state` | Show current context as JSON |
| `pulse history` | Show 30-minute activity timeline |
| `pulse init` | Inject shell hook into `.bashrc` |
| `pulse init-windows` | Windows setup instructions |
| `pulse mcp` | Start MCP server for Claude Desktop / Cursor |
| `pulse_run <cmd>` | Run command with full stderr capture |

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
