import os, sys, json, subprocess
from pathlib import Path
import typer, asyncio
from rich import print
from . import daemon as _daemon

app = typer.Typer(help="TerminalPulse — short-term memory for AI agents")
STATE_FILE = Path.home() / ".devpulse_state.json"


@app.command()
def start(watch: str = typer.Option(".", help="Directory to watch")):
    """Run the pulse daemon in the foreground."""
    asyncio.run(_daemon.main(os.path.abspath(watch)))


@app.command()
def state():
    """Print the current hottest context."""
    if not STATE_FILE.exists():
        print("[yellow]No state yet. Is the daemon running?[/]")
        raise typer.Exit(1)
    print(json.loads(STATE_FILE.read_text()))


@app.command()
def fix():
    """Read hottest error and active file, send to TerminalMind to fix."""
    if not STATE_FILE.exists():
        print("[yellow]No state yet. Is the daemon running?[/]")
        raise typer.Exit(1)

    state_data = json.loads(STATE_FILE.read_text())
    hottest = state_data.get("hottest", [])

    error = next((e for e in hottest if e["type"] == "command_failed"), None)
    focus = next((e for e in hottest if e["type"] == "focus_changed"), None)

    if not error:
        print("[yellow]No recent errors found in pulse state.[/]")
        raise typer.Exit(0)

    cmd = error.get("cmd", "unknown command")
    exit_code = error.get("exit_code", 1)
    active_file = focus.get("path", "unknown file") if focus else "unknown file"
    stderr = error.get("stderr_tail", None)

    if stderr:
        context = f"Command: `{cmd}` failed with exit code {exit_code}.\nActive file: {active_file}.\nError output:\n{stderr.replace('|', chr(10))}"
        print(f"[cyan]Sending to TerminalMind with full error context[/]")
        subprocess.run(["tmind", "ask", context])
    else:
        context = f"Command failed: `{cmd}` (exit code {exit_code}). Active file: {active_file}."
        print(f"[cyan]Sending to TerminalMind:[/] {context}")
        subprocess.run(["tmind", "heal", cmd], cwd=error.get("cwd", "."))

@app.command()
def init():
    """Auto-setup: injects shell hook into .bashrc so pulse works automatically."""
    bashrc = Path.home() / ".bashrc"

    hook = '''
# TerminalPulse hook
_pulse_sock="$HOME/.terminalpulse.sock"
_pulse_last_cmd=""
_pulse_preexec() {
  [[ "$BASH_COMMAND" == _pulse_* ]] && return
  _pulse_last_cmd="$BASH_COMMAND"
}
trap '_pulse_preexec' DEBUG
_pulse_precmd() {
  local code=$?
  if [ $code -ne 0 ] && [ -n "$_pulse_last_cmd" ] && [ -S "$_pulse_sock" ]; then
    printf \'{"type":"command_failed","cmd":"%s","exit_code":%d,"cwd":"%s"}\\n\' \\
      "$_pulse_last_cmd" "$code" "$PWD" | nc -U "$_pulse_sock" 2>/dev/null
  fi
  _pulse_last_cmd=""
}
PROMPT_COMMAND="_pulse_precmd${PROMPT_COMMAND:+;$PROMPT_COMMAND}"
'''

    content = bashrc.read_text() if bashrc.exists() else ""
    if "TerminalPulse hook" in content:
        print("[yellow]TerminalPulse hook already exists in .bashrc — skipping.[/]")
        return

    with open(bashrc, "a") as f:
        f.write(hook)

    print("[green]TerminalPulse hook added to ~/.bashrc[/]")
    print("[cyan]Run: source ~/.bashrc to activate[/]")


@app.command()
def init_windows():
    """Print instructions to set up the Windows focus tracker."""
    print("[cyan]Windows Setup Instructions:[/]")
    print("")
    print("1. Open Windows PowerShell")
    print("2. Run this command:")
    print(f"[green]   python {Path.home() / 'terminalpulse/terminalpulse/windows_tracker.py'}[/]")
    print("")
    print("3. Keep PowerShell open while coding.")
    print("[yellow]Tip: Add it to Windows Task Scheduler to auto-start on login.[/]")


if __name__ == "__main__":
    app()
