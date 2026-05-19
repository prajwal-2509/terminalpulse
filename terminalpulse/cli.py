import os, sys, json, subprocess
from pathlib import Path
from datetime import datetime
import typer, asyncio
from rich import print
from rich.table import Table
from rich.console import Console
from . import daemon as _daemon

app = typer.Typer(help="TerminalPulse — short-term memory for AI agents")
STATE_FILE = Path.home() / ".devpulse_state.json"
console = Console()


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

    s = json.loads(STATE_FILE.read_text())
    hottest = s.get("hottest", [])
    git = s.get("git", {})
    project_type = s.get("project_type", "unknown")
    active_file = s.get("active_file", "unknown file")
    active_language = s.get("active_language", "unknown")

    error = next((e for e in hottest if e["type"] == "command_failed"), None)

    if not error:
        print("[yellow]No recent errors found in pulse state.[/]")
        raise typer.Exit(0)

    cmd = error.get("cmd", "unknown command")
    exit_code = error.get("exit_code", 1)
    stderr = error.get("stderr_tail", None)

    # build rich context
    context_parts = [
        f"Project type: {project_type}",
        f"Language: {active_language}",
        f"Active file: {active_file}",
        f"Command failed: `{cmd}` (exit code {exit_code})",
    ]

    if git.get("branch"):
        context_parts.append(f"Git branch: {git['branch']}")
    if git.get("changed_files"):
        context_parts.append(f"Changed files: {git['changed_files']}")
    if git.get("last_commit"):
        context_parts.append(f"Last commit: {git['last_commit']}")
    if stderr:
        context_parts.append(f"Error output:\n{stderr.replace('|', chr(10))}")

    context = "\n".join(context_parts)

    print(f"[cyan]Project:[/] {project_type} ({active_language})")
    print(f"[cyan]Branch:[/] {git.get('branch', 'unknown')}")
    print(f"[cyan]Error:[/] {cmd}")
    print(f"[cyan]Sending full context to TerminalMind...[/]")

    if stderr:
        subprocess.run(["tmind", "ask", context])
    else:
        subprocess.run(["tmind", "heal", cmd], cwd=error.get("cwd", "."))


@app.command()
def history():
    """Show timeline of last 30 minutes of coding activity."""
    if not STATE_FILE.exists():
        print("[yellow]No state yet. Is the daemon running?[/]")
        raise typer.Exit(1)

    s = json.loads(STATE_FILE.read_text())
    events = s.get("history", [])

    if not events:
        print("[yellow]No history yet.[/]")
        raise typer.Exit(0)

    table = Table(title="TerminalPulse — Coding History")
    table.add_column("Time", style="cyan")
    table.add_column("Event", style="white")
    table.add_column("Detail", style="green")
    table.add_column("Language", style="yellow")

    for ev in reversed(events[-30:]):
        t = datetime.fromtimestamp(ev["ts"]).strftime("%H:%M:%S")
        table.add_row(
            t,
            ev["type"],
            ev["detail"][:60] if ev["detail"] else "",
            ev.get("language") or "",
        )

    console.print(table)


@app.command()
def init():
    """Auto-setup: injects shell hook into .bashrc."""
    bashrc = Path.home() / ".bashrc"

    hook = '''
# TerminalPulse hook
_pulse_sock="$HOME/.terminalpulse.sock"
_pulse_last_cmd=""
_pulse_preexec() {
  [[ "$BASH_COMMAND" == _pulse_* ]] || [[ "$BASH_COMMAND" == pulse_run* ]] && return
  _pulse_last_cmd="$BASH_COMMAND"
}
trap '_pulse_preexec' DEBUG
_pulse_precmd() {
  local code=$?
  if [ $code -ne 0 ] && [ -n "$_pulse_last_cmd" ] && [ -S "$_pulse_sock" ]; then
    printf \'{"type":"command_failed","cmd":"%s","exit_code":%d,"cwd":"%s"}\n\' \\
      "$_pulse_last_cmd" "$code" "$PWD" | nc -U "$_pulse_sock" 2>/dev/null
  fi
  _pulse_last_cmd=""
}
PROMPT_COMMAND="_pulse_precmd${PROMPT_COMMAND:+;$PROMPT_COMMAND}"

# TerminalPulse - large project wrapper
pulse_run() {
  local stderr_file
  stderr_file=$(mktemp)
  "$@" 2> >(tee "$stderr_file" >&2)
  local code=$?
  if [ $code -ne 0 ] && [ -S "$_pulse_sock" ]; then
    local stderr_out
    stderr_out=$(tail -n 20 "$stderr_file" | sed \'s/"/\\\\"/g\' | tr \'\\n\' \'|\')
    local cmd_str="$*"
    printf \'{"type":"command_failed","cmd":"%s","exit_code":%d,"cwd":"%s","stderr_tail":"%s"}\n\' \\
      "$cmd_str" "$code" "$PWD" "$stderr_out" \\
      | nc -U "$_pulse_sock" 2>/dev/null
  fi
  rm -f "$stderr_file"
  return $code
}
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

@app.command()
def mcp():
    """Start the MCP server for Claude Desktop and Cursor integration."""
    from . import mcp_server
    print("[green]Starting TerminalPulse MCP server on port 7078[/]")
    print("[cyan]Add this to your Claude Desktop config to connect[/]")
    asyncio.run(mcp_server.main())

if __name__ == "__main__":
    app()
