# TerminalPulse ⚡

Short-term memory for AI agents. Captures your coding context in real time — silently.

## The Problem
Every AI tool today requires you to manually copy-paste your error. That takes 30 seconds and breaks your flow.

## The Solution
TerminalPulse watches your terminal, editor, and filesystem in the background. When something goes wrong, just type `pulse fix` — no copy-pasting, no explaining.

## Install
pip install terminalpulse

## Setup
pulse init
source ~/.bashrc
pulse start --watch .

## Commands
| Command | What it does |
|---|---|
| `pulse init` | Auto-injects shell hook into .bashrc |
| `pulse start` | Starts the background daemon |
| `pulse state` | Shows current coding context as JSON |
| `pulse fix` | Sends hottest error to TerminalMind for auto-fix |
| `pulse init-windows` | Setup instructions for Windows focus tracking |

## How it works
Three streams feed a time-decaying knowledge graph:
- **Focus** — which file is open in VS Code
- **Activity** — which files were just saved
- **Distress** — which terminal commands just failed

Older events decay automatically so the AI always gets current context.

## Test Results
| Test | Error Type | Result |
|---|---|---|
| Test 1 | ZeroDivisionError | Fixed and verified |
| Test 2 | ModuleNotFoundError | Captured (fix depends on TerminalMind version) |
| Test 3 | SyntaxError | Fixed and verified |

## Requirements
- Python 3.10+
- WSL Ubuntu (for Linux daemon)
- terminalmind (for pulse fix command)

## Architecture
```
VS Code (Windows) → HTTP:7077 → pulsed daemon → ~/.devpulse_state.json
Terminal errors → Unix socket → pulsed daemon → ~/.devpulse_state.json
File saves → watchdog → pulsed daemon → ~/.devpulse_state.json
                                              ↓
                                         pulse fix → TerminalMind → Auto-fix
```
