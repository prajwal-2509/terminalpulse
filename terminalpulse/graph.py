from __future__ import annotations
import json, math, time, subprocess
from pathlib import Path
from typing import Optional
import networkx as nx
from .events import Event, EventType

STATE_FILE = Path.home() / ".devpulse_state.json"
LAMBDA = 0.01
PRUNE_BELOW = 0.01
SEVERITY = {
    EventType.COMMAND_FAILED: 1.0,
    EventType.FILE_SAVED: 0.3,
    EventType.FOCUS_CHANGED: 0.1,
    EventType.COMMAND_OK: 0.05,
}


def get_git_context() -> dict:
    def run(cmd):
        try:
            return subprocess.check_output(
                cmd, shell=True, stderr=subprocess.DEVNULL
            ).decode().strip()
        except:
            return None
    return {
        "branch": run("git branch --show-current"),
        "last_commit": run("git log -1 --pretty=%B"),
        "changed_files": run("git diff --name-only HEAD"),
        "staged_files": run("git diff --name-only --cached"),
    }


def detect_language(path: Optional[str]) -> Optional[str]:
    if not path:
        return None
    ext = Path(path).suffix
    mapping = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".jsx": "javascript",
        ".rs": "rust",
        ".go": "go",
        ".java": "java",
        ".cpp": "cpp",
        ".c": "c",
        ".rb": "ruby",
        ".php": "php",
    }
    return mapping.get(ext, "unknown")


def detect_project_type(cwd: Optional[str]) -> str:
    if not cwd:
        return "unknown"
    p = Path(cwd)
    if (p / "package.json").exists():
        pkg = json.loads((p / "package.json").read_text())
        deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
        if "react" in deps and "typescript" in deps:
            return "react-typescript"
        if "react" in deps:
            return "react"
        if "next" in deps:
            return "nextjs"
        return "node"
    if (p / "pyproject.toml").exists() or (p / "requirements.txt").exists():
        return "python"
    if (p / "Cargo.toml").exists():
        return "rust"
    if (p / "go.mod").exists():
        return "go"
    return "unknown"


class PulseGraph:
    def __init__(self) -> None:
        self.g = nx.DiGraph()
        self._counter = 0
        self._focus_node: Optional[str] = None
        self._history: list[dict] = []

    def _weight(self, ts: float) -> float:
        return math.exp(-LAMBDA * (time.time() - ts))

    def ingest(self, ev: Event) -> None:
        nid = f"{ev.type.value}:{self._counter}"
        self._counter += 1
        self.g.add_node(nid, event=ev.model_dump(), severity=SEVERITY[ev.type])

        if ev.type == EventType.COMMAND_FAILED and self._focus_node:
            self.g.add_edge(nid, self._focus_node, kind="occurred_while_editing")

        if ev.type == EventType.FOCUS_CHANGED:
            self._focus_node = nid

        # keep history for pulse history command
        self._history.append({
            "ts": ev.ts,
            "type": ev.type.value,
            "detail": ev.path or ev.cmd or "",
            "language": detect_language(ev.path or ev.cmd),
        })
        if len(self._history) > 200:
            self._history = self._history[-200:]

        self._prune()
        self.export()

    def _prune(self) -> None:
        dead = [n for n, d in self.g.nodes(data=True)
                if self._weight(d["event"]["ts"]) < PRUNE_BELOW]
        self.g.remove_nodes_from(dead)
        if self._focus_node not in self.g:
            self._focus_node = None

    def hottest(self, k: int = 5) -> list[dict]:
        scored = []
        for n, d in self.g.nodes(data=True):
            heat = self._weight(d["event"]["ts"]) * d["severity"]
            scored.append((heat, d["event"]))
        scored.sort(key=lambda x: -x[0])
        return [{"heat": round(h, 4), **e} for h, e in scored[:k]]

    def export(self) -> None:
        focus_event = None
        if self._focus_node and self._focus_node in self.g:
            focus_event = self.g.nodes[self._focus_node]["event"]

        cwd = focus_event.get("cwd") if focus_event else None

        state = {
            "generated_at": time.time(),
            "hottest": self.hottest(5),
            "node_count": self.g.number_of_nodes(),
            "git": get_git_context(),
            "project_type": detect_project_type(cwd),
            "active_file": focus_event.get("path") if focus_event else None,
            "active_language": detect_language(
                focus_event.get("path") if focus_event else None
            ),
            "history": self._history[-30:],
        }
        tmp = STATE_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(state, indent=2))
        tmp.replace(STATE_FILE)
