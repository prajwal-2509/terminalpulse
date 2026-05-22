from __future__ import annotations
import asyncio, json, os, signal
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .events import Event, EventType
from .graph import PulseGraph

SOCK_PATH = Path.home() / ".terminalpulse.sock"
WATCH_EXTS = {".py", ".js", ".ts", ".tsx", ".jsx", ".rs", ".go", ".md", ".toml", ".json", ".java", ".cpp", ".c", ".rb", ".php", ".css", ".html", ".vue", ".svelte"}

IGNORE_DIRS = {"node_modules", ".git", "__pycache__", "dist", "build", ".venv", "venv", ".next", "target", ".gradle", "vendor"}


class FsHandler(FileSystemEventHandler):
    def __init__(self, queue: asyncio.Queue, loop: asyncio.AbstractEventLoop):
        self.queue = queue
        self.loop = loop

    def on_modified(self, event):
        if event.is_directory: return
        p = Path(event.src_path)
        # ignore files inside ignored directories
        if any(part in IGNORE_DIRS for part in p.parts):
            return
        if p.suffix not in WATCH_EXTS: return
        ev = Event(type=EventType.FILE_SAVED, path=str(p), cwd=os.getcwd())
        self.loop.call_soon_threadsafe(self.queue.put_nowait, ev)

class FsHandler(FileSystemEventHandler):
    def __init__(self, queue: asyncio.Queue, loop: asyncio.AbstractEventLoop):
        self.queue = queue
        self.loop = loop

    def on_modified(self, event):
        if event.is_directory: return
        p = Path(event.src_path)
        if p.suffix not in WATCH_EXTS: return
        ev = Event(type=EventType.FILE_SAVED, path=str(p), cwd=os.getcwd())
        self.loop.call_soon_threadsafe(self.queue.put_nowait, ev)


async def handle_shell_client(reader, writer, queue: asyncio.Queue):
    data = await reader.readline()
    try:
        payload = json.loads(data)
        ev = Event(**payload)
        await queue.put(ev)
    except Exception as e:
        print(f"bad payload: {e}")
    writer.close()


async def handle_http_client(reader, writer, queue: asyncio.Queue):
    data = b""
    while True:
        chunk = await reader.read(1024)
        if not chunk:
            break
        data += chunk
        if b"\r\n\r\n" in data:
            break
    try:
        body = data.split(b"\r\n\r\n", 1)[1]
        payload = json.loads(body)
        ev = Event(**payload)
        await queue.put(ev)
        writer.write(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nOK")
    except Exception as e:
        print(f"bad http payload: {e}")
        writer.write(b"HTTP/1.1 400 Bad Request\r\nContent-Length: 2\r\n\r\nER")
    await writer.drain()
    writer.close()


async def consumer(queue: asyncio.Queue, graph: PulseGraph):
    while True:
        ev = await queue.get()
        graph.ingest(ev)
        print(f"⚡ {ev.type.value}  {ev.path or ev.cmd or ''}")


async def main(watch_dir: str):
    queue: asyncio.Queue = asyncio.Queue()
    graph = PulseGraph()
    loop = asyncio.get_running_loop()

    obs = Observer()
    obs.schedule(FsHandler(queue, loop), watch_dir, recursive=True)
    obs.start()

    if SOCK_PATH.exists(): SOCK_PATH.unlink()
    server = await asyncio.start_unix_server(
        lambda r, w: handle_shell_client(r, w, queue), path=str(SOCK_PATH)
    )
    os.chmod(SOCK_PATH, 0o600)

    http_server = await asyncio.start_server(
        lambda r, w: handle_http_client(r, w, queue),
        "0.0.0.0", 7077
    )

    print(f"🧠 pulsed listening on {SOCK_PATH}, watching {watch_dir}")
    print(f"🌐 HTTP endpoint on port 7077 for Windows bridge")
    try:
        await asyncio.gather(
            server.serve_forever(),
            http_server.serve_forever(),
            consumer(queue, graph)
        )
    finally:
        obs.stop(); obs.join()
        if SOCK_PATH.exists(): SOCK_PATH.unlink()
