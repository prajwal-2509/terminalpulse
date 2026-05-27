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

```
You hit an error.

→  read the traceback
→  copy it
→  open AI chat
→  paste and explain your project
→  explain the file you were in
→  explain your git branch
→  wait
→  switch back to terminal
→  apply the fix

That's 2 minutes. Every. Single. Time.
```

---

## ✅ The Solution

```bash
python3 app.py
# KeyError: 'user_id'
# ⚡ Error detected. Run 'pulse fix' to auto-fix.

pulse fix
# → knows the command that failed
# → knows the full error output
# → knows the file you were editing
# → knows your git branch
# → fix in seconds
```

---

## 🏗️ How It Works

Three silent streams feed a **time-decaying knowledge graph**:

```
┌─────────────────────────────────────────────────────────┐
│                    TerminalPulse Daemon                  │
│                                                         │
│  VS Code title  ──── Focus stream   ──┐                 │
│  File saves     ──── Activity stream ─┼──▶ heat graph   │
│  Bash errors    ──── Distress stream ─┘    │            │
│                                            ▼            │
│                               ~/.devpulse_state.json    │
└─────────────────────────────────────────────────────────┘
                                            │
                              pulse fix ────┘
                                  │
                          TerminalMind ──▶ patch
```

Every event gets a heat score that decays over time:

```
heat = e^(-λ × seconds_since_event) × severity
```

Stale context fades. The AI always gets what's relevant *right now*.

### Stack

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
# 1. Inject shell hook
pulse install-deps
pulse init
source ~/.bashrc

# 2. Start watching
cd your-project
pulse watch
```

**Optional — VS Code focus tracking on Windows:**

```powershell
python \\wsl.localhost\Ubuntu-22.04\home\username\terminalpulse\terminalpulse\windows_tracker.py
```

Or run `pulse init-windows` for exact instructions.

---

## 🛠️ Commands

| Command | What It Does |
|---|---|
| `pulse watch` | Auto-detect project type and start daemon |
| `pulse start --watch .` | Start daemon manually |
| `pulse fix` | Send hottest error + full context to AI |
| `pulse context` | Formatted context block for any AI |
| `pulse state` | Current context as JSON |
| `pulse history` | 30-minute activity timeline |
| `pulse report` | Daily summary |
| `pulse insights` | Pattern detection |
| `pulse init` | Inject shell hook into `.bashrc` |
| `pulse init-windows` | Windows setup instructions |
| `pulse install-deps` | Install system dependencies |
| `pulse mcp` | Start MCP server for Claude Desktop / Cursor |
| `pulse_run <cmd>` | Run command with full stderr capture |

---

## ⚡ Auto-Suggest on Error

Every failed command triggers:

```
⚡ Error detected. Run 'pulse fix' to auto-fix.
```

No switching tabs. No searching. It's right there.

---

## 📋 `pulse context` — Works With Any AI

```bash
pulse context
```

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

Paste into Claude, ChatGPT, Cursor — whatever you use. Zero explaining.

---

## 📊 `pulse report` — Daily Summary

```bash
pulse report
```

```
📊 TerminalPulse Daily Report    Branch: feature/auth
─────────────────────────────────────────────────────
  Files saved      12       Most edited:   auth.ts (4x)
  Errors hit        5       Most focused:  login.ts
  Focus changes     8       Top error:     npm run build (3x)

  Rough session — 5 errors. Run pulse insights for patterns.
```

---

## 🔍 `pulse insights` — Pattern Detection

```bash
pulse insights
```

```
⚡ TerminalPulse Insights    React + TypeScript › feature/auth
──────────────────────────────────────────────────────────────
  12 saves  ·  5 errors  ·  20 events

  Most active    auth.ts (4 saves)
  Recurring      npm run build  failed 3×  → run pulse fix
  Error rate     41%  → run tests more frequently
```

---

## 🧑‍💻 Real World Usage

```bash
# One-time install
pip install terminalpulse terminalmind && tmind auth
pulse install-deps && pulse init && source ~/.bashrc

# Every session
cd your-project && pulse watch

# When something breaks
pulse fix              # auto-fix via TerminalMind
pulse context          # or paste context into any AI

# End of session
pulse insights         # patterns
pulse report           # summary
```

### Before vs After

```
WITHOUT TerminalPulse          WITH TerminalPulse
──────────────────────         ──────────────────
Copy error manually            — auto-captured
Open AI chat                   — already connected
Explain your project           — auto-detected
Explain git branch             — auto-detected
Paste file contents            — auto-read
Wait for response              — instant
Apply fix manually             — one keypress

⏱  ~2 minutes                 ⚡  ~5 seconds
```

---

## 🔌 MCP Integration

Connect **Claude Desktop** or **Cursor** directly to your live pulse state.

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

Available tools:

| Tool | Returns |
|---|---|
| `get_pulse_state` | Full current coding context |
| `get_hottest_error` | Most recent error with full stderr |
| `get_active_context` | Active file, language, git branch |
| `get_history` | Last 30 minutes activity timeline |

---

## 🧪 Test Results

| Error Type | Captured | Fixed | Time |
|---|---|---|---|
| `ZeroDivisionError` | ✓ | ✓ | ~1s |
| `SyntaxError` | ✓ | ✓ | ~1s |
| `ModuleNotFoundError` | ✓ | ✓ | ~1s |
| `KeyError` | ✓ | ✓ | ~1s |
| Large stderr via `pulse_run` | ✓ | ✓ | ~1s |

---

## 🌍 Language Support

| Language | Detected | Errors Captured | Fixes Generated |
|---|---|---|---|
| Python | ✓ | ✓ | ✓ |
| JavaScript | ✓ | ✓ | ✓ |
| TypeScript | ✓ | ✓ | ✓ |
| React / Next.js | ✓ | ✓ | ✓ |
| Rust | ✓ | ✓ | ✓ |
| Go | ✓ | ✓ | ✓ |
| Java | ✓ | ✓ | ✓ |

---

## 🔑 API Key Setup (All Platforms)

| Platform | Command |
|---|---|
| Run once (any) | `tmind auth` |
| Linux / Mac | `export GROQ_API_KEY="your_key"` |
| Windows PowerShell | `$env:GROQ_API_KEY="your_key"` |
| Permanent | `echo 'export GROQ_API_KEY="key"' >> ~/.bashrc` |

---

## 🛡️ Security & Privacy

```
Your code never leaves your machine.

  ~/.devpulse_state.json   ← lives locally, never uploaded
  Error context only       ← only the broken file goes to Groq
  API keys                 ← OS Keyring or ~/.terminalmind_key
```

---

## 📋 Requirements

- Python 3.10+
- WSL Ubuntu
- `netcat` — pre-installed on Ubuntu
- `terminalmind` — for `pulse fix`
- Windows 11 + VS Code — focus tracking (optional)

---

## 🤝 Contributing

1. Fork → `git checkout -b feature/your-feature`
2. Build → `git commit -m 'your feature'`
3. Ship → `git push origin feature/your-feature` → Pull Request

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
