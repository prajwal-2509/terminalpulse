import json
import time
import pytest
from pathlib import Path
from terminalpulse.events import Event, EventType
from terminalpulse.graph import PulseGraph, detect_language, detect_project_type


# ── Event model tests ──────────────────────────────────────────────────────

def test_event_command_failed():
    ev = Event(type=EventType.COMMAND_FAILED, cmd="python3 app.py", exit_code=1, cwd="/tmp")
    assert ev.type == EventType.COMMAND_FAILED
    assert ev.cmd == "python3 app.py"
    assert ev.exit_code == 1

def test_event_file_saved():
    ev = Event(type=EventType.FILE_SAVED, path="/tmp/app.py", cwd="/tmp")
    assert ev.type == EventType.FILE_SAVED
    assert ev.path == "/tmp/app.py"

def test_event_focus_changed():
    ev = Event(type=EventType.FOCUS_CHANGED, path="auth.ts", cwd="")
    assert ev.type == EventType.FOCUS_CHANGED

def test_event_has_timestamp():
    ev = Event(type=EventType.COMMAND_OK)
    assert ev.ts > 0
    assert ev.ts <= time.time()


# ── Language detection tests ───────────────────────────────────────────────

def test_detect_python():
    assert detect_language("/home/user/app.py") == "python"

def test_detect_typescript():
    assert detect_language("/home/user/auth.ts") == "typescript"

def test_detect_tsx():
    assert detect_language("/home/user/App.tsx") == "typescript"

def test_detect_javascript():
    assert detect_language("/home/user/index.js") == "javascript"

def test_detect_rust():
    assert detect_language("/home/user/main.rs") == "rust"

def test_detect_go():
    assert detect_language("/home/user/main.go") == "go"

def test_detect_unknown():
    assert detect_language("/home/user/file.xyz") == "unknown"

def test_detect_none():
    assert detect_language(None) is None


# ── Project type detection tests ───────────────────────────────────────────

def test_detect_python_project(tmp_path):
    (tmp_path / "pyproject.toml").write_text("[project]\nname='test'")
    assert detect_project_type(str(tmp_path)) == "python"

def test_detect_python_requirements(tmp_path):
    (tmp_path / "requirements.txt").write_text("flask\nrequests")
    assert detect_project_type(str(tmp_path)) == "python"

def test_detect_react_typescript(tmp_path):
    pkg = {"dependencies": {"react": "^18", "typescript": "^5"}}
    (tmp_path / "package.json").write_text(json.dumps(pkg))
    assert detect_project_type(str(tmp_path)) == "react-typescript"

def test_detect_nextjs(tmp_path):
    pkg = {"dependencies": {"next": "^14"}}
    (tmp_path / "package.json").write_text(json.dumps(pkg))
    assert detect_project_type(str(tmp_path)) == "nextjs"

def test_detect_node(tmp_path):
    pkg = {"dependencies": {"express": "^4"}}
    (tmp_path / "package.json").write_text(json.dumps(pkg))
    assert detect_project_type(str(tmp_path)) == "node"

def test_detect_rust_project(tmp_path):
    (tmp_path / "Cargo.toml").write_text("[package]\nname='test'")
    assert detect_project_type(str(tmp_path)) == "rust"

def test_detect_go_project(tmp_path):
    (tmp_path / "go.mod").write_text("module test")
    assert detect_project_type(str(tmp_path)) == "go"

def test_detect_unknown_project(tmp_path):
    assert detect_project_type(str(tmp_path)) == "unknown"


# ── PulseGraph tests ───────────────────────────────────────────────────────

def test_graph_ingest_error():
    g = PulseGraph()
    ev = Event(type=EventType.COMMAND_FAILED, cmd="python3 app.py", exit_code=1, cwd="/tmp")
    g.ingest(ev)
    assert g.g.number_of_nodes() == 1

def test_graph_ingest_file_saved():
    g = PulseGraph()
    ev = Event(type=EventType.FILE_SAVED, path="/tmp/app.py", cwd="/tmp")
    g.ingest(ev)
    assert g.g.number_of_nodes() == 1

def test_graph_hottest_returns_list():
    g = PulseGraph()
    ev = Event(type=EventType.COMMAND_FAILED, cmd="python3 app.py", exit_code=1, cwd="/tmp")
    g.ingest(ev)
    hottest = g.hottest(5)
    assert isinstance(hottest, list)
    assert len(hottest) == 1

def test_graph_heat_score():
    g = PulseGraph()
    ev = Event(type=EventType.COMMAND_FAILED, cmd="python3 app.py", exit_code=1, cwd="/tmp")
    g.ingest(ev)
    hottest = g.hottest(1)
    assert hottest[0]["heat"] > 0
    assert hottest[0]["heat"] <= 1.0

def test_graph_error_links_to_focus():
    g = PulseGraph()
    focus = Event(type=EventType.FOCUS_CHANGED, path="app.py", cwd="/tmp")
    g.ingest(focus)
    error = Event(type=EventType.COMMAND_FAILED, cmd="python3 app.py", exit_code=1, cwd="/tmp")
    g.ingest(error)
    assert g.g.number_of_edges() == 1

def test_graph_multiple_events():
    g = PulseGraph()
    for i in range(5):
        ev = Event(type=EventType.FILE_SAVED, path=f"/tmp/file{i}.py", cwd="/tmp")
        g.ingest(ev)
    assert g.g.number_of_nodes() == 5

def test_graph_hottest_sorted_by_heat():
    g = PulseGraph()
    ev1 = Event(type=EventType.FILE_SAVED, path="/tmp/a.py", cwd="/tmp")
    g.ingest(ev1)
    time.sleep(0.1)
    ev2 = Event(type=EventType.COMMAND_FAILED, cmd="python3 a.py", exit_code=1, cwd="/tmp")
    g.ingest(ev2)
    hottest = g.hottest(2)
    assert hottest[0]["heat"] >= hottest[1]["heat"]

def test_graph_exports_state(tmp_path):
    import terminalpulse.graph as gmod
    original = gmod.STATE_FILE
    gmod.STATE_FILE = tmp_path / "state.json"
    g = PulseGraph()
    ev = Event(type=EventType.FILE_SAVED, path="/tmp/app.py", cwd="/tmp")
    g.ingest(ev)
    assert (tmp_path / "state.json").exists()
    state = json.loads((tmp_path / "state.json").read_text())
    assert "hottest" in state
    assert "node_count" in state
    gmod.STATE_FILE = original

def test_graph_history_recorded():
    g = PulseGraph()
    ev = Event(type=EventType.FILE_SAVED, path="/tmp/app.py", cwd="/tmp")
    g.ingest(ev)
    assert len(g._history) == 1
    assert g._history[0]["type"] == "file_saved"
