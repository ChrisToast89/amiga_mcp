#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Chris Collins <chris@hitorro.com>
"""End-to-end check of a running devbench and the Amiga behind it.

Drives the devbench MCP endpoint (the same path Claude Code uses) through a
round trip with a real bridge client: system queries, a file transfer,
launching hello_world, reading and writing its variables, a screenshot, then
stopping it with amiga_stop_client. Works for both targets; the architecture
comes from the Amiga's own sysinfo.

Usage:
  scripts/live-test.py                  # AmigaOS 4 devbench on :3000
  scripts/live-test.py --port 3001      # classic 68k devbench on :3001
  scripts/live-test.py --binary PATH    # hello_world built for that target

Needs the devbench and emulator up (scripts/start.sh) and a hello_world built
for the target's architecture (examples/hello_world/hello_world by default;
the tree holds one architecture at a time, so pass --binary for the other).
Exits 0 when every check passes.
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.request

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REMOTE = "RAM:devbench_live_test"
CLIENT = "hello_world"


class Mcp:
    def __init__(self, url):
        self.url = url
        self.session = None
        self.next_id = 1

    def _post(self, body):
        headers = {"Content-Type": "application/json",
                   "Accept": "application/json, text/event-stream"}
        if self.session:
            headers["mcp-session-id"] = self.session
        req = urllib.request.Request(self.url, json.dumps(body).encode(), headers)
        with urllib.request.urlopen(req, timeout=120) as resp:
            self.session = resp.headers.get("mcp-session-id") or self.session
            text = resp.read().decode()
        for line in text.splitlines():
            if line.startswith("data:"):
                return json.loads(line[5:])
        return json.loads(text) if text.strip() else None

    def rpc(self, method, params=None):
        self.next_id += 1
        return self._post({"jsonrpc": "2.0", "id": self.next_id,
                           "method": method, "params": params or {}})

    def start(self):
        self.rpc("initialize", {"protocolVersion": "2025-03-26", "capabilities": {},
                                "clientInfo": {"name": "live-test", "version": "1"}})
        self._post({"jsonrpc": "2.0", "method": "notifications/initialized"})

    def call(self, tool, **args):
        res = self.rpc("tools/call", {"name": tool, "arguments": args})
        result = res.get("result", {})
        text = "".join(c.get("text", "") for c in result.get("content", []))
        if result.get("isError") or "error" in res:
            raise RuntimeError(text or str(res.get("error")))
        return text


def has_client(clients_text, name):
    """True when amiga_list_clients output ("Clients (1): a(3), b(4)") has `name`."""
    listed = clients_text.split(":", 1)[-1]
    return name in re.findall(r"([^\s,()]+)\(\d+\)", listed)


def binary_arch(path):
    with open(path, "rb") as f:
        head = f.read(4)
    if head == b"\x00\x00\x03\xf3":
        return "m68k"
    if head == b"\x7fELF":
        return "ppc"
    return "unknown"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--port", type=int, default=int(os.environ.get("PORT", 3000)))
    ap.add_argument("--binary", default=os.path.join(PROJECT_DIR, "examples/hello_world/hello_world"))
    opts = ap.parse_args()

    mcp = Mcp(f"http://localhost:{opts.port}/mcp")
    results = []

    def check(name, fn):
        t0 = time.monotonic()
        try:
            ok, detail = fn()
        except Exception as e:  # a failed check must not stop the rest
            ok, detail = False, f"{type(e).__name__}: {e}"
        ms = (time.monotonic() - t0) * 1000
        results.append(ok)
        print(f"  [{'PASS' if ok else 'FAIL'}] {name} ({ms:.0f}ms){': ' + detail if detail else ''}")
        return ok

    print(f"devbench live test against http://localhost:{opts.port}/")
    if not check("MCP session", lambda: (mcp.start() or True, "")):
        return 1

    def tools():
        n = len(mcp.rpc("tools/list")["result"]["tools"])
        return n > 100, f"{n} tools"
    check("tools/list", tools)

    def ping():
        out = mcp.call("amiga_ping")
        return out.startswith("Amiga alive"), out
    if not check("ping", ping):
        print("  bridge not answering; is the emulator up? (scripts/start.sh status)")
        return 1

    def version():
        out = mcp.call("amiga_version")
        return out.startswith("AmigaBridge v"), out
    check("bridge version", version)

    arch = {}
    def sysinfo():
        out = mcp.call("amiga_sysinfo")
        cpu = next((l.split(":", 1)[1].strip() for l in out.splitlines() if "CPU:" in l), "?")
        arch["target"] = "ppc" if "PowerPC" in cpu else "m68k"
        return cpu != "?", f"CPU {cpu} -> {arch['target']}"
    check("sysinfo", sysinfo)

    def list_dir():
        out = mcp.call("amiga_list_dir", path="SYS:")
        return "entries" in out, out.splitlines()[0]
    check("list SYS:", list_dir)

    def dos_command():
        out = mcp.call("amiga_dos_command", command="echo devbench-live-test")
        return "devbench-live-test" in out, out.strip()
    check("AmigaDOS command", dos_command)

    target = arch.get("target")
    if not os.path.exists(opts.binary):
        check("hello_world binary", lambda: (False, f"{opts.binary} not built"))
        target = None
    elif binary_arch(opts.binary) != target:
        check("hello_world binary", lambda: (False, f"{opts.binary} is {binary_arch(opts.binary)}, "
                                                   f"target is {target}; pass --binary"))
        target = None

    def wait_gone():
        for _ in range(20):
            out = mcp.call("amiga_list_clients")
            if not has_client(out, CLIENT):
                return True, out
            time.sleep(0.5)
        return False, f"still registered: {out}"

    def stop_left_running():
        # Builds before hello_world handled CTRL-C ignore amiga_stop_client;
        # clearing its registered `running` variable stops any version.
        mcp.call("amiga_set_var", name="running", value="0")
        return wait_gone()

    def stop_client():
        out = mcp.call("amiga_stop_client", name=CLIENT)
        if not out.startswith("[ok]"):
            return False, out
        ok, detail = wait_gone()
        return ok, out if ok else detail

    if target and has_client(mcp.call("amiga_list_clients"), CLIENT):
        # With the old one still registered the checks below could see it
        # instead of the one this test launches
        if not check("stop a hello_world left running", stop_left_running):
            target = None

    if target:
        def push():
            out = mcp.call("amiga_push_file", local_path=opts.binary, amiga_path=REMOTE)
            return "CRC32 verified" in out, out
        if check("push hello_world (CRC verified)", push):
            def launch():
                out = mcp.call("amiga_launch", command=REMOTE)
                return out.startswith("[OK]"), out
            check("launch", launch)

            def registered():
                for _ in range(30):
                    out = mcp.call("amiga_list_clients")
                    if has_client(out, CLIENT):
                        return True, out
                    time.sleep(0.5)
                return False, out
            if check("client registers", registered):
                def startup_log():
                    for _ in range(10):
                        if f"[{CLIENT}] Hello World" in mcp.call("amiga_log", count=50):
                            return True, ""
                        time.sleep(0.5)
                    return False, "no startup line in the last 50 log entries"
                check("client log reaches host", startup_log)

                def var_round_trip():
                    mcp.call("amiga_set_var", name="message", value="live-test")
                    time.sleep(0.5)
                    out = mcp.call("amiga_get_var", name="message")
                    return "live-test" in out and "(cached)" not in out, out
                check("set + get variable", var_round_trip)

                def counter():
                    out = mcp.call("amiga_get_var", name="loop_count")
                    return "=" in out and "(cached)" not in out, out
                check("read variable", counter)

                def screenshot():
                    out = mcp.call("amiga_screenshot")
                    return out.startswith("Screenshot saved"), out.split("(", 1)[-1].rstrip(")")
                check("screenshot", screenshot)

                check("amiga_stop_client", stop_client)
            mcp.call("amiga_dos_command", command=f"delete {REMOTE} QUIET")

    passed = sum(results)
    print(f"{passed}/{len(results)} passed")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
