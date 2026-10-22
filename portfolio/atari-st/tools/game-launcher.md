# Hatari game launcher

`tools/games/launcher.py` (in hatari_augmented) is the host-side menu for the ports. It reads `atari_st_games/games.ini` (title, port directory, 8.3 program name, machine, extra Hatari options, screenshot, description, controls) and Play builds the game if asked, stops any Hatari on the agent port and starts `hatari-agent-run.sh` with the game's machine, its `build/` as drive C: and the program autostarted, so the agent API stays available while you play. `--list` and `--play <id>` do the same without the window. Here RJ's Birthday Bash is selected; the picture is the game's own `docs/foyer.png`.

![Hatari game launcher](game-launcher.png)

## Annotated
![Hatari game launcher, annotated with numbered callouts](game-launcher-annotated.png)

1. **Game list** — Every [section] of games.ini with the machine it needs; double-click or Return plays it.
2. **Title and target** — Machine, port directory and the 8.3 program name autostarted as C:\<program>.
3. **Screenshot** — The image named by the game's screenshot key, from the port's docs/.
4. **Description and controls** — The description and controls keys from games.ini.
5. **Actions** — Play (optionally make first, sound on/off) starts Hatari on the right machine through hatari-agent-run.sh; Stop Hatari quits it; Agent console opens hatari_gui.py on the same port.
6. **Status line** — Last log line: game count, then build and start-up messages.
