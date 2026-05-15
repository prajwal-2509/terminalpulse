from __future__ import annotations
import time
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class EventType(str, Enum):
    FILE_SAVED = "file_saved"
    COMMAND_FAILED = "command_failed"
    COMMAND_OK = "command_ok"
    FOCUS_CHANGED = "focus_changed"


class Event(BaseModel):
    type: EventType
    ts: float = Field(default_factory=time.time)
    cwd: Optional[str] = None
    # type-specific:
    path: Optional[str] = None          # FILE_SAVED, FOCUS_CHANGED
    cmd: Optional[str] = None           # COMMAND_*
    exit_code: Optional[int] = None     # COMMAND_*
    stderr_tail: Optional[str] = None   # COMMAND_FAILED
