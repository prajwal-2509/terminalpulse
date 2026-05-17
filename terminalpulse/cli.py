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

    state = json.loads(STATE_FILE.read_text())
    hottest = state.get("hottest", [])

    # find hottest error
    error = next((e for e in hottest if e["type"] == "command_failed"), None)
    # find hottest focus
    focus = next((e for e in hottest if e["type"] == "focus_changed"), None)

    if not error:
        print("[yellow]No recent errors found in pulse state.[/]")
        raise typer.Exit(0)

    cmd = error.get("cmd", "unknown command")
    exit_code = error.get("exit_code", 1)
    active_file = focus.get("path", "unknown file") if focus else "unknown file"

    context = f"Command failed: `{cmd}` (exit code {exit_code}). Active file: {active_file}."
    print(f"[cyan]Sending to TerminalMind:[/] {context}")

    subprocess.run(["tmind", "ask", context])


if __name__ == "__main__":
    app()
