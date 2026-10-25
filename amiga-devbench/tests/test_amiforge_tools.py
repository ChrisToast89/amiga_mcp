# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Chris Collins <chris@hitorro.com>

"""Unit tests for the amiforge_* MCP tools (amiforge_tools.py).

A fake bridge answers AREXXSEND the way the real one does (AREXXRESULT, or
ERR|AREXX for a missing port / a timeout), and a small fake AmiForge behind it
speaks the MCP envelope ("AF1 rc more length payload", MCPMORE paging, MCPBUF
slots) the way src/ide/McpPort.cpp does, with a tiny chunk size so paging is
exercised. No Amiga needed.
"""
import asyncio
import json

from amiga_devbench import amiforge_tools as af
from amiga_devbench import mcp_tools


# ─── the fake IDE ───

def _esc_out(s):
    return af.escape(s, spaces=False)


class FakeAmiForge:
    CHUNK = 40

    def __init__(self):
        self.rest = ""
        self.slots = {}
        self.files = {"DH1:p/main.c": "int main(void)\n{\n    return 0;\n}\n"}
        self.current = "DH1:p/main.c"
        self.build = "idle"
        self.buildresult = "none"
        self.build_polls = 0
        self.debug = "none"
        self.debug_polls = 0
        self.breaks = []
        self.log = []          # commands received (inner, after MCP)

    # envelope like mcp::envelope / mcp::nextChunk
    def _wrap(self, rc, chunk):
        return f"AF1 {rc} {len(self.rest)} {len(chunk)} {chunk}"

    def _cut(self, esc):
        toks = af._TOKEN.findall(esc)
        out, n = [], 0
        for t in toks:
            if n + len(t) > self.CHUNK:
                break
            out.append(t)
            n += len(t)
        return n

    def envelope(self, rc, payload):
        esc = _esc_out(payload)
        n = self._cut(esc)
        self.rest = esc[n:]
        return self._wrap(rc, esc[:n])

    def more(self):
        n = self._cut(self.rest)
        chunk, self.rest = self.rest[:n], self.rest[n:]
        return self._wrap(0, chunk)

    def arexx(self, command):
        """(rc, result) for one ARexx command."""
        word, _, rest = command.partition(" ")
        if word == "MCPMORE":
            return 0, self.more()
        if word != "MCP":
            return 0, "classic"
        self.log.append(rest)
        try:
            payload = self.run(rest)
            return 0, self.envelope(0, payload)
        except LookupError as e:
            return 0, self.envelope(10, str(e))

    @staticmethod
    def _args(rest):
        out = {}
        for w in rest.split():
            k, eq, v = w.partition("=")
            out[k.upper()] = v if eq else "1"
        return out

    def _text(self, v):
        if len(v) == 3 and v.startswith("\\@"):
            return self.slots[int(v[2])]
        return af.unescape(v)

    def run(self, line):
        cmd, _, rest = line.partition(" ")
        a = self._args(rest)
        if cmd == "MCPBUF":
            slot = int(a["SLOT"])
            if "CLEAR" in a:
                self.slots[slot] = ""
            self.slots[slot] = self.slots.get(slot, "") + af.unescape(a.get("TEXT", ""))
            return str(len(self.slots[slot]))
        if cmd == "GETSTATE":
            if self.build == "running":
                self.build_polls += 1
                if self.build_polls >= 2:
                    self.build, self.buildresult = "idle", "failed"
            if self.debug == "running":
                self.debug_polls += 1
                if self.debug_polls >= 2:
                    self.debug = "stopped"
            lines = ["port=AMIFORGE", "project=DH1:p/p.afp", f"file={self.current}", "line=3", "col=5",
                     "documents=1", "modified=0", f"build={self.build}", f"buildresult={self.buildresult}",
                     "errors=1", "warnings=0", f"debug={self.debug}", "sessions=1", "program=idle"]
            if self.debug == "stopped":
                lines += ["stopreason=breakpoint", f"stopfile={self.current}", "stopline=3",
                          "stopfunction=main", "stoptext=Breakpoint 1, main() at main.c:3"]
            return "\n".join(lines) + "\n"
        if cmd == "DOCUMENTS":
            return "DH1:p/main.c\t0\t1\t5\n"
        if cmd == "READ":
            path = af.unescape(a.get("FILE", self.current))
            if path not in self.files:
                raise LookupError("can't read " + path)
            t = self.files[path]
            ls = t.split("\n")
            fr, to = int(a.get("FROMLINE", 1)), int(a.get("TOLINE", len(ls)))
            return f"{len(ls)}\t{fr}\t{to}\t{path}\n" + "\n".join(ls[fr - 1:to])
        if cmd == "SUBST":
            path = af.unescape(a.get("FILE", self.current))
            old, new = self._text(a["OLD"]), self._text(a.get("NEW", ""))
            t = self.files[path]
            n = t.count(old)
            if n == 0:
                raise LookupError("the text to replace isn't in the file")
            if n > 1 and "ALL" not in a:
                raise LookupError(f"the text to replace is in the file {n} times")
            line = t[:t.index(old)].count("\n") + 1
            self.files[path] = t.replace(old, new)
            return f"{n}\t{line}"
        if cmd == "STARTBUILD":
            self.build, self.build_polls = "running", 0
            return ""
        if cmd == "ERRORS":
            return "error\tDH1:p/main.c\t3\t5\t'x' undeclared\tExplain\\nmore\n"
        if cmd == "DEBUGSTART":
            self.debug, self.debug_polls = "running", 0
            return "1"
        if cmd == "CONTINUE":
            if self.debug != "stopped":
                raise LookupError("not debugging (DEBUGSTART first)")
            self.debug, self.debug_polls = "running", 0
            return ""
        if cmd == "LOCALS":
            return "argc\tint\t1\t0\np\tstruct node *\t0x01234560\t1\n"
        if cmd == "BREAK":
            self.breaks.append((af.unescape(a["FILE"]), int(a["LINE"]), af.unescape(a.get("COND", ""))))
            return a["LINE"]
        if cmd == "BREAKS":
            return "".join(f"{f}\t{ln}\t1\t{c}\t\t\n" for f, ln, c in self.breaks)
        if cmd == "EVAL":
            return "p->x\tint\t42\t0\n"
        raise LookupError("unknown " + cmd)


# ─── the fake bridge ───

class FakeBus:
    def __init__(self):
        self.q = None

    def subscribe(self, *events):
        bus = self

        class _CM:
            async def __aenter__(self):
                bus.q = asyncio.Queue()
                return bus.q

            async def __aexit__(self, *a):
                bus.q = None
                return False

        return _CM()

    async def wait_for(self, event, timeout=5.0, predicate=None):
        return None


class FakeConn:
    def __init__(self, bus, ide, ports=("AMIFORGE",)):
        self.bus, self.ide, self.ports = bus, ide, set(ports)
        self.connected = True
        self.sent = []

    def send(self, msg):
        self.sent.append(msg)
        if msg["type"] != "AREXXSEND":
            return
        if msg["port"] not in self.ports:
            ev = ("err", {"context": "AREXX", "message": f"Port '{msg['port']}' not found"})
        else:
            rc, result = self.ide.arexx(msg["command"])
            # the real bridge sanitises the line and the host strips it
            assert "|" not in result and "\n" not in result, result
            ev = ("arexxresult", {"rc": rc, "result": result.strip()})
        asyncio.get_event_loop().call_soon(lambda: self.bus.q and self.bus.q.put_nowait(ev))


def _setup(**kw):
    bus = FakeBus()
    ide = FakeAmiForge()
    conn = FakeConn(bus, ide, **kw)
    mcp_tools._conn, mcp_tools._state, mcp_tools._event_bus = conn, object(), bus
    return ide, conn


def _run(coro):
    return json.loads(asyncio.run(coro))


# ─── tests ───

def test_escape_roundtrip():
    s = 'a b\tc\nd|e"f\\g\x01\xe9'
    e = af.escape(s)
    assert " " not in e and all(0x20 <= ord(c) < 0x7F for c in e)
    assert af.unescape(e) == s
    assert af.escape("x y", spaces=False) == "x y"
    assert af.escape("€") == "?"           # not Latin-1
    assert af.unescape("\\z") == "\\z"


def test_parse_envelope_restores_trailing_spaces():
    rc, more, p = af.parse_envelope("AF1 0 0 4 x")   # "x   " with the spaces stripped
    assert (rc, more, p) == (0, 0, "x   ")
    rc, more, p = af.parse_envelope("AF1 10 0 10 no\\sproject".replace("\\s", " "))
    assert rc == 10 and p == "no project"
    try:
        af.parse_envelope("[OK] hello")
        assert False
    except af.AmiForgeError as e:
        assert "too old" in str(e)


def test_records_and_keyvalues():
    assert af.records("a\tb\\tc\td\\ne\n\nx\n") == [["a", "b\tc", "d\ne"], ["x"]]
    assert af.keyvalues("a=1\nb=x=y\nnoeq\n") == {"a": "1", "b": "x=y"}


def test_status_pages_long_results():
    ide, conn = _setup()
    r = _run(af.amiforge_status())
    assert r["ok"] is True
    assert r["state"]["project"] == "DH1:p/p.afp"
    assert r["state"]["line"] == 3 and r["state"]["errors"] == 1
    assert r["documents"] == [{"path": "DH1:p/main.c", "modified": False, "current": True, "lines": 5}]
    # GETSTATE is longer than the fake's 40-character chunks: MCPMORE was used
    assert any(m["command"] == "MCPMORE" for m in conn.sent)


def test_not_running_is_a_clear_error():
    _setup(ports=())
    r = _run(af.amiforge_status())
    assert r["ok"] is False
    assert "isn't running" in r["error"] and "amiforge_launch" in r["error"]


def test_read_file_numbers_lines():
    _setup()
    r = _run(af.amiforge_read_file("DH1:p/main.c", 2, 3))
    assert r["total_lines"] == 5 and r["from_line"] == 2
    assert r["text"] == "    2| {\n    3|     return 0;"
    r = _run(af.amiforge_read_file("DH1:p/nope.c"))
    assert r["ok"] is False and "can't read" in r["error"] and r["rc"] == 10


def test_edit_short_and_long_text():
    ide, conn = _setup()
    r = _run(af.amiforge_edit("DH1:p/main.c", "return 0;", "return x;"))
    assert r == {"ok": True, "replacements": 1, "first_line": 3}
    assert "return x;" in ide.files["DH1:p/main.c"]
    # inline: the values went in the command as single words
    subst = [c for c in ide.log if c.startswith("SUBST")][0]
    assert "OLD=return\\s0;" in subst
    # long replacement text goes through MCPBUF slot 2 in pieces
    big = "\n".join(f'    printf("line %ld\\n", (long){i}); | "quoted"' for i in range(200))
    r = _run(af.amiforge_edit("DH1:p/main.c", "return x;", big))
    assert r["ok"] is True
    assert big in ide.files["DH1:p/main.c"]
    bufs = [c for c in ide.log if c.startswith("MCPBUF SLOT=2")]
    assert len(bufs) > 1 and "CLEAR" in bufs[0] and "CLEAR" not in bufs[1]
    assert all(len(c) < 8000 for c in ide.log)


def test_edit_ambiguous_reports_the_ide_error():
    ide, _ = _setup()
    ide.files["DH1:p/main.c"] = "x = 1; x = 1;"
    r = _run(af.amiforge_edit("DH1:p/main.c", "x = 1;", "y"))
    assert r["ok"] is False and "2 times" in r["error"]


def test_build_waits_and_returns_diagnostics():
    _setup()
    orig = af.asyncio.sleep

    async def fast(_t):
        await orig(0)
    af.asyncio.sleep = fast
    try:
        r = _run(af.amiforge_build())
    finally:
        af.asyncio.sleep = orig
    assert r["result"] == "failed" and r["errors"] == 1
    d = r["diagnostics"][0]
    assert d == {"kind": "error", "file": "DH1:p/main.c", "line": 3, "col": 5,
                 "message": "'x' undeclared", "explanation": "Explain\nmore"}
    r = _run(af.amiforge_build(mode="nonsense"))
    assert r["ok"] is False


def test_debug_start_waits_for_the_stop():
    ide, _ = _setup()
    orig = af.asyncio.sleep

    async def fast(_t):
        await orig(0)
    af.asyncio.sleep = fast
    try:
        r = _run(af.amiforge_debug("start", stop_at_main=True))
        assert r["debug"] == "stopped" and r["stopreason"] == "breakpoint"
        assert r["stopline"] == 3 and r["stopfunction"] == "main"
        assert r["locals"][1] == {"name": "p", "type": "struct node *", "value": "0x01234560", "has_children": True}
        assert ">    3|     return 0;" in r["source"]
        assert "DEBUGSTART MAIN" in ide.log
        r = _run(af.amiforge_debug("continue"))
        assert r["debug"] == "stopped"
        ide.debug = "none"
        r = _run(af.amiforge_debug("continue"))
        assert r["ok"] is False and "DEBUGSTART" in r["error"]
        r = _run(af.amiforge_debug("fly"))
        assert r["ok"] is False
    finally:
        af.asyncio.sleep = orig


def test_breakpoints_and_eval():
    ide, _ = _setup()
    r = _run(af.amiforge_breakpoint("set", "main.c", 3, "i == 2"))
    assert r["line"] == 3
    assert r["breakpoints"] == [{"file": "main.c", "line": 3, "enabled": True, "condition": "i == 2"}]
    assert any("COND=i\\s==\\s2" in c for c in ide.log)
    r = _run(af.amiforge_breakpoint("set"))
    assert r["ok"] is False
    r = _run(af.amiforge_eval("p->x"))
    assert r["value"]["value"] == "42"


def test_tools_are_registered_with_json_results():
    tools = {t.name: t for t in asyncio.run(mcp_tools.mcp.list_tools())}
    for name in ("amiforge_status", "amiforge_build", "amiforge_edit", "amiforge_debug",
                 "amiforge_breakpoint", "amiforge_locals", "amiforge_eval", "amiforge_launch"):
        assert name in tools, name
    assert set(tools["amiforge_edit"].inputSchema["properties"]) == {"path", "old_text", "new_text",
                                                                    "replace_all", "port"}
