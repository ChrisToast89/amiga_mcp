# Hatari agent console — Console tab

`tools/agent/hatari_gui.py` (in hatari_augmented) is a Tk front end for the Hatari agent API, built on the same `hatari_agent.py` client the bots and tests use. It shows the live emulator screen (zoomable; clicks, drags and typing on it become Atari input) beside four tabs. The Console tab shows what the running program prints through NatFeats, from `GET /console`: here Spectral Keep on the Falcon030 logs its state, rooms and frame timings as `KEEP I ...` lines.

![Hatari agent console — Console tab](agent-console-console.png)

## Annotated
![Hatari agent console — Console tab, annotated with numbered callouts](agent-console-console-annotated.png)

1. **Toolbar** — Pause, Resume, run one frame or one second, cold reset and save a screenshot, plus a fast-forward toggle; each is one agent API call.
2. **Live emulator screen** — The /screen image polled every 150 ms at 1-3x zoom; clicking, dragging and typing on it are sent to the Atari as mouse and key input.
3. **Tabs** — Console, Joystick, Debugger and Machine.
4. **Program console** — Text the Atari program prints through NatFeats, read from GET /console: here Spectral Keep's KEEP log lines with fps, room and per-frame timings.
5. **Status line** — Emulator state, frame counter, PC, machine and TOS, screen mode, the GEM mouse position and the last debugger stop, from GET /status.
