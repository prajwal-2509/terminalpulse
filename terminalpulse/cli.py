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


def _build_context(s: dict, error: dict) -> str:
    git = s.get("git", {})
    project_type = s.get("project_type", "unknown")
    active_file = s.get("active_file") or "not detected"
    active_language = s.get("active_language") or "not detected"
    history = s.get("history", [])
    saves = [e for e in history if e["type"] == "file_saved"][-5:]

    cmd = error.get("cmd", "unknown") if error else "none"
    exit_code = error.get("exit_code", 1) if error else 0
    stderr = error.get("stderr_tail") if error else None

    lines = []
    lines.append("=== TerminalPulse Context ===")
    lines.append(f"Project: {project_type}")
    lines.append(f"Language: {active_language}")
    lines.append(f"Active file: {active_file}")
    if git.get("branch"):
        lines.append(f"Git branch: {git['branch']}")
    if git.get("last_commit"):
        lines.append(f"Last commit: {git['last_commit']}")
    if git.get("changed_files"):
        lines.append(f"Changed files:\n{git['changed_files']}")
    if saves:
        lines.append("\nRecently saved:")
        for e in saves:
            lines.append(f"  - {e['detail']}")
    if error:
        lines.append(f"\nLast error:")
        lines.append(f"  Command: {cmd}")
        lines.append(f"  Exit code: {exit_code}")
        if stderr:
            lines.append(f"  Output:\n{stderr.replace('|', chr(10))}")
    if active_file and active_file != "not detected" and Path(active_file).exists():
        try:
            code = Path(active_file).read_text().split("\n")[:100]
            lines.append(f"\nFile contents ({active_file}):")
            lines.append("\n".join(code))
        except Exception:
            pass
    elif error and error.get("cwd"):
        cwd = Path(error.get("cwd"))
        cmd_parts = cmd.split()
        for part in cmd_parts:
            candidate = cwd / part
            if candidate.exists() and candidate.suffix in {
                ".py", ".js", ".ts", ".tsx", ".jsx", ".rs", ".go"
            }:
                try:
                    code_lines = candidate.read_text().split("\n")[:200]
                    lines.append(f"\nFile contents ({part}):")
                    lines.append("\n".join(code_lines))
                except Exception:
                    pass
    lines.append("=============================")
    return "\n".join(lines)


def _copy_to_clipboard(ctx: str):
    try:
        subprocess.run(["xclip", "-selection", "clipboard"],
                      input=ctx.encode(), check=True)
        print("[green]✓ Copied to clipboard — paste into any AI[/green]")
    except Exception:
        print("[yellow]Tip: install xclip to auto-copy: sudo apt install xclip[/yellow]")


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
    active_file = s.get("active_file") or "not detected"
    active_language = s.get("active_language") or "not detected"

    error = next((e for e in hottest if e["type"] == "command_failed"), None)

    if not error:
        print("[yellow]No recent errors found in pulse state.[/]")
        raise typer.Exit(0)

    cmd = error.get("cmd", "unknown command")
    exit_code = error.get("exit_code", 1)
    stderr = error.get("stderr_tail", None)

    # check if terminalmind is installed
    tmind_available = subprocess.run(
        ["which", "tmind"], capture_output=True
    ).returncode == 0

    if not tmind_available:
        print("[yellow]TerminalMind not installed. Falling back to pulse context...[/]")
        print("[dim]Install with: pip install terminalmind && tmind auth[/dim]")
        ctx = _build_context(s, error)
        console.print(f"\n[cyan]{ctx}[/cyan]\n")
        _copy_to_clipboard(ctx)
        raise typer.Exit(0)

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

    if active_file and active_file != "not detected" and Path(active_file).exists():
        try:
            file_contents = Path(active_file).read_text()
            lines = file_contents.split("\n")[:200]
            context_parts.append(
                f"Contents of {active_file}:\n" + "\n".join(lines)
            )
        except Exception:
            pass
    elif error.get("cwd"):
        cwd = Path(error.get("cwd"))
        cmd_parts = cmd.split()
        for part in cmd_parts:
            candidate = cwd / part
            if candidate.exists() and candidate.suffix in {
                ".py", ".js", ".ts", ".tsx", ".jsx", ".rs", ".go"
            }:
                try:
                    lines = candidate.read_text().split("\n")[:200]
                    context_parts.append(
                        f"Contents of {part}:\n" + "\n".join(lines)
                    )
                except Exception:
                    pass

    context = "\n".join(context_parts)

    print(f"[cyan]Project:[/] {project_type} ({active_language})")
    print(f"[cyan]Branch:[/] {git.get('branch', 'not a git repo')}")
    print(f"[cyan]Error:[/] {cmd}")
    print(f"[cyan]Sending full context to TerminalMind...[/]")

    full_context = "Do not use any tools. Answer only from this context:\n\n" + context
    subprocess.run(["tmind", "ask", full_context])


@app.command()
def context():
    """Generate a formatted context block for any AI — Claude, ChatGPT, Cursor."""
    if not STATE_FILE.exists():
        print("[yellow]No state yet. Is the daemon running?[/]")
        raise typer.Exit(1)

    s = json.loads(STATE_FILE.read_text())
    hottest = s.get("hottest", [])
    error = next((e for e in hottest if e["type"] == "command_failed"), None)
    ctx = _build_context(s, error)
    console.print(f"\n[cyan]{ctx}[/cyan]\n")
    _copy_to_clipboard(ctx)


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
def insights():
    """Detect patterns in your coding session and surface actionable insights."""
    if not STATE_FILE.exists():
        print("[yellow]No state yet. Is the daemon running?[/]")
        raise typer.Exit(1)

    s = json.loads(STATE_FILE.read_text())
    history = s.get("history", [])
    git = s.get("git", {})
    project_type = s.get("project_type", "unknown")

    if len(history) < 3:
        print("[yellow]Not enough history yet. Keep coding for a few minutes.[/]")
        raise typer.Exit(0)

    error_commands: dict = {}
    file_time: dict = {}
    total_errors = 0
    total_saves = 0

    for ev in history:
        t = ev["type"]
        detail = ev.get("detail", "") or ""

        if t == "command_failed":
            total_errors += 1
            error_commands[detail] = error_commands.get(detail, 0) + 1

        if t == "file_saved":
            total_saves += 1
            fname = Path(detail).name if detail else "unknown"
            file_time[fname] = file_time.get(fname, 0) + 1

    most_edited = max(file_time, key=file_time.get) if file_time else None
    most_errored_cmd = max(error_commands, key=error_commands.get) if error_commands else None

    console.print("\n[bold cyan]⚡ TerminalPulse Insights[/bold cyan]")
    branch = git.get('branch') or 'not a git repo'
    console.print(f"[dim]Project: {project_type} | Branch: {branch}[/dim]\n")
    console.print(f"[white]Session activity:[/white]")
    console.print(f"  • {total_saves} file saves recorded")
    console.print(f"  • {total_errors} errors detected")
    console.print(f"  • {len(history)} total events\n")

    if most_edited:
        console.print(f"[yellow]Most active file:[/yellow] {most_edited} ({file_time[most_edited]} saves)")

    if most_errored_cmd and error_commands[most_errored_cmd] > 1:
        count = error_commands[most_errored_cmd]
        console.print(f"[red]Recurring failure:[/red] `{most_errored_cmd}` failed {count} times")
        console.print(f"  [dim]→ Suggestion: run `pulse fix` to investigate root cause[/dim]")

    if total_saves > 0:
        error_rate = round((total_errors / total_saves) * 100)
        if error_rate > 50:
            console.print(f"[red]High error rate:[/red] {error_rate}%")
            console.print(f"  [dim]→ Consider running tests more frequently[/dim]")
        elif error_rate > 20:
            console.print(f"[yellow]Moderate error rate:[/yellow] {error_rate}%")
        else:
            console.print(f"[green]Low error rate:[/green] {error_rate}% — clean session")

    changed = git.get("changed_files", "") or ""
    if changed and most_errored_cmd:
        changed_list = changed.split("\n")
        console.print(f"\n[white]Changed files this session:[/white]")
        for f in changed_list[:5]:
            if f:
                console.print(f"  • {f}")

    console.print("")


@app.command()
def report():
    """Show end of day coding summary."""
    if not STATE_FILE.exists():
        print("[yellow]No state yet. Is the daemon running?[/]")
        raise typer.Exit(1)

    s = json.loads(STATE_FILE.read_text())
    history = s.get("history", [])
    git = s.get("git", {})

    if not history:
        print("[yellow]No history yet.[/]")
        raise typer.Exit(0)

    errors = [e for e in history if e["type"] == "command_failed"]
    saves = [e for e in history if e["type"] == "file_saved"]
    focuses = [e for e in history if e["type"] == "focus_changed"]

    error_counts: dict = {}
    for e in errors:
        cmd = e.get("detail", "unknown")
        error_counts[cmd] = error_counts.get(cmd, 0) + 1
    most_common_error = max(error_counts, key=error_counts.get) if error_counts else None

    file_counts: dict = {}
    for e in saves:
        f = Path(e.get("detail", "")).name
        file_counts[f] = file_counts.get(f, 0) + 1
    most_edited = max(file_counts, key=file_counts.get) if file_counts else None

    focus_counts: dict = {}
    for e in focuses:
        f = Path(e.get("detail", "")).name
        focus_counts[f] = focus_counts.get(f, 0) + 1
    most_focused = max(focus_counts, key=focus_counts.get) if focus_counts else None

    console.print("\n[bold cyan]📊 TerminalPulse Daily Report[/bold cyan]")
    branch = git.get('branch') or 'not a git repo'
    console.print(f"[dim]Branch: {branch}[/dim]\n")
    console.print(f"  • Files saved:     [green]{len(saves)}[/green]")
    console.print(f"  • Errors hit:      [red]{len(errors)}[/red]")
    console.print(f"  • Focus changes:   [yellow]{len(focuses)}[/yellow]")

    if most_edited:
        console.print(f"\n[white]Most edited file:[/white] {most_edited} ({file_counts[most_edited]} saves)")
    if most_focused:
        console.print(f"[white]Most focused file:[/white] {most_focused}")
    if most_common_error and error_counts[most_common_error] > 1:
        console.print(f"[white]Most common error:[/white] `{most_common_error}` ({error_counts[most_common_error]}x)")

    if len(errors) == 0:
        console.print("\n[green]Clean session — no errors![/green]")
    elif len(errors) <= 3:
        console.print("\n[yellow]Good session — few errors.[/yellow]")
    else:
        console.print(f"\n[red]Rough session — {len(errors)} errors. Run `pulse insights` for patterns.[/red]")

    console.print("")


@app.command()
def watch():
    """Auto-detect project type and start watching intelligently."""
    cwd = Path.cwd()

    if (cwd / "package.json").exists():
        pkg = json.loads((cwd / "package.json").read_text())
        deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
        if "react" in deps and "typescript" in deps:
            project = "React + TypeScript"
        elif "next" in deps:
            project = "Next.js"
        elif "react" in deps:
            project = "React"
        else:
            project = "Node.js"
    elif (cwd / "pyproject.toml").exists() or (cwd / "requirements.txt").exists():
        project = "Python"
    elif (cwd / "Cargo.toml").exists():
        project = "Rust"
    elif (cwd / "go.mod").exists():
        project = "Go"
    else:
        project = "Unknown"

    print(f"[green]Project detected:[/] {project}")
    print(f"[cyan]Watching:[/] {cwd}")
    print(f"[yellow]Ignoring:[/] node_modules, .git, __pycache__, dist, build, .venv")
    print(f"[cyan]Starting daemon...[/]")

    asyncio.run(_daemon.main(str(cwd)))


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
    echo "⚡ Error detected. Run \'pulse fix\' to auto-fix." >&2
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
    echo "⚡ Error detected. Run \'pulse fix\' to auto-fix." >&2
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
def install_deps():
    """Install required system dependencies (xclip, netcat)."""
    print("[cyan]Installing system dependencies...[/cyan]")
    subprocess.run(["sudo", "apt-get", "install", "-y", "xclip", "netcat-openbsd"])
    print("[green]Done. Run 'pulse init' and 'source ~/.bashrc' to activate.[/green]")


@app.command()
def mcp():
    """Start the MCP server for Claude Desktop and Cursor integration."""
    from . import mcp_server
    print("[green]Starting TerminalPulse MCP server on port 7078[/]")
    print("[cyan]Add this to your Claude Desktop config to connect[/]")
    asyncio.run(mcp_server.main())

@app.command()
def summary():
    """Plain English summary of your current coding session."""
    if not STATE_FILE.exists():
        print("[yellow]No state yet. Is the daemon running?[/]")
        raise typer.Exit(1)

    s = json.loads(STATE_FILE.read_text())
    history = s.get("history", [])
    git = s.get("git", {})
    project_type = s.get("project_type", "unknown")
    active_file = s.get("active_file") or "unknown"

    errors = [e for e in history if e["type"] == "command_failed"]
    saves = [e for e in history if e["type"] == "file_saved"]
    focuses = [e for e in history if e["type"] == "focus_changed"]

    file_counts: dict = {}
    for e in saves:
        f = Path(e.get("detail", "")).name
        file_counts[f] = file_counts.get(f, 0) + 1

    error_counts: dict = {}
    for e in errors:
        cmd = e.get("detail", "unknown")
        error_counts[cmd] = error_counts.get(cmd, 0) + 1

    most_edited = max(file_counts, key=file_counts.get) if file_counts else None
    most_errored = max(error_counts, key=error_counts.get) if error_counts else None
    branch = git.get("branch") or "unknown branch"
    last_commit = git.get("last_commit") or "no commits"

    console.print("\n[bold cyan]📝 Session Summary[/bold cyan]\n")

    if project_type != "unknown":
        console.print(f"You are working on a [green]{project_type}[/green] project on branch [yellow]{branch}[/yellow].")
    else:
        console.print(f"You are on branch [yellow]{branch}[/yellow].")

    if most_edited:
        console.print(f"Most of your time was spent editing [white]{most_edited}[/white] ({file_counts[most_edited]} saves).")

    if active_file and active_file != "unknown":
        console.print(f"Your active file right now is [white]{active_file}[/white].")

    if len(errors) == 0:
        console.print(f"[green]No errors this session — clean run.[/green]")
    elif most_errored and error_counts[most_errored] > 1:
        console.print(f"You hit [red]{len(errors)} errors[/red], most from `{most_errored}` ({error_counts[most_errored]}x).")
    else:
        console.print(f"You hit [red]{len(errors)} error(s)[/red] this session.")

    if last_commit and last_commit != "no commits":
        console.print(f"Last commit: [dim]{last_commit.strip()}[/dim]")

    console.print("")

if __name__ == "__main__":
    app()
