import os, sys, json
from pathlib import Path
import typer, asyncio
from rich import print
from . import daemon as _daemon

app = typer.Typer(help="TerminalPulse — short-term memory for AI agents")
STATE_FILE = Path.home() / ".devpulse_state.json"


@app.command()
def start(watch: str = typer.Option(".", help="Directory to watch")):
    """Run the pulse daemon in the foreground (use nohup/systemd for background)."""
    asyncio.run(_daemon.main(os.path.abspath(watch)))


@app.command()
def state():
    """Print the current hottest context."""
    if not STATE_FILE.exists():
        print("[yellow]No state yet. Is the daemon running?[/]"); raise typer.Exit(1)
    print(json.loads(STATE_FILE.read_text()))


if __name__ == "__main__":
    app()
