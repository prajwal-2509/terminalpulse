# ⚡ TerminalPulse

> **Short-term memory for AI agents. Captures your coding context in real time — silently.**

TerminalPulse runs in the background and watches your terminal, editor, and filesystem. When something goes wrong, type `pulse fix` — no copy-pasting, no explaining. It already knows what happened.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![PyPI](https://img.shields.io/pypi/v/terminalpulse?style=flat-square&logo=pypi)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-WSL%20%7C%20Linux-orange?style=flat-square)

---

## 📋 Table of Contents

- [Architecture](#-architecture)
- [Installation](#-installation)
- [Setup](#-setup)
- [Usage & Commands](#-usage--commands)
- [Test Results](#-test-results)
- [Requirements](#-requirements)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🏗️ Architecture

TerminalPulse runs three silent streams feeding a time-decaying knowledge graph:

| Stream | Source | What It Captures |
|---|---|---|
| **Focus** | VS Code window title (Windows) | Which file is active in your editor |
| **Activity** | Filesystem watchdog (WSL) | Which files were just saved |
| **Distress** | Bash hook (WSL) | Which terminal commands just failed |

The graph applies **temporal decay** to every event — older events fade automatically so the AI always gets current context, not noise from this morning:

```
W(n) = e^( -λ × (t_now - t_event) )
```

### Data Flow

```
VS Code (Windows) → HTTP:7077 → pulsed daemon → ~/.devpulse_state.json
Terminal errors   → Unix socket → pulsed daemon → ~/.devpulse_state.json
File saves        → watchdog   → pulsed daemon → ~/.devpulse_state.json
                                      ↓
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

## ⚙️ Setup

### Step 1 — Inject the shell hook (one time only)

```bash
pulse init
source ~/.bashrc
```

### Step 2 — Start the daemon

```bash
pulse start --watch /path/to/your/project
```

### Step 3 — Windows focus tracking (optional)

For VS Code file detection, open **Windows PowerShell** and run:

```powershell
python path\to\terminalpulse\windows_tracker.py
```

Or run the following for exact setup instructions:

```bash
pulse init-windows
```

---

## 🛠️ Usage & Commands

---

### `pulse init`

Auto-injects the shell hook into `~/.bashrc`. Run once after install.

```bash
pulse init
source ~/.bashrc
```

**What it does:** Hooks into your shell so every failed command is silently captured by the daemon.

---

### `pulse start`

Starts the background daemon that watches your project directory.

```bash
pulse start --watch .
```

**What it does:** Launches the async daemon, begins watching for file saves, focus changes, and terminal errors.

---

### `pulse state`

Prints the current hottest coding context as JSON — ranked by recency and decay weight.

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
      "stderr_tail": "ZeroDivisionError: division by zero"
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

### `pulse fix`

Reads the hottest error and active file, then sends full context to TerminalMind for an auto-fix.

```bash
pulse fix
```

**What it does:** No input needed. It already knows what broke, which file is open, and what you were running.

---

### `pulse_run` — for large projects

Use this prefix for large build commands to capture full stderr output:

```bash
pulse_run npm run build
pulse_run ./gradlew build
pulse_run pytest

# Then fix whatever broke:
pulse fix
```

**What it does:** Wraps your command and pipes the full stderr into the daemon — useful when build output is too large for the standard shell hook.

---

### `pulse init-windows`

Prints Windows PowerShell setup instructions for VS Code focus tracking.

```bash
pulse init-windows
```

---

## 🧪 Test Results

All tests run against real broken Python files using `pulse fix`:

| # | Error Type | Captured | Fixed | Verified |
|---|---|---|---|---|
| 1 | `ZeroDivisionError` | ✅ | ✅ | ✅ |
| 2 | `SyntaxError` | ✅ | ✅ | ✅ |
| 3 | `ModuleNotFoundError` | ✅ | ✅ (install suggestion) | ✅ |
| 4 | Large project stderr | ✅ via `pulse_run` | ✅ | ✅ |

**Time from error to AI fix:** ~1 second (vs ~30 seconds copy-pasting manually)

---

## 📋 Requirements

- Python 3.10+
- WSL Ubuntu (Linux daemon)
- `netcat` (`nc`) — usually pre-installed on Ubuntu
- `terminalmind` — required for `pulse fix`
- Windows 11 with VS Code — for focus tracking (optional)

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

<p align="center">Built with ❤️ for developers who are tired of copy-pasting errors into AI.</p>
