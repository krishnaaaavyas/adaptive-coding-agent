"""Audit-hook guard for candidate-blind test commands (opt-in pytest plugin).

Blocks real repository historical/evaluator reads and real network access.
Synthetic tmp_path experiments/results are allowed. No fixture is inspected.
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
BLOCKED = ("experiments", "results", "memory", "rules", "rubrics", "workspaces",
           "benchmark_design/discovery", "harness/scorers/fixtures")


def guard(event, arguments):
    if event == "socket.connect":
        # Windows asyncio creates a loopback socketpair as its internal wakeup
        # pipe. Permit only that stdlib call chain, never HTTP/model sockets.
        frame = sys._getframe(1)
        while frame:
            if frame.f_code.co_name == "socketpair" and frame.f_globals.get("__name__") == "socket":
                return
            frame = frame.f_back
        raise RuntimeError("Candidate-blind tests prohibit real network/model connections")
    if event not in ("open", "os.listdir", "os.scandir") or not arguments:
        return
    raw = arguments[0]
    if not isinstance(raw, (str, bytes)):
        return
    candidate = Path(raw.decode() if isinstance(raw, bytes) else raw)
    if not candidate.is_absolute():
        candidate = Path.cwd() / candidate
    # Lexical normalization avoids recursive resolve/audit calls.
    import os
    candidate = Path(os.path.abspath(candidate))
    try:
        relative = candidate.relative_to(ROOT).as_posix().casefold()
    except ValueError:
        return
    if any(relative == name or relative.startswith(name + "/") for name in BLOCKED):
        raise RuntimeError("Forbidden real artifact access in candidate-blind tests")


sys.addaudithook(guard)
