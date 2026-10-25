# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Chris Collins <chris@hitorro.com>

"""amiforge_* MCP tools: drive the AmiForge IDE (AmigaOS 4.1 PPC) from an assistant.

AmiForge has an ARexx port (``AMIFORGE`` by default). These tools send it
commands through the amiga-bridge's AREXXSEND, the same path as
``amiga_arexx_send``:

    assistant -> devbench MCP -> bridge (AREXXSEND) -> ARexx port AMIFORGE -> IDE

The bridge carries an ARexx RESULT as one line (``|`` and newlines become
spaces, RESULT is dropped when RC isn't 0, 8 KB per line), so every command is
wrapped as ``MCP <command>``. AmiForge answers with an envelope

    AF1 <rc> <more> <length> <escaped payload>

which always comes back with ARexx RC 0. ``more`` > 0 means the rest is fetched
with ``MCPMORE``. Text sent to AmiForge is escaped the same way, with spaces as
``\\s`` so every value is one word; long text goes in pieces into a slot
(``MCPBUF``) and is referred to as ``\\@1``. The format is described in
AmiForge's src/ide/McpCmd.h and docs/user-guide.md ("Controlling AmiForge from
an AI assistant").

Every IDE command returns at once; builds and debugger steps are started and
these tools poll ``GETSTATE`` until they finish. Results are JSON strings.
"""

from __future__ import annotations

import asyncio
import functools
import inspect
import json
import re
import time
from typing import Any

from . import mcp_tools as _mt
from .mcp_tools import mcp

DEFAULT_PORT = "AMIFORGE"
DEFAULT_LAUNCH = "DH1:AmiForge/AmiForge"
INLINE_MAX = 2500     # escaped characters of text sent inline; longer goes through MCPBUF
SLOT_CHUNK = 3000     # escaped characters per MCPBUF piece
AREXX_TIMEOUT = 15.0  # the bridge gives up on a reply after 10 s and says so

# one conversation with the IDE at a time: MCPMORE pages and MCPBUF slots are per port
_lock = asyncio.Lock()


class AmiForgeError(Exception):
    """A command failed (rc is AmiForge's return code; 0 = transport problem)."""

    def __init__(self, message: str, rc: int = 10):
        super().__init__(message)
        self.rc = rc


# ─── escaping (mirrors AmiForge's src/ide/McpCmd.cpp) ───

_ESC = {"\\": "\\\\", "\n": "\\n", "\t": "\\t", "\r": "\\r", "|": "\\p", '"': "\\q"}
_UNESC = {"n": "\n", "t": "\t", "r": "\r", "s": " ", "p": "|", "q": '"', "e": "\x1b", "\\": "\\"}


def escape(text: str, spaces: bool = True) -> str:
    """Escape text for AmiForge: printable ASCII only, no spaces (\\s) when `spaces`."""
    out = []
    for ch in text:
        if ch in _ESC:
            out.append(_ESC[ch])
        elif ch == " ":
            out.append("\\s" if spaces else " ")
        else:
            o = ord(ch)
            if o > 0xFF:
                out.append("?")            # AmigaOS text is Latin-1
            elif o < 0x20 or o >= 0x7F:
                out.append(f"\\x{o:02X}")
            else:
                out.append(ch)
    return "".join(out)


def unescape(text: str) -> str:
    out = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c != "\\" or i + 1 >= n:
            out.append(c)
            i += 1
            continue
        nxt = text[i + 1]
        if nxt in _UNESC:
            out.append(_UNESC[nxt])
            i += 2
        elif nxt == "x" and i + 3 < n and _is_hex(text[i + 2:i + 4]):
            out.append(chr(int(text[i + 2:i + 4], 16)))
            i += 4
        else:
            out.append("\\" + nxt)
            i += 2
    return "".join(out)


def _is_hex(s: str) -> bool:
    return len(s) == 2 and all(c in "0123456789abcdefABCDEF" for c in s)


def parse_envelope(line: str) -> tuple[int, int, str]:
    """'AF1 rc more length payload' -> (rc, more, unescaped payload)."""
    if not line.startswith("AF1 "):
        raise AmiForgeError(
            "AmiForge answered without the MCP envelope - this AmiForge is too old "
            f"for the amiforge_ tools (got: {line[:80]!r})", rc=0)
    parts = line[4:].split(" ", 3)
    if len(parts) < 3:
        raise AmiForgeError(f"malformed AmiForge reply: {line[:80]!r}", rc=0)
    rc, more, length = int(parts[0]), int(parts[1]), int(parts[2])
    body = parts[3] if len(parts) > 3 else ""
    if len(body) < length:                 # the transport strips trailing spaces
        body += " " * (length - len(body))
    return rc, more, unescape(body[:length])


def field_unescape(s: str) -> str:
    out = []
    i = 0
    while i < len(s):
        if s[i] == "\\" and i + 1 < len(s):
            out.append({"t": "\t", "n": "\n", "\\": "\\"}.get(s[i + 1], "\\" + s[i + 1]))
            i += 2
        else:
            out.append(s[i])
            i += 1
    return "".join(out)


def records(payload: str) -> list[list[str]]:
    """Tab-separated records, one per line."""
    return [[field_unescape(f) for f in ln.split("\t")] for ln in payload.split("\n") if ln != ""]


def keyvalues(payload: str) -> dict[str, str]:
    d: dict[str, str] = {}
    for ln in payload.split("\n"):
        if "=" in ln:
            k, v = ln.split("=", 1)
            d[k] = v
    return d


def _int(s: str, default: int = 0) -> int:
    try:
        return int(s)
    except (TypeError, ValueError):
        return default


# ─── transport ───

async def _arexx(port: str, command: str, timeout: float = AREXX_TIMEOUT) -> tuple[int, str]:
    """One AREXXSEND round trip. Returns (rc, result) or raises AmiForgeError."""
    try:
        conn, _state, bus = _mt._require_connected()
    except (RuntimeError, AssertionError):
        raise AmiForgeError("the devbench isn't connected to the Amiga bridge "
                            "(start the bridge on the Amiga; check amiga_ping)", rc=0)
    async with bus.subscribe("arexxresult", "err") as queue:
        conn.send({"type": "AREXXSEND", "port": port, "command": command})
        deadline = asyncio.get_event_loop().time() + timeout
        while True:
            remaining = deadline - asyncio.get_event_loop().time()
            if remaining <= 0:
                raise AmiForgeError(
                    "no answer from the bridge in time (is the bridge busy?)", rc=0)
            try:
                evt, data = await asyncio.wait_for(queue.get(), timeout=remaining)
            except asyncio.TimeoutError:
                continue
            if evt == "err":
                if data.get("context") != "AREXX":
                    continue
                msg = data.get("message", "")
                if "not found" in msg or "disappeared" in msg:
                    raise AmiForgeError(
                        f"AmiForge isn't running: there is no ARexx port {port} on the Amiga. "
                        "Start AmiForge there (amiforge_launch), then try again.", rc=0)
                if "timed out" in msg:
                    raise AmiForgeError(
                        "AmiForge didn't answer within 10 s: it is probably showing a window "
                        "or requester of its own (look with amiforge_screenshot and close it), "
                        "or it is busy.", rc=0)
                raise AmiForgeError(f"ARexx: {msg}", rc=0)
            return int(data.get("rc", -1)), data.get("result", "")


async def _call_unlocked(command: str, port: str) -> str:
    rc, result = await _arexx(port, "MCP " + command)
    if rc != 0:
        raise AmiForgeError(
            f"AmiForge rejected the command (ARexx RC {rc}) - is the port {port} an AmiForge "
            "with the MCP commands?", rc=0)
    erc, more, payload = parse_envelope(result)
    parts = [payload]
    while more > 0:
        rc, result = await _arexx(port, "MCPMORE")
        _rc2, more, chunk = parse_envelope(result)
        parts.append(chunk)
    payload = "".join(parts)
    if erc != 0:
        raise AmiForgeError(payload or f"command failed (RC {erc})", rc=erc)
    return payload


_TOKEN = re.compile(r"\\x[0-9A-Fa-f]{2}|\\.|.", re.S)


async def _put_text(text: str, slot: int, port: str) -> str:
    """A value for a text argument: inline, or via MCPBUF slot `slot` when long."""
    esc = escape(text)
    if len(esc) <= INLINE_MAX:
        return esc
    pieces, cur, size = [], [], 0
    for tok in _TOKEN.findall(esc):     # never split an escape sequence
        if size + len(tok) > SLOT_CHUNK:
            pieces.append("".join(cur))
            cur, size = [], 0
        cur.append(tok)
        size += len(tok)
    if cur:
        pieces.append("".join(cur))
    for i, piece in enumerate(pieces):
        await _call_unlocked(f"MCPBUF SLOT={slot}{' CLEAR' if i == 0 else ''} TEXT={piece}", port)
    return f"\\@{slot}"


async def call(command: str, port: str = DEFAULT_PORT) -> str:
    """Send one MCP-wrapped command and return its (unescaped) payload."""
    async with _lock:
        return await _call_unlocked(command, port)


def _tool(fn):
    """Return JSON; turn AmiForgeError into {"ok": false, "error": ...}."""
    @functools.wraps(fn)
    async def wrapper(*args, **kwargs):
        try:
            result = await fn(*args, **kwargs)
            if isinstance(result, dict) and "ok" not in result:
                result = {"ok": True, **result}
            return json.dumps(result, indent=1, ensure_ascii=False)
        except AmiForgeError as e:
            out: dict[str, Any] = {"ok": False, "error": str(e)}
            if e.rc:
                out["rc"] = e.rc
            return json.dumps(out, indent=1, ensure_ascii=False)
    # FastMCP reads the signature: the arguments are fn's, the result is a JSON string
    wrapper.__signature__ = inspect.signature(fn).replace(return_annotation=str)
    wrapper.__annotations__ = {**getattr(fn, "__annotations__", {}), "return": "str"}
    return wrapper


# ─── parsing the IDE's answers ───

def _state(payload: str) -> dict[str, Any]:
    kv = keyvalues(payload)
    st: dict[str, Any] = dict(kv)
    for k in ("line", "col", "documents", "modified", "errors", "warnings", "sessions",
              "stopline", "exitcode", "frame"):
        if k in st:
            st[k] = _int(st[k])
    return st


def _documents(payload: str) -> list[dict[str, Any]]:
    return [{"path": r[0], "modified": r[1] == "1", "current": r[2] == "1",
             "lines": _int(r[3]) if len(r) > 3 else 0} for r in records(payload)]


def _diagnostics(payload: str) -> list[dict[str, Any]]:
    out = []
    for r in records(payload):
        r += [""] * (6 - len(r))
        d: dict[str, Any] = {"kind": r[0], "file": r[1], "line": _int(r[2]), "col": _int(r[3]),
                             "message": r[4]}
        if r[5]:
            d["explanation"] = r[5]
        out.append(d)
    return out


def _vars(payload: str) -> list[dict[str, Any]]:
    out = []
    for r in records(payload):
        r += [""] * (4 - len(r))
        out.append({"name": r[0], "type": r[1], "value": r[2], "has_children": r[3] == "1"})
    return out


def _frames(payload: str) -> list[dict[str, Any]]:
    out = []
    for r in records(payload):
        r += [""] * (6 - len(r))
        out.append({"level": _int(r[0]), "function": r[1], "file": r[2], "line": _int(r[3]),
                    "pc": r[4], "module": r[5]})
    return out


def _breakpoints(payload: str) -> list[dict[str, Any]]:
    out = []
    for r in records(payload):
        r += [""] * (6 - len(r))
        b: dict[str, Any] = {"file": r[0], "line": _int(r[1]), "enabled": r[2] == "1"}
        if r[3]:
            b["condition"] = r[3]
        if r[4]:
            b["hits"] = _int(r[4])
        if r[5]:
            b["address"] = r[5]
        out.append(b)
    return out


def _arg(name: str, value: str) -> str:
    return f"{name}={escape(value)}"


async def _get_state(port: str) -> dict[str, Any]:
    return _state(await _call_unlocked("GETSTATE", port))


async def _wait(port: str, done, timeout: float, interval: float = 0.5) -> dict[str, Any]:
    """Poll GETSTATE until done(state) or timeout. Returns the last state (+ timed_out)."""
    end = time.monotonic() + timeout
    while True:
        async with _lock:
            st = await _get_state(port)
        if done(st):
            return st
        if time.monotonic() >= end:
            st["timed_out"] = True
            return st
        await asyncio.sleep(interval)


async def _source_context(port: str, path: str, line: int, around: int = 2) -> str:
    if not path or line <= 0:
        return ""
    try:
        payload = await _call_unlocked(
            f"READ {_arg('FILE', path)} FROMLINE={max(1, line - around)} TOLINE={line + around}", port)
    except AmiForgeError:
        return ""
    head, _, text = payload.partition("\n")
    h = head.split("\t")
    first = _int(h[1], 1) if len(h) > 1 else 1
    return "\n".join(f"{'>' if first + i == line else ' '}{first + i:5d}| {t}"
                     for i, t in enumerate(text.split("\n")))


async def _debug_summary(port: str, st: dict[str, Any], with_locals: bool = True) -> dict[str, Any]:
    out: dict[str, Any] = {"debug": st.get("debug")}
    for k in ("stopreason", "stopfile", "stopline", "stopfunction", "stoptext", "exitcode", "timed_out"):
        if k in st:
            out[k] = st[k]
    if st.get("debug") == "stopped":
        async with _lock:
            out["source"] = await _source_context(port, st.get("stopfile", ""), st.get("stopline", 0))
            if with_locals:
                try:
                    out["locals"] = _vars(await _call_unlocked("LOCALS", port))
                except AmiForgeError as e:
                    out["locals_error"] = str(e)
            if st.get("stopreason") == "exception":
                try:
                    out["crash"] = await _call_unlocked("CRASH", port)
                except AmiForgeError:
                    pass
    return out


# ─── tools ───

@mcp.tool()
@_tool
async def amiforge_status(port: str = DEFAULT_PORT) -> dict:
    """State of the AmiForge IDE on the Amiga: project, current file and cursor, open files
    (modified or not), build state and result, debugger state (stopped where, why), and
    whether a captured program run is still going. Call this first; it also tells you
    whether AmiForge is running. `port` is AmiForge's ARexx port (default AMIFORGE; a second
    copy started with REXXPORT=name uses that name)."""
    async with _lock:
        st = await _get_state(port)
        docs = _documents(await _call_unlocked("DOCUMENTS", port))
    return {"state": st, "documents": docs}


@mcp.tool()
@_tool
async def amiforge_launch(path: str = DEFAULT_LAUNCH, project: str = "", port: str = DEFAULT_PORT,
                          wait_seconds: float = 30.0) -> dict:
    """Start AmiForge on the Amiga (if its ARexx port isn't there yet) and wait for its port.
    path: the AmiForge program (default DH1:AmiForge/AmiForge). project: an .afp to open at
    start (recommended: without one AmiForge reopens the last project or shows its project
    browser, which doesn't answer ARexx until it is closed). port: a port name other than
    AMIFORGE starts it with REXXPORT=<port>."""
    try:
        async with _lock:
            st = await _get_state(port)
        return {"started": False, "message": f"AmiForge is already running on port {port}", "state": st}
    except AmiForgeError as e:
        if "isn't running" not in str(e):
            raise
    conn, _s, bus = _mt._require_connected()
    q = lambda p: f'"{p}"' if " " in p else p   # the bridge checks the program exists
    cmd = q(path)
    if port != DEFAULT_PORT:
        cmd += f" REXXPORT={port}"
    if project:
        cmd += " " + q(project)
    cmd_id = int(time.time() * 1000) % 100000
    conn.send({"type": "LAUNCH", "id": cmd_id, "command": cmd})
    msg = await bus.wait_for("cmd", timeout=5.0, predicate=lambda d: d.get("id") == cmd_id)
    if msg and msg.get("status") not in ("OK", "ok"):
        raise AmiForgeError(f"couldn't start {path}: {msg.get('data', '')}", rc=0)
    end = time.monotonic() + wait_seconds
    last = ""
    while time.monotonic() < end:
        await asyncio.sleep(1.0)
        try:
            async with _lock:
                st = await _get_state(port)
            return {"started": True, "command": cmd, "state": st}
        except AmiForgeError as e:
            last = str(e)
    raise AmiForgeError(f"started {cmd}, but its ARexx port {port} didn't answer within "
                        f"{wait_seconds:.0f} s ({last})", rc=0)


@mcp.tool()
@_tool
async def amiforge_projects(depth: int = 2, port: str = DEFAULT_PORT) -> dict:
    """The projects in AmiForge's projects folder (name, .afp path, description) and the
    project templates amiforge_new_project can use (id, name, description)."""
    async with _lock:
        st = await _get_state(port)
        projects = [{"name": r[0], "afp": r[1], "description": r[2] if len(r) > 2 else ""}
                    for r in records(await _call_unlocked(f"PROJECTS DEPTH={int(depth)}", port))]
        templates = [{"id": r[0], "name": r[1], "description": r[2] if len(r) > 2 else ""}
                     for r in records(await _call_unlocked("TEMPLATES", port))]
    return {"projects_folder": st.get("projectsfolder", ""), "projects": projects, "templates": templates}


async def _project_info(port: str) -> dict:
    info = keyvalues(await _call_unlocked("PROJECTINFO", port))
    files = [{"path": r[0], "full_path": r[1] if len(r) > 1 else ""}
             for r in records(await _call_unlocked("PROJECTFILES", port))]
    return {"project": info, "files": files}


@mcp.tool()
@_tool
async def amiforge_open_project(path: str, port: str = DEFAULT_PORT) -> dict:
    """Open a project (.afp file, an Amiga path such as DH1:Work/hello/hello.afp). Fails if
    files with unsaved changes would have to be closed: save or revert them first. Returns
    the project's settings and files."""
    async with _lock:
        await _call_unlocked(f"OPENPROJECT {_arg('FILE', path)}", port)
        return await _project_info(port)


@mcp.tool()
@_tool
async def amiforge_new_project(template: str, name: str, drawer: str, port: str = DEFAULT_PORT) -> dict:
    """Create a project from a template (ids from amiforge_projects, e.g. "shell") in
    <drawer>/<name> and open it. name: a C identifier-like name. Returns the new project."""
    async with _lock:
        afp = await _call_unlocked(
            f"NEWPROJECT {_arg('TEMPLATE', template)} {_arg('NAME', name)} {_arg('DRAWER', drawer)}", port)
        info = await _project_info(port)
    return {"afp": afp, **info}


@mcp.tool()
@_tool
async def amiforge_project_info(port: str = DEFAULT_PORT) -> dict:
    """The open project's settings (compiler flags, libraries, output program, arguments,
    stop-at-main...) and its files (relative and full paths)."""
    async with _lock:
        return await _project_info(port)


@mcp.tool()
@_tool
async def amiforge_open_file(path: str, line: int = 0, port: str = DEFAULT_PORT) -> dict:
    """Open a file in the editor (or switch to it) and optionally move the cursor to a line,
    so the user sees what you're looking at. Relative paths are in the project's drawer."""
    cmd = f"ACTIVATE {_arg('FILE', path)}" + (f" LINE={int(line)}" if line > 0 else "")
    async with _lock:
        full = await _call_unlocked(cmd, port)
    return {"path": full}


@mcp.tool()
@_tool
async def amiforge_read_file(path: str = "", from_line: int = 1, to_line: int = 0,
                             numbered: bool = True, port: str = DEFAULT_PORT) -> dict:
    """Read a file as AmiForge sees it: the editor's text when the file is open (including
    unsaved changes), else the file on disk. path: empty = the current file; relative =
    the project's drawer. Lines are 1-based; to_line 0 = the end. With numbered, each line is
    prefixed "  12| " (the prefix is not part of the text)."""
    cmd = "READ" + (f" {_arg('FILE', path)}" if path else "") + f" FROMLINE={max(1, int(from_line))}"
    if to_line > 0:
        cmd += f" TOLINE={int(to_line)}"
    async with _lock:
        payload = await _call_unlocked(cmd, port)
    head, _, text = payload.partition("\n")
    h = head.split("\t")
    total, first, last = _int(h[0]), _int(h[1], 1), _int(h[2])
    name = field_unescape(h[3]) if len(h) > 3 else path
    if numbered and text:
        text = "\n".join(f"{first + i:5d}| {t}" for i, t in enumerate(text.split("\n")))
    return {"path": name, "total_lines": total, "from_line": first, "to_line": last, "text": text}


@mcp.tool()
@_tool
async def amiforge_edit(path: str, old_text: str, new_text: str, replace_all: bool = False,
                        port: str = DEFAULT_PORT) -> dict:
    """Replace exact text in a file, in the editor (the file is opened if needed; the change
    is undoable there and NOT saved - amiforge_save, or a build, saves it). old_text must
    occur exactly once unless replace_all; include enough surrounding text to make it unique.
    Matching is exact and case-sensitive, whitespace included."""
    async with _lock:
        old_v = await _put_text(old_text, 1, port)
        new_v = await _put_text(new_text, 2, port)
        payload = await _call_unlocked(f"SUBST {_arg('FILE', path)} OLD={old_v} NEW={new_v}"
                                       + (" ALL" if replace_all else ""), port)
    r = (records(payload) or [["0", "0"]])[0]
    return {"replacements": _int(r[0]), "first_line": _int(r[1]) if len(r) > 1 else 0}


@mcp.tool()
@_tool
async def amiforge_edit_lines(path: str, from_line: int, to_line: int, text: str,
                              port: str = DEFAULT_PORT) -> dict:
    """Replace whole lines from_line..to_line (1-based, inclusive) of a file with text (any
    number of lines; empty text deletes them). to_line = from_line - 1 inserts before
    from_line; from_line = last line + 1 appends. In the editor, not saved (see amiforge_save).
    Returns the file's new line count."""
    async with _lock:
        v = await _put_text(text, 1, port)
        n = await _call_unlocked(f"EDITLINES {_arg('FILE', path)} FROMLINE={int(from_line)} "
                                 f"TOLINE={int(to_line)} TEXT={v}", port)
    return {"total_lines": _int(n)}


@mcp.tool()
@_tool
async def amiforge_save(port: str = DEFAULT_PORT) -> dict:
    """Save every modified file in AmiForge (untitled files can't be: they need a name)."""
    async with _lock:
        await _call_unlocked("SAVEALL", port)
        docs = _documents(await _call_unlocked("DOCUMENTS", port))
    return {"documents": docs}


@mcp.tool()
@_tool
async def amiforge_revert(path: str = "", port: str = DEFAULT_PORT) -> dict:
    """Throw away a file's unsaved changes: reload it from disk (path empty = current file)."""
    async with _lock:
        await _call_unlocked("REVERT" + (f" {_arg('FILE', path)}" if path else ""), port)
    return {}


async def _errors(port: str, include_all: bool = False) -> list[dict[str, Any]]:
    return _diagnostics(await _call_unlocked("ERRORS" + (" ALL" if include_all else ""), port))


async def _build(port: str, mode: str, wait: bool, timeout: float) -> dict:
    flag = {"build": "", "rebuild": " REBUILD", "clean": " CLEAN"}.get(mode)
    if flag is None:
        raise AmiForgeError("mode is build, rebuild or clean")
    async with _lock:
        await _call_unlocked("STARTBUILD" + flag, port)
    if not wait:
        return {"started": True}
    t0 = time.monotonic()
    st = await _wait(port, lambda s: s.get("build") == "idle", timeout, interval=1.0)
    async with _lock:
        diags = await _errors(port)
        out: dict[str, Any] = {
            "result": "running" if st.get("timed_out") else st.get("buildresult"),
            "errors": st.get("errors", 0), "warnings": st.get("warnings", 0),
            "seconds": round(time.monotonic() - t0, 1), "diagnostics": diags,
        }
        if st.get("buildresult") == "failed" and not any(d["kind"] == "error" for d in diags):
            log = await _call_unlocked("BUILDLOG", port)
            out["log_tail"] = "\n".join(log.rstrip("\n").split("\n")[-30:])
    return out


@mcp.tool()
@_tool
async def amiforge_build(mode: str = "build", wait: bool = True, timeout: float = 600.0,
                         port: str = DEFAULT_PORT) -> dict:
    """Build the open project in AmiForge (with the AmigaOS 4.1 SDK's GCC on the Amiga).
    Saves modified files first, like the Build menu. mode: build, rebuild or clean. With wait,
    returns when it has finished: result (ok/failed), error and warning counts, and the
    diagnostics (kind, file, line, col, message, and AmiForge's Amiga-aware explanation when
    it has one). Builds on the emulated Amiga are slow: a small project takes 10-60 s."""
    return await _build(port, mode, wait, timeout)


@mcp.tool()
@_tool
async def amiforge_errors(include_all: bool = False, port: str = DEFAULT_PORT) -> dict:
    """The last build's errors and warnings (file, line, col, message, explanation). With
    include_all, every build log line (commands, output, notes) too."""
    async with _lock:
        return {"diagnostics": await _errors(port, include_all)}


@mcp.tool()
@_tool
async def amiforge_build_log(tail: int = 200, port: str = DEFAULT_PORT) -> dict:
    """The last build's log as AmiForge shows it (the last `tail` lines; 0 = all)."""
    async with _lock:
        log = await _call_unlocked("BUILDLOG", port)
    lines = log.rstrip("\n").split("\n") if log else []
    if tail > 0:
        lines = lines[-tail:]
    return {"log": "\n".join(lines)}


@mcp.tool()
@_tool
async def amiforge_run(build: bool = True, capture_output: bool = True, wait_seconds: float = 10.0,
                       port: str = DEFAULT_PORT) -> dict:
    """Run the project's program (building it first when `build`). With capture_output, the
    program's output goes to a file (T:AmiForge-mcp-run.txt; input is NIL:) and is returned
    once it ends or after wait_seconds (then it keeps running: amiforge_run_output later,
    amiforge_stop_program to stop it). Without, it runs in its own console window like the
    Run menu, and nothing is returned. Programs that open windows keep running until closed."""
    if build:
        b = await _build(port, "build", True, 600.0)
        if b.get("result") != "ok":
            return {"ok": False, "error": "the build failed", "build": b}
    async with _lock:
        await _call_unlocked("RUNPROGRAM" + (" CAPTURE" if capture_output else ""), port)
    if not capture_output:
        return {"started": True}
    st = await _wait(port, lambda s: s.get("program") != "running", wait_seconds, interval=0.5)
    async with _lock:
        out = await _call_unlocked("RUNOUTPUT", port)
    head, _, text = out.partition("\n")
    return {"running": head.endswith("1"), "output": text}


@mcp.tool()
@_tool
async def amiforge_run_output(port: str = DEFAULT_PORT) -> dict:
    """The output so far of the program started by amiforge_run (capture_output), and
    whether it's still running."""
    async with _lock:
        out = await _call_unlocked("RUNOUTPUT", port)
    head, _, text = out.partition("\n")
    return {"running": head.endswith("1"), "output": text}


@mcp.tool()
@_tool
async def amiforge_stop_program(port: str = DEFAULT_PORT) -> dict:
    """Send Ctrl-C to the program started by amiforge_run (capture_output)."""
    async with _lock:
        await _call_unlocked("STOPPROGRAM", port)
    return {}


_DEBUG_ACTIONS = {"continue": "CONTINUE", "step": "STEP", "next": "NEXT", "step_out": "STEPOUT",
                  "pause": "PAUSE", "stop": "DEBUGSTOP"}


@mcp.tool()
@_tool
async def amiforge_debug(action: str, file: str = "", line: int = 0, stop_at_main: bool | None = None,
                         build: bool = False, wait: bool = True, timeout: float = 30.0,
                         port: str = DEFAULT_PORT) -> dict:
    """Control AmiForge's source-level debugger. action:
      start     - start debugging the built program (build=True builds first); it stops at
                  main if stop_at_main (default: the project's setting) or at a breakpoint
      continue  - run on from a stop
      step      - one source line, into calls
      next      - one source line, over calls
      step_out  - until the current function returns
      run_to    - continue until file:line
      pause     - stop the running program where it is
      stop      - end the session (kills the program)
      state     - just report
    With wait, returns once the program has stopped again or exited (or after timeout s,
    with timed_out): the stop reason, file, line, function, the source around it, the
    locals, and for a crash AmiForge's explanation."""
    action = action.lower()
    if action == "start":
        if build:
            b = await _build(port, "build", True, 600.0)
            if b.get("result") != "ok":
                return {"ok": False, "error": "the build failed", "build": b}
        flag = "" if stop_at_main is None else (" MAIN" if stop_at_main else " NOMAIN")
        async with _lock:
            session = _int(await _call_unlocked("DEBUGSTART" + flag, port))
        if not wait:
            return {"session": session}
        st = await _wait(port, lambda s: s.get("debug") in ("stopped", "none", "exited"), timeout)
        return await _debug_summary(port, st)
    if action == "state":
        async with _lock:
            st = await _get_state(port)
        return await _debug_summary(port, st)
    if action == "run_to":
        if not file or line <= 0:
            raise AmiForgeError("run_to needs file and line")
        cmd = f"RUNTO {_arg('FILE', file)} LINE={int(line)}"
    elif action in _DEBUG_ACTIONS:
        cmd = _DEBUG_ACTIONS[action]
    else:
        raise AmiForgeError(f"unknown action {action!r}: start, continue, step, next, step_out, "
                            "run_to, pause, stop or state")
    async with _lock:
        await _call_unlocked(cmd, port)
    if not wait or action == "stop":
        async with _lock:
            st = await _get_state(port)
        return await _debug_summary(port, st, with_locals=False)
    await asyncio.sleep(0.2)
    st = await _wait(port, lambda s: s.get("debug") in ("stopped", "none", "exited"), timeout)
    return await _debug_summary(port, st)


@mcp.tool()
@_tool
async def amiforge_breakpoint(action: str = "list", file: str = "", line: int = 0, condition: str = "",
                              port: str = DEFAULT_PORT) -> dict:
    """Breakpoints of the open project. action: set (file, line, optional condition - a C
    expression; it stops only when non-zero), clear (file, line), clear_all, list. They work
    before and during debugging; while debugging, set reports the line it really went on (the
    first line with code). Returns the breakpoint list (file, line, enabled, condition, hits)."""
    action = action.lower()
    out: dict[str, Any] = {}
    async with _lock:
        if action == "set":
            if not file or line <= 0:
                raise AmiForgeError("set needs file and line")
            cmd = f"BREAK {_arg('FILE', file)} LINE={int(line)}"
            if condition:
                cmd += f" {_arg('COND', condition)}"
            out["line"] = _int(await _call_unlocked(cmd, port), line)
        elif action == "clear":
            if not file or line <= 0:
                raise AmiForgeError("clear needs file and line")
            await _call_unlocked(f"UNBREAK {_arg('FILE', file)} LINE={int(line)}", port)
        elif action == "clear_all":
            await _call_unlocked("UNBREAK ALL", port)
        elif action != "list":
            raise AmiForgeError(f"unknown action {action!r}: set, clear, clear_all or list")
        out["breakpoints"] = _breakpoints(await _call_unlocked("BREAKS", port))
    return out


@mcp.tool()
@_tool
async def amiforge_locals(port: str = DEFAULT_PORT) -> dict:
    """The parameters and local variables of the selected stack frame (name, type, value,
    has_children) while the program is stopped. Use amiforge_eval for members / pointers."""
    async with _lock:
        return {"locals": _vars(await _call_unlocked("LOCALS", port))}


@mcp.tool()
@_tool
async def amiforge_stack(select_frame: int = -1, port: str = DEFAULT_PORT) -> dict:
    """The call stack while stopped (level, function, file, line, pc, module). select_frame
    >= 0 makes that frame the one amiforge_locals and amiforge_eval look at."""
    async with _lock:
        if select_frame >= 0:
            await _call_unlocked(f"FRAME {int(select_frame)}", port)
        return {"frames": _frames(await _call_unlocked("STACK", port))}


@mcp.tool()
@_tool
async def amiforge_eval(expression: str, children: bool = False, port: str = DEFAULT_PORT) -> dict:
    """Evaluate a C expression in the stopped program (selected frame): variables, members
    (p->next->value, s.field), array elements, casts, arithmetic. With children, the members
    of a struct / elements of an array / the target of a pointer too."""
    cmd = "EVAL" + (" CHILDREN" if children else "") + " " + escape(expression)
    async with _lock:
        vs = _vars(await _call_unlocked(cmd, port))
    if not vs:
        raise AmiForgeError("no value")
    return {"value": vs[0], **({"children": vs[1:]} if children else {})}


@mcp.tool()
@_tool
async def amiforge_registers(port: str = DEFAULT_PORT) -> dict:
    """The PowerPC registers of the stopped program (r0-r31, pc, lr, ctr, msr, cr, xer, dar, dsisr)."""
    async with _lock:
        return {"registers": {r[0]: r[1] for r in records(await _call_unlocked("REGS", port)) if len(r) > 1}}


@mcp.tool()
@_tool
async def amiforge_symbols(path: str = "", port: str = DEFAULT_PORT) -> dict:
    """The outline of a source file (functions, structs, classes, macros, globals, assembler
    labels: kind, name, line, detail). path empty = the current file."""
    async with _lock:
        rs = records(await _call_unlocked("SYMBOLS" + (f" {_arg('FILE', path)}" if path else ""), port))
    return {"symbols": [{"kind": r[0], "name": r[1], "line": _int(r[2]),
                         **({"detail": r[3]} if len(r) > 3 and r[3] else {})} for r in rs]}


@mcp.tool()
@_tool
async def amiforge_references(name: str, port: str = DEFAULT_PORT) -> dict:
    """Every use of an identifier (whole word, outside comments and strings) in the project's
    files and the other open files: file, line, col, and the line's text (up to 500)."""
    async with _lock:
        rs = records(await _call_unlocked(f"REFERENCES {_arg('NAME', name)}", port))
    return {"references": [{"file": r[0], "line": _int(r[1]), "col": _int(r[2]),
                            "text": r[3] if len(r) > 3 else ""} for r in rs]}


@mcp.tool()
@_tool
async def amiforge_git_status(port: str = DEFAULT_PORT) -> dict:
    """Git status of the project's repository as AmiForge's Git tab sees it: the repository,
    the branch, and the changed files with their two-letter status (index, work tree:
    M modified, A added, D deleted, ? untracked)."""
    async with _lock:
        rs = records(await _call_unlocked("GITSTATUS", port))
    head = rs[0] if rs else ["", ""]
    return {"repository": head[0], "branch": head[1] if len(head) > 1 else "",
            "files": [{"status": r[0], "path": r[1] if len(r) > 1 else ""} for r in rs[1:]]}


@mcp.tool()
@_tool
async def amiforge_screenshot(window: str = "") -> dict:
    """A screenshot of the Amiga screen (or of one window, by title) to see AmiForge, the
    running program or a requester. Returns the image file path on the host."""
    result = await _mt.amiga_screenshot(window)
    return {"result": result}


@mcp.tool()
@_tool
async def amiforge_command(command: str, port: str = DEFAULT_PORT) -> dict:
    """Send any AmiForge ARexx command (see HELP; e.g. "GOTO 12", "FIND foo", "HELP EVAL")
    wrapped in MCP, and return its RESULT text. Arguments of the MCP commands take the escaped
    form (\\s for a space); the classic commands (OPEN, INSERT...) take plain text."""
    async with _lock:
        return {"result": await _call_unlocked(command, port)}
