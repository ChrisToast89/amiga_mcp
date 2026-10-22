# 3DO homebrew (3do_dev)

A sister project to Amiga DevBench: a modern development kit for the **3DO Interactive Multiplayer** (1993; ARM60 at
12.5 MHz, 2 MB DRAM + 1 MB VRAM, the MADAM cel engine and CLIO's audio DSP, running the Portfolio multitasking OS), with a
scriptable, debuggable emulator that people, scripts and Claude Code (over MCP) all drive. Most of the games are the Amiga games
from this repository's `examples/`, running unchanged on the 3DO through an Amiga compatibility layer; three are rewrites of
Unity games for the cel engine.

- [Games and demos](#games-and-demos) — 24 entries
- [3DO DevBench web UI](devbench/README.md) — 17 screens, each plain and annotated

## How it is built

- **Toolchain.** ARM's own Norcroft C/C++ compiler (SDT 2.51, as 3DO developers used it), packaged by trapexit's 3do-devkit
  with the Portfolio 2.5 SDK. The compilers are 32-bit i386 Linux binaries, so `./3do build` runs them in a small Docker
  container (through QEMU user-mode emulation on Apple Silicon). Code is C89 (`armcc -bigend -apcs 3/32/nofp`), linked into a
  self-relocating AIF, packed into an ISO and RSA-signed so the retail BIOS boots it; a second link as ELF with DWARF gives
  gdb and the debugger source-level symbols.
- **Emulator.** Opera, the maintained libretro 3DO core, patched (`emulator/patches/`) with hooks for the kernel's debug
  console (MADAM register writes copied to a ring buffer), breakpoints, single-step, watchpoints, tracepoints and an SWI
  trace, plus a GDB server. A Python host (`tools/tdo`) loads the core with ctypes and steps it frame by frame, headless at
  about 15x real time, so every run is scripted and deterministic.
- **Sessions and tools.** `./3do run|log|shot|test|ctl|gdb` all work on sessions with control sockets; the MCP server
  exposes the same commands (`emu_boot`, `emu_run_until`, `emu_press`, `emu_look`, `emu_break`, `emu_profile`, `os_inspect`,
  `os_snapshot`/`os_diff`…) and [DevBench](devbench/README.md) puts a web UI, REST API and MCP over HTTP on top.
- **The Amiga layer** (`sdk/amiga`). graphics.library calls draw into an offscreen 320x256 buffer that is shown each frame
  as one hardware cel scaled to 320x240, with a pen-number palette in the cel's PLUT so palette writes recolour the screen as
  on the Amiga; Paula is emulated on the 3DO's DSP (one `varmono8.dsp` sample player per channel through `mixer4x2.dsp`)
  with a ProTracker player; `gfx_swap()` paces to 50 fps; files map to the disc and NVRAM. Games can put extra cels
  under the frame (Rotoball's floor, Pea Shooter Blast's tile cache, Void Trader's triangles).
- **Testing.** Every game has a `test.py` that boots its ISO headless, waits for a log line, presses buttons, checks the
  game's own log lines and measures its speed; `./3do selftest` builds and tests everything. The arcade disc bundles all
  the games behind a menu.

## How these images were captured

All 2026-10-20 from the emulator's native framebuffer (320x240), upscaled 3x nearest-neighbour to 960x720. Title and most
gameplay shots come from running each project's own `test.py` headless (its scripted button presses) with the screenshots
redirected; the rest come from short scripted runs through the same Python host (`tdo.core.Emulator`: boot, wait for the
ready line, hold pad buttons, save frames) to reach a busier moment. No sources were modified or rebuilt.

## Games and demos

| | Program | Type | About |
|---|---|---|---|
| <img src="ace_pilot/ace_pilot-gameplay.png" width="200"> | [Ace Pilot](ace_pilot/ace_pilot.md) | game | A first-person 3D wireframe dogfighting game: biplanes and blimps over a gridded airfield, with a split-screen two-player mode, ported from the Amiga original (`amiga_mcp examples/ace_pilot`). (2 images) |
| <img src="bullion_dash/bullion_dash-gameplay.png" width="200"> | [Bullion Dash](bullion_dash/bullion_dash.md) | game | A puzzle platformer: collect all the gold, dig traps for the guards and climb out, with a built-in level editor (C on the title). (2 images) |
| <img src="canyon_rescue/canyon_rescue-gameplay.png" width="200"> | [Canyon Rescue](canyon_rescue/canyon_rescue.md) | game | Fly the valleys of a fractal planet and rescue downed pilots, some of whom are Mimics in disguise, ported from the Amiga original (`amiga_mcp examples/canyon_rescue`). (2 images) |
| <img src="dot_chase/dot_chase-gameplay.png" width="200"> | [Dot Chase](dot_chase/dot_chase.md) | game | A dot-eater arcade game: a ladybug gathers seeds in a hedge maze while four spiders hunt it, and a flower turns the tables. (2 images) |
| <img src="frank_the_frog/frank_the_frog-gameplay.png" width="200"> | [Frank the Frog](frank_the_frog/frank_the_frog.md) | game | A road-and-river crossing game: hop Frank through traffic and ride logs and turtles to the homes, with generated music. (2 images) |
| <img src="jump_quest/jump_quest-gameplay.png" width="200"> | [Jump Quest](jump_quest/jump_quest.md) | game | A side-scrolling platformer starring RJ and Dale for one or two players taking turns, with three levels. (2 images) |
| <img src="lunar_rider/lunar_rider-gameplay.png" width="200"> | [Lunar Rider](lunar_rider/lunar_rider.md) | game | A side-scrolling moon-buggy ride: jump craters and rocks and shoot UFOs and meteors on the way to each checkpoint. (2 images) |
| <img src="nova_defense/nova_defense-gameplay.png" width="200"> | [Nova Defense](nova_defense/nova_defense.md) | game | A fixed-screen alien shooter: hold back the descending swarm from behind crystal shields and pick off the comet. (2 images) |
| <img src="orb_hunter/orb_hunter-gameplay.png" width="200"> | [Orb Hunter](orb_hunter/orb_hunter.md) | game | A cavern-exploration platformer: search the caverns room by room and collect power-ups (spring boots, roll form, missiles, bombs) to reach new areas. (4 images) |
| <img src="orbital_patrol/orbital_patrol-gameplay.png" width="200"> | [Orbital Patrol](orbital_patrol/orbital_patrol.md) | game | A side-scrolling planet-defence shooter: protect the humans from abductors across a wrapping world, with a scanner, smart bombs and hyperspace. (2 images) |
| <img src="pea_shooter_blast/pea_shooter_blast-gameplay.png" width="200"> | [Pea Shooter Blast](pea_shooter_blast/pea_shooter_blast.md) | game | Side-scrolling tank action: drive, jump and blast through the enemy lines. (2 images) |
| <img src="planet_chomp/planet_chomp-gameplay.png" width="200"> | [Planet Chomp](planet_chomp/planet_chomp.md) | game | A maze chase on a tiny planet: the maze wraps all the way round a sphere, and you eat every crumb while four spooks (Gloom, Spark, Mist and Moss) hunt you, grabbing a golden key to turn the tables. (3 images) |
| <img src="rj_birthday/rj_birthday-gameplay.png" width="200"> | [RJ's Birthday Bash](rj_birthday/rj_birthday.md) | game | An arcade party game written as a tribute to RJ Mical (Intuition, Amiga, Atari Lynx, 3DO) for his 70th birthday: run the party across six themed rooms of RJ's house. (2 images) |
| <img src="rock_blaster/rock_blaster-gameplay.png" width="200"> | [Rock Blaster](rock_blaster/rock_blaster.md) | game | A vector rock shooter: rotate, thrust and blast drifting rocks that split as they are hit. (2 images) |
| <img src="rolling_steel/rolling_steel-gameplay.png" width="200"> | [Rolling Steel](rolling_steel/rolling_steel.md) | game | A marble racer over six floating courses against one clock that carries over, in the spirit of the 1984 arcade cabinet. (3 images) |
| <img src="rotoball/rotoball-gameplay.png" width="200"> | [Rotoball](rotoball/rotoball.md) | game | A split-screen futuristic ball sport in the style of Ballblazer: the top pane shows the CPU opponent's view and the bottom pane the player's, each skimmer facing the ball. (2 images) |
| <img src="sky_knights/sky_knights-gameplay.png" width="200"> | [Sky Knights](sky_knights/sky_knights.md) | game | Aerial jousting on winged mounts for one or two players: strike opponents from above and collect the eggs. (2 images) |
| <img src="spectral_keep/spectral_keep-gameplay.png" width="200"> | [Spectral Keep](spectral_keep/spectral_keep.md) | game | An isometric flip-screen adventure in the style of Knight Lore and Head over Heels: three keeps and 24 rooms, carrying relics to the throne. (3 images) |
| <img src="stakattack/stakattack-gameplay.png" width="200"> | [StakAttack](stakattack/stakattack.md) | game | A colourful falling-block puzzle in a 12-wide well with original tracker music. (3 images) |
| <img src="uranus_lander/uranus_lander-gameplay.png" width="200"> | [Uranus Lander](uranus_lander/uranus_lander.md) | game | A lunar-lander game: rotate and thrust down onto the landing pads of procedurally generated terrain before the fuel runs out, with ProTracker music. (2 images) |
| <img src="void_trader/void_trader-gameplay.png" width="200"> | [Void Trader](void_trader/void_trader.md) | game | Space combat and trading in filled 3D: fly with six degrees of freedom, fight pirates, dock at the station to trade and earn 5000 credits to win. (3 images) |
| <img src="arcade/arcade-menu.png" width="200"> | [3DO Arcade](arcade/arcade.md) | tool | The arcade disc: a game selector that bundles every Amiga-layer game on one CD. (3 images) |
| <img src="demo/demo-1.png" width="200"> | [CLAUDE x 3DO demo](demo/demo.md) | demo | A small cel-engine demo, written from scratch for the 3DO rather than ported. (2 images) |
| <img src="hello/hello.png" width="200"> | [hello](hello/hello.md) | demo | The starter program every new project is created from (`./3do new` copies it from `sdk/template`): a double-buffered display, controller input and debug logging. (1 image) |

Not captured: `unittest` and `paula_test` (test programs with no meaningful display).
