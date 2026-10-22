# DevBench — the host side of Amiga DevBench

DevBench (`amiga-devbench/`) is the host-side half of this project: a single Python server (Starlette + uvicorn)
that talks to a real or emulated Amiga and exposes it two ways at once: a **web UI** for people and an
**MCP server** (`/mcp`, FastMCP) for Claude Code. Builds, deploys, logs, memory, tasks, screens, files and a
debugger are all reachable from either side.

## Architecture

```
 Amiga (emulated)                                  Host (macOS / Linux / Windows)
 ┌──────────────────────────────┐   serial over   ┌──────────────────────────────────────────┐
 │ your app ── libbridge.a ─┐   │   TCP (FS-UAE / │ amiga_devbench (Python)                  │
 │   ab_init / AB_I / ab_poll│   │   QEMU expose   │  ├─ serial protocol (CLOG, CVAR, HB, …)  │
 │                           ▼   │   the Amiga     │  ├─ web UI  ── browser  (this portfolio) │
 │ amiga-bridge daemon ◄─MsgPort │   serial port)  │  ├─ MCP /mcp ── Claude Code              │
 │  owns serial.device           ├────────────────►│  ├─ REST /api/* (used by the UI)         │
 │  LISTTASKS, INSPECT, SCRIPT…  │◄────────────────┤  ├─ Docker cross-compilers (build)       │
 └──────────────────────────────┘ pipe-delimited   │  └─ emulator manager + deploy            │
                                  text lines       └──────────────────────────────────────────┘
```

- **amiga-bridge** runs on the Amiga. It owns `serial.device`, sends heartbeats (`HB|tick|free_chip|free_fast|clients`),
  forwards app logs (`CLOG|client|level|tick|msg`) and answers commands from the host (`GETVAR`, `SETVAR`, `CALLHOOK`,
  `INSPECT`, `LISTTASKS`, `SCRIPT`, …: over 100 according to the dashboard's Capabilities card).
- Apps link **libbridge.a** and talk to the daemon over Exec message ports: `ab_init("name")`, `AB_I("…")`,
  `ab_register_var()`, `ab_register_hook()`, `ab_poll()` once per frame.
- **devbench** connects to the emulator's serial-over-TCP port, keeps the log/variable/client state, and serves the
  web UI and MCP tools from the same process. Every UI panel uses the same REST/bridge calls the MCP tools do,
  and the Settings → Traffic tab logs both.

## Two targets

| | Classic 68k | AmigaOS 4 PPC |
|---|---|---|
| OS / emulator | AmigaOS 3.x on FS-UAE (AmiKit) | AmigaOS 4.1 on QEMU `sam460ex` |
| devbench profile / port | `local-fsuae` · :3001 | `qemu-os4` · :3000 |
| Toolchain | `amigadev/crosstools:m68k-amigaos` | `walkero/amigagccondocker:os4-gcc11` |
| Deploy | shared folder (`DH2:Dev/`) | dev HDF written with `xdftool` |
| UI cues | blue stripe + "Classic Amiga · 68k" badge | orange stripe + "AmigaOS 4 · PowerPC" badge |
| Extras | chipset tools (copper, sprites, chip regs, Paula); FS-UAE RPC debugger tab with a patched FS-UAE | — |

Both devbenches were running side by side for these captures (OS4 on :3000, 68k on :3001), each with its bridge
connected while other agents ran programs on the emulators. Screens that look the same on both targets were
captured once, from OS4.

## Screens — AmigaOS 4 PPC (:3000)
- [Dashboard](os4-dashboard.md)
- [Logs](os4-logs.md)
- [Files · Browser](os4-files-browser.md)
- [Files · File viewer](os4-files-viewer.md)
- [Files · Transfer](os4-files-transfer.md)
- [Tools · Memory](os4-tools-memory.md)
- [Tools · Variables](os4-tools-variables.md)
- [Tools · Shell](os4-tools-shell.md)
- [Tools · Tasks](os4-tools-tasks.md)
- [Inspect · Graphics](os4-inspect-graphics.md)
- [Inspect · System](os4-inspect-system.md)
- [Inspect · Debug](os4-inspect-debug.md)
- [Develop](os4-develop.md)
- [Debugger](os4-debugger.md)
- [Settings · Config](os4-settings-config.md)
- [Settings · Traffic](os4-settings-traffic.md)
- [About](os4-about.md)

## Screens — Classic 68k (:3001)
- [Dashboard](68k-dashboard.md)
- [Files · Browser](68k-files-browser.md)
- [Tools · Memory](68k-tools-memory.md)
- [Inspect · Graphics](68k-inspect-graphics.md)
- [Inspect · Debug](68k-inspect-debug.md)
- [Settings · Config](68k-settings-config.md)
- [FS-UAE native debugger](68k-fsuae.md)

## How these images were made
- `portfolio/tools/webui_shot.py`: headless Chrome via the DevTools protocol (configurable CDP port/profile),
  1600×1000 viewport at deviceScaleFactor 2.
- `portfolio/tools/capture_devbench.py os4|68k [screen…]`: opens each tab/sub-tab, runs only read-only refresh
  calls, waits for the data, screenshots it, and reads each callout's `getBoundingClientRect()` from the DOM into
  `annotations/<name>.json`. Long panels (Inspect → System/Debug) are captured at full height.
- `portfolio/tools/annotate.py annotations/*.json`: renders the numbered callouts and legend
  (`<name>-annotated.png`).
- `portfolio/tools/write_devbench_md.py`: writes these pages from the same specs.
