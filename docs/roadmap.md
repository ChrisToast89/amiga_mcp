<!-- SPDX-License-Identifier: MIT -->
<!-- Copyright (c) 2026 Chris Collins <chris@hitorro.com> -->

# Roadmap

[Documentation index](README.md) · [Install DevBench](quickstart.md)

## Future Improvements

### Debugging & Inspection

Breakpoints, stepping, symbolic backtraces and STABS address-to-line lookup
already exist; see the [debugger guide](debuggers.md).

- **Source context**: Show the source lines around an address in the memory inspector.
- **Watchpoints**: Monitor memory addresses for changes and notify the host when values change (polled or via custom exception handler).

### Build & Workflow

- **Incremental builds**: ~~Cache Docker layers or use a persistent container~~ *(done — persistent container, ~10x speedup)*. Further: watch source files for auto-rebuild.
- **Build error parsing**: Parse GCC error output and map to source files on the host for clickable error navigation.
- **Auto-rebuild on save**: Watch source files and trigger build+deploy+relaunch automatically.
- **Multiple target configs**: Support different CPU targets (68000, 68020, 68040) and memory configurations.
- **Unit test framework**: ~~Lightweight test harness that runs on the Amiga and reports results via the bridge~~ *(done — `ab_test_begin`/`AB_ASSERT`/`ab_test_end` + `amiga_run_tests` MCP tool)*.

### Protocol & Communication

- **Binary protocol option**: Replace text protocol with a compact binary format for higher throughput (especially for large memory dumps).
- **Compression**: Compress large transfers (file reads, memory dumps) to reduce serial bandwidth.
- **Flow control**: Implement proper XON/XOFF or hardware flow control for reliability on real hardware.
- **Checksum/CRC**: ~~Add integrity checking for serial data~~ *(done — CRC32 file checksums via `amiga_checksum`)*. Still needed: per-message CRC for serial link integrity.
- **Multi-serial**: Support multiple serial connections for parallel debugging of networked Amiga setups.

### Web UI

- **Variable graphing**: Plot variable values over time (e.g., chart free memory or CPU usage).
- **Sprite editor**: Visual sprite data editor using memory write.
- **Sound register viewer**: Paula chip register inspection for audio debugging.
- **Dark/light theme toggle**: Currently dark-only.

### Client Library

- **Automatic variable push**: Option to push all registered variables on every heartbeat without manual `ab_push_var()` calls.
- **Structured logging**: Log with key=value pairs for easier filtering and search on the host.
- **C++ support**: Wrapper classes with RAII for automatic cleanup.
- **Lua/REXX scripting**: Execute scripts on the Amiga that interact with registered variables and hooks.

### Infrastructure

- **Real hardware support**: Test and optimize for real Amiga serial ports (active at 9600-115200 baud) instead of emulator TCP.
- **Network transport**: Optional TCP/IP transport using bsdsocket.library for Amigas with network cards (faster than serial).
- **Multi-client web UI**: Show different clients in separate tabs/panels with independent variable views.
- **Session recording**: Record all bridge traffic for later replay and analysis.
- **CI/CD pipeline**: Automated build + deploy + test cycle triggered by git push.
- **VS Code extension**: Bring the web UI and MCP tools into VS Code as an extension with inline diagnostics.
- **ROM-based bridge**: Burn the bridge daemon into a custom Kickstart ROM module for zero-setup debugging.

### AmigaOS Integration

- **Intuition event forwarding**: ~~Forward mouse clicks and keyboard events from the host to the Amiga~~ *(done — `amiga_input_key`, `amiga_input_mouse_move`, `amiga_input_click`)*.
- **Clipboard bridge**: ~~Share clipboard between host and Amiga~~ *(done — Clipboard Bridge in web UI + CLIPGET/CLIPSET protocol)*.
- **Assign management**: ~~Create/modify/remove Amiga assigns from the host~~ *(done — `amiga_list_assigns`, `amiga_assign` + ASSIGNS protocol + web UI Assign Manager)*.
- **Preference editing**: ~~Read and write AmigaOS preference files from the host~~ *(done — Preferences Editor in web UI)*.
- **Package manager**: Simple system for installing/removing Amiga software via the bridge.
