# Hatari agent console — Debugger tab

The 68k debugger over the agent API. Here Break has stopped the Falcon in Spectral Keep's code: the registers, the disassembly at the PC (highlighted), breakpoint entry by address, symbol or condition, and a field for any Hatari debugger command. The status line reads STOPPED with `last stop: user @ $029288`.

![Hatari agent console — Debugger tab](agent-console-debugger.png)

## Annotated
![Hatari agent console — Debugger tab, annotated with numbered callouts](agent-console-debugger-annotated.png)

1. **Toolbar** — Pause, Resume, run one frame or one second, cold reset and save a screenshot, plus a fast-forward toggle; each is one agent API call.
2. **Live emulator screen** — The /screen image polled every 150 ms at 1-3x zoom; clicking, dragging and typing on it are sent to the Atari as mouse and key input.
3. **Tabs** — Console, Joystick, Debugger and Machine.
4. **Debugger controls** — Break, step, step over, continue and run to breakpoint, through the /debug endpoints.
5. **Registers** — 68k data and address registers, PC, SR, USP and ISP while the CPU is stopped.
6. **Disassembly** — Code at the PC, with the current instruction highlighted and branch targets resolved.
7. **Breakpoints** — Add by address, symbol or condition such as d0=$20; lists the active ones.
8. **Debugger command** — Any Hatari debugger command (here info osheader); output goes to the Console tab.
9. **Status line** — Emulator state, frame counter, PC, machine and TOS, screen mode, the GEM mouse position and the last debugger stop, from GET /status.
