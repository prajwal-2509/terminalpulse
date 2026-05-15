from __future__ import annotations
import json, math, time
from pathlib import Path
from typing import Optional
import networkx as nx
from .events import Event, EventType

STATE_FILE = Path.home() / ".devpulse_state.json"
LAMBDA = 0.01          # decay rate (per second). ~0.5 weight after ~70s
PRUNE_BELOW = 0.01     # drop nodes whose weight falls below this
SEVERITY = {
    EventType.COMMAND_FAILED: 1.0,
    EventType.FILE_SAVED: 0.3,
    EventType.FOCUS_CHANGED: 0.1,
    EventType.COMMAND_OK: 0.05,
}


class PulseGraph:
    def __init__(self) -> None:
        self.g = nx.DiGraph()
        self._counter = 0
        self._focus_node: Optional[str] = None

    def _weight(self, ts: float) -> float:
        return math.exp(-LAMBDA * (time.time() - ts))

    def ingest(self, ev: Event) -> None:
        nid = f"{ev.type.value}:{self._counter}"
        self._counter += 1
        self.g.add_node(nid, event=ev.model_dump(), severity=SEVERITY[ev.type])

        # link errors to current focus
        if ev.type == EventType.COMMAND_FAILED and self._focus_node:
            self.g.add_edge(nid, self._focus_node, kind="occurred_while_editing")

        if ev.type == EventType.FOCUS_CHANGED:
            self._focus_node = nid

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
        state = {
            "generated_at": time.time(),
            "hottest": self.hottest(5),
            "node_count": self.g.number_of_nodes(),
        }
        tmp = STATE_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(state, indent=2))
        tmp.replace(STATE_FILE)   # atomic write
