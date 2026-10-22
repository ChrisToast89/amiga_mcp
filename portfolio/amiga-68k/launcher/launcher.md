# Launcher
**Platform:** Classic Amiga (68k, AGA A1200/A4000 class) · **Source:** `examples/launcher/` · **Type:** tool

An app launcher in a GadTools ListView window on the Workbench screen. It scans `DH2:Dev/` for executables (skipping data files such as `.mod`, `.stats`, `.info`), lists new apps first and then by launch count, starts the chosen program asynchronously with `SystemTags`, and saves the counts to `DH2:Dev/launcher.stats`. It registers with the bridge as `launcher`.

## Running
![Launcher ListView listing the Dev programs](launcher.png)
The "Launcher W/S=Nav Enter=Run" window lists the Dropbox:Dev programs (hubert, orb_hunter, planet_chomp_68k, plasma, rolling_steel_68k selected, rotoball, system_monitor, ... uranus_lander, boing_ball), with [NE] marking new entries and launch counts such as (11), (7), (6), (4). In this session it came up by itself at every emulator boot.

**Controls:** click to select, double-click or Enter to launch, W / S or Up / Down to navigate, Esc quits.
