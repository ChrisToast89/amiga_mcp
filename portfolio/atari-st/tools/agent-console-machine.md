# Hatari agent console — Machine tab

Machine setup: the TOS images in the agent ROM directory (EmuTOS 1024k multi-language and the 192k country builds), machine type and RAM for a cold boot, media (floppy, a host folder as GEMDOS drive C:, an autostart program) and free-form Hatari options sent to `POST /config`.

![Hatari agent console — Machine tab](agent-console-machine.png)

## Annotated
![Hatari agent console — Machine tab, annotated with numbered callouts](agent-console-machine-annotated.png)

1. **Toolbar** — Pause, Resume, run one frame or one second, cold reset and save a screenshot, plus a fast-forward toggle; each is one agent API call.
2. **Live emulator screen** — The /screen image polled every 150 ms at 1-3x zoom; clicking, dragging and typing on it are sent to the Atari as mouse and key input.
3. **Tabs** — Console, Joystick, Debugger and Machine.
4. **TOS ROMs** — The ROM images in the agent ROM directory with their EmuTOS version and country.
5. **Boot a machine** — Pick a machine type and RAM size and cold-boot the selected ROM.
6. **Media** — Insert a floppy image, mount a host folder as GEMDOS drive C: or set the program to autostart.
7. **Hatari options** — Any Hatari command-line options, applied through POST /config (may reset the machine).
8. **Status line** — Emulator state, frame counter, PC, machine and TOS, screen mode, the GEM mouse position and the last debugger stop, from GET /status.
