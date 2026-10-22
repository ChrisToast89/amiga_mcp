#!/usr/bin/env python3
"""write_devbench_md.py - one markdown page per devbench screen + README index.

Legend items come from portfolio/devbench/annotations/<name>.json (the same
specs annotate.py renders), so the numbered list always matches the image.
"""
import json, os

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "devbench")
TARGET = {"os4": "AmigaOS 4 PPC", "68k": "Classic 68k"}

# name -> (screen title, intro)
INTRO = {
    "dashboard": ("Dashboard",
        "The landing page: one glance tells you which Amiga this devbench drives, whether the serial/TCP link and the "
        "Amiga-side bridge daemon are alive, which bridge clients are registered and how much memory is free. It also "
        "holds emulator Start/Restart/Stop and a raw protocol console for poking the daemon directly. The same facts "
        "are available to Claude Code through MCP (`amiga_ping`, `amiga_list_clients`, `amiga_capabilities`, "
        "`amiga_emulator_status`)."),
    "logs": ("Logs",
        "Every `AB_I`/`AB_W`/`AB_E` line an app sends through the bridge client library (CLOG messages), streamed "
        "live over server-sent events. Filter by level, client or text while a program runs; this is the inner-loop "
        "printf view. Claude reads the same buffer with `amiga_log`, `amiga_watch_logs` and `amiga_tail`. Here the "
        "stream is a game's per-frame heartbeat lines."),
    "files-browser": ("Files · Browser",
        "Browse the Amiga's filesystem over the bridge: volumes and assigns on the left, a LISTDIR of the selected "
        "directory on the right, with per-file View / Edit / Run / CRC / Rename / Copy buttons. Useful for checking "
        "that a deploy landed and for poking at config files without touching the emulator window "
        "(MCP: `amiga_list_volumes`, `amiga_list_dir`, `amiga_read_file`)."),
    "files-viewer": ("Files · File viewer",
        "Clicking View on a file opens it in a modal, read over the bridge. Here it's the OS4 guest's "
        "`S:Startup-Sequence` (MCP: `amiga_read_file`)."),
    "files-transfer": ("Files · Transfer",
        "Push files from the host to the Amiga, or pull them back, over the serial bridge itself. This is for setups "
        "with no shared folder or writable hardfile. A glob can send several files at once "
        "(MCP: `amiga_transfer`, `amiga_push_file`, `amiga_pull_file`)."),
    "tools-memory": ("Tools · Memory",
        "A hex/ASCII memory viewer and poker. Read any address through the bridge's INSPECT command, jump to common "
        "addresses with the bookmarks, and write hex bytes back (RAM only, validated with TypeOfMem). Classic-chipset "
        "addresses such as `$DFF000` and the CIAs only mean something on 68k "
        "(MCP: `amiga_inspect_memory`, `amiga_write_memory`)."),
    "tools-variables": ("Tools · Variables",
        "Variables an app exposes with `ab_register_var()` appear here and can be read or changed live: tune a "
        "game's speed or gravity without rebuilding. The clients running during this capture registered none, so "
        "the table is empty (MCP: `amiga_get_var`, `amiga_set_var`)."),
    "tools-shell": ("Tools · Shell",
        "An interactive AmigaDOS shell in the browser, via the `shell_proxy` bridge client, with history, tab "
        "completion and aliases. The proxy wasn't running when this was captured, so the tab offers to launch it. "
        "Claude runs one-off commands with `amiga_dos_command` / `amiga_exec` instead."),
    "tools-tasks": ("Tools · Tasks",
        "The Exec task list (LISTTASKS): name, priority, state and stack size, refreshed on demand or "
        "automatically. Use it to confirm a program started, or to find out what is hogging the CPU. On this OS4 build "
        "many task names come back as `?` (MCP: `amiga_list_tasks`)."),
    "inspect-graphics": ("Inspect · Graphics",
        "Graphics inspection tools: bridge screenshots of the screen or a single window, the palette, the active "
        "copper list, hardware sprites, a raw bitmap renderer, an IFF ILBM viewer and a visual diff between two "
        "captures (MCP: `amiga_screenshot`, `amiga_get_palette`, `amiga_copper_list`, `amiga_sprites`)."),
    "inspect-system": ("Inspect · System",
        "Read-only views of the running OS plus a few controls: system and bridge info, volumes, public message "
        "ports, the Intuition screen/window/gadget tree, the library and device inspector, assigns, fonts, locale "
        "catalogs, ARexx ports and the clipboard, plus startup-sequence, ENV: prefs, boot-log, file-tail, checksum "
        "and protection-bit tools. Input injection and Shutdown/Reboot live here too. Each card is backed by MCP "
        "tools such as `amiga_sysinfo`, `amiga_list_libs` and `amiga_list_screens`."),
    "inspect-debug": ("Inspect · Debug",
        "Low-level debugging aids that work through the bridge: symbol loading and lookup, a disassembler, the "
        "crash handler's last report, the Exec memory map, memory search/diff, stack checks, custom-chip registers, "
        "Paula audio state, SnoopDos-style call tracing, a chip-write logger, and per-client resource, performance "
        "and pool tracking (MCP: `amiga_disassemble`, `amiga_last_crash`, `amiga_audio_channels`, "
        "`amiga_list_resources`, `amiga_perf_report`)."),
    "develop": ("Develop",
        "Project-level actions: pick one of the `examples/` projects and run it on the Amiga, scaffold a new "
        "bridge-enabled project from a template, and watch live results from apps that use the bridge test harness "
        "(`ab_test_begin()` / `AB_ASSERT()` / `ab_test_end()`). From Claude Code the whole edit → build → deploy → run "
        "loop is one call: `amiga_build_deploy_run`."),
    "debugger": ("Debugger",
        "A source-level debugger for your own bridge-enabled programs. Attach to (or launch and attach to) a "
        "client, load its symbols, set breakpoints in the source gutter, then continue or step while watching "
        "registers, the call stack and locals. Nothing is attached in this capture "
        "(MCP: `amiga_debug_attach`, `amiga_set_breakpoint`, `amiga_step`, `amiga_next`, `amiga_backtrace`)."),
    "settings-config": ("Settings · Config",
        "Edits the active profile's settings: serial link, emulator binary and config, auto-start, crash-handler "
        "auto-enable and the deploy target. The right-hand pane edits the FS-UAE config file in place and can "
        "restart the emulator with it. For the qemu-os4 profile that pane is empty, since QEMU is started from a "
        "script and has no FS-UAE config."),
    "settings-traffic": ("Settings · Traffic",
        "Every MCP tool call (from Claude Code or any other MCP client) and every REST call the web UI makes is "
        "logged with timing and status. Select an entry to see its request and response, or replay it. The list "
        "here, filtered to MCP, shows calls made by agents driving the OS4 guest at the time "
        "(`amiga_input_key`, `amiga_launch`, `amiga_list_clients`, …). Useful for seeing exactly what Claude did."),
    "about": ("About",
        "The About dialog, opened from the logo or the About button: AmigaDevBench's tribute to the people who "
        "built the Amiga."),
    "fsuae": ("FS-UAE native debugger",
        "Classic-68k only. With a patched FS-UAE build (geekychris/fsuae_remote_patch) that exposes an HTTP/JSON-RPC "
        "debug API, this tab gives CPU-level control without the bridge: pause/step, registers, breakpoints and "
        "watchpoints, memory, chipset registers and save states (MCP: `amiga_fsuae_*`). The FS-UAE running for "
        "this capture doesn't expose that RPC (probe status: unavailable), so the tab is normally hidden (it was opened "
        "directly for this screenshot) and shows how to enable it."),
}

ORDER = ["dashboard", "logs", "files-browser", "files-viewer", "files-transfer", "tools-memory", "tools-variables",
         "tools-shell", "tools-tasks", "inspect-graphics", "inspect-system", "inspect-debug", "develop", "debugger",
         "settings-config", "settings-traffic", "about", "fsuae"]

TARGET_NOTE = {
    ("68k", "dashboard"): " On this target the badge and stripe are blue, and the emulator card manages FS-UAE.",
    ("os4", "dashboard"): " On this target the badge and stripe are orange, and the emulator card manages QEMU (sam460ex).",
    ("68k", "inspect-graphics"): " On 68k the palette, copper list and sprite readers return real chipset data, "
        "here from a 4-colour screen.",
    ("os4", "inspect-graphics"): " The copper and sprite tools are classic-chipset features, so they matter on "
        "68k (see the 68k capture). On OS4 this tab is mostly used for screenshots.",
    ("68k", "inspect-debug"): " This 68k capture shows the disassembler on Kickstart ROM at `$FC0000`, the chip/fast "
        "memory map, decoded custom-chip registers and Paula's four channels.",
    ("os4", "inspect-debug"): " On OS4 the chip-register and audio cards don't apply (sam460ex has no classic "
        "chipset); the memory map shows the Exec memory list.",
    ("68k", "tools-memory"): " Here it shows the first 256 bytes of the Kickstart ROM at `$F80000`.",
    ("os4", "tools-memory"): " No read was issued on the OS4 guest for this capture.",
    ("68k", "files-browser"): " On the 68k AmiKit setup the volumes include the host-shared `Dropbox:` folder that deploys land in.",
    ("68k", "settings-config"): " Here the editor shows the AmiKit-Debug FS-UAE config, whose header notes it uses serial over TCP for the bridge.",
}


def screen_key(name):
    return name.split("-", 1)[1]


def main():
    names = sorted(f[:-5] for f in os.listdir(os.path.join(D, "annotations")) if f.endswith(".json"))
    pages = {}
    for name in names:
        tgt, key = name.split("-", 1)
        spec = json.load(open(os.path.join(D, "annotations", name + ".json")))
        title, intro = INTRO[key]
        intro += TARGET_NOTE.get((tgt, key), "")
        alt = f"DevBench {title} screen ({TARGET[tgt]})"
        lines = [f"# DevBench — {title} ({TARGET[tgt]})", "", intro, "",
                 f"![{alt}]({name}.png)", "", "## Annotated",
                 f"![{alt}, annotated with numbered callouts]({name}-annotated.png)", ""]
        for i, it in enumerate(spec["items"], 1):
            lines.append(f"{i}. **{it['label']}** — {it['text']}")
        open(os.path.join(D, name + ".md"), "w").write("\n".join(lines) + "\n")
        pages.setdefault(tgt, []).append((ORDER.index(key), name, title))
        print("wrote", name + ".md")

    def index(tgt):
        return "\n".join(f"- [{t}]({n}.md)" for _, n, t in sorted(pages.get(tgt, [])))

    readme = f"""# DevBench — the host side of Amiga DevBench

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
{index('os4')}

## Screens — Classic 68k (:3001)
{index('68k')}

## How these images were made
- `portfolio/tools/webui_shot.py`: headless Chrome via the DevTools protocol (configurable CDP port/profile),
  1600×1000 viewport at deviceScaleFactor 2.
- `portfolio/tools/capture_devbench.py os4|68k [screen…]`: opens each tab/sub-tab, runs only read-only refresh
  calls, waits for the data, screenshots it, and reads each callout's `getBoundingClientRect()` from the DOM into
  `annotations/<name>.json`. Long panels (Inspect → System/Debug) are captured at full height.
- `portfolio/tools/annotate.py annotations/*.json`: renders the numbered callouts and legend
  (`<name>-annotated.png`).
- `portfolio/tools/write_devbench_md.py`: writes these pages from the same specs.
"""
    open(os.path.join(D, "README.md"), "w").write(readme)
    print("wrote README.md")


if __name__ == "__main__":
    main()
