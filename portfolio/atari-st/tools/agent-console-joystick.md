# Hatari agent console — Joystick tab

A joystick pad for port 1 (the joystick port) or port 0 (the mouse port). Holding a button holds that direction through `POST /input/joystick`; the note records an ST quirk the INTERACT tests found: with the mouse on, joystick-1 fire arrives as the right mouse button.

![Hatari agent console — Joystick tab](agent-console-joystick.png)

## Annotated
![Hatari agent console — Joystick tab, annotated with numbered callouts](agent-console-joystick-annotated.png)

1. **Toolbar** — Pause, Resume, run one frame or one second, cold reset and save a screenshot, plus a fast-forward toggle; each is one agent API call.
2. **Live emulator screen** — The /screen image polled every 150 ms at 1-3x zoom; clicking, dragging and typing on it are sent to the Atari as mouse and key input.
3. **Tabs** — Console, Joystick, Debugger and Machine.
4. **Port** — Port 1 is the normal joystick port, port 0 the mouse port.
5. **Joystick pad** — Eight directions and fire; holding a button holds the direction (POST /input/joystick).
6. **Hardware note** — With the mouse on, the ST reports joystick-1 fire as the right mouse button.
7. **Status line** — Emulator state, frame counter, PC, machine and TOS, screen mode, the GEM mouse position and the last debugger stop, from GET /status.
