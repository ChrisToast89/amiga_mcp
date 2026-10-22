# Amiga DevBench portfolio

Screenshots and write-ups of everything built with Amiga DevBench, captured from the real
emulators: classic 68k AmigaOS 3.x on FS-UAE (AmiKit), AmigaOS 4.1 PowerPC on QEMU sam460ex,
and the sister projects' Atari ST/STE/Falcon (Hatari) and 3DO (Opera) ports.
Each program has its own folder with its PNGs and one markdown file describing every image.
Captured 2026-10-20.

- [Classic Amiga 68k](#classic-amiga-68k) — 37 programs
- [AmigaOS 4.1 PowerPC](#amigaos-41-powerpc) — 14 entries
- [DevBench web UI](devbench/README.md) — 24 screens, each plain and annotated
- [Atari ST / STE / Falcon ports](atari-st/README.md) — 21 entries (Hatari), plus annotated agent tooling
- [3DO ports](3do/README.md) — 24 entries (Opera), plus the [3DO devbench](3do/devbench/README.md), annotated

## Classic Amiga 68k

| | Program | Type | About |
|---|---|---|---|
| <img src="amiga-68k/ace_pilot/ace_pilot-gameplay.png" width="200"> | [Ace Pilot](amiga-68k/ace_pilot/ace_pilot.md) | game | A first-person 3D wireframe dogfighting game against enemy biplanes and blimps, with ground targets, a split-screen two-player mode and two display modes (classic green vectors or multi-colour). (2 images) |
| <img src="amiga-68k/bullion_dash/bullion_dash-gameplay.png" width="200"> | [Bullion Dash](amiga-68k/bullion_dash/bullion_dash.md) | game | A puzzle platformer: collect all the gold, dig traps for the guards and escape, with a built-in level editor (E on the title). (2 images) |
| <img src="amiga-68k/canyon_rescue/canyon_rescue-gameplay.png" width="200"> | [Canyon Rescue](amiga-68k/canyon_rescue/canyon_rescue.md) | game | Fly the valleys of a fractal planet and rescue downed pilots, some of whom are Mimics in disguise. (2 images) |
| <img src="amiga-68k/dot_chase/dot_chase-gameplay.png" width="200"> | [Dot Chase](amiga-68k/dot_chase/dot_chase.md) | game | A dot-eater arcade game: a ladybug gathers seeds in a hedge maze while four spiders hunt it, and a flower turns the tables; it supports alternating two-player play. (2 images) |
| <img src="amiga-68k/emberkeep/emberkeep-gameplay.png" width="200"> | [Emberkeep](amiga-68k/emberkeep/emberkeep.md) | game | A clean-room top-down cavern explorer played by lantern light: only a small area around the player is lit, the lantern burns oil that must be refilled from flasks, and collecting the runes opens the exit portal. (2 images) |
| <img src="amiga-68k/frank_the_frog/frank_the_frog-gameplay.png" width="200"> | [Frank the Frog](amiga-68k/frank_the_frog/frank_the_frog.md) | game | A road-and-river crossing arcade game: help Frank hop through traffic and ride logs and turtles to the ponds. (2 images) |
| <img src="amiga-68k/jump_quest/jump_quest-gameplay.png" width="200"> | [Jump Quest](amiga-68k/jump_quest/jump_quest.md) | game | A platformer starring RJ and Dale, for one or two players taking turns, with three levels defined in `src/levels/`. (2 images) |
| <img src="amiga-68k/lunar_rider/lunar_rider-gameplay.png" width="200"> | [Lunar Rider](amiga-68k/lunar_rider/lunar_rider.md) | game | A side-scrolling moon-buggy ride: jump craters, shoot rocks, UFOs and meteors, and reach each zone. (2 images) |
| <img src="amiga-68k/miner_meteor/miner_meteor-gameplay.png" width="200"> | [Miner Meteor](amiga-68k/miner_meteor/miner_meteor.md) | game | A clean-room single-screen tile platformer in the style of early-1980s 8-bit games: each level is a fixed 20x15-tile room with keys to collect, an exit that unlocks after the last key, and hazards such as spikes, patrolling guardians, conveyors and collapsing floors, while the air supply drains. (2 images) |
| <img src="amiga-68k/nova_defense/nova_defense-gameplay.png" width="200"> | [Nova Defense](amiga-68k/nova_defense/nova_defense.md) | game | A fixed-screen alien shooter: 48 aliens in staggered rows, crystal shields and a passing comet. (2 images) |
| <img src="amiga-68k/orb_hunter/orb_hunter-gameplay.png" width="200"> | [Orb Hunter](amiga-68k/orb_hunter/orb_hunter.md) | game | A cavern-exploration platformer with tile-based rooms, power-ups (roll form, missiles, bombs, beams), several enemy types and bosses. (2 images) |
| <img src="amiga-68k/orbital_patrol/orbital_patrol-gameplay.png" width="200"> | [Orbital Patrol](amiga-68k/orbital_patrol/orbital_patrol.md) | game | A side-scrolling planet-defence shooter: protect the humans from abductors across a wraparound world six screens wide, with a scanner showing the whole world, six enemy types, smart bombs and hyperspace. (2 images) |
| <img src="amiga-68k/pea_shooter_blast/pea_shooter_blast-gameplay.png" width="200"> | [Pea Shooter Blast](amiga-68k/pea_shooter_blast/pea_shooter_blast.md) | game | Side-scrolling tank action with ladders, enemies, bosses and eight weapon levels. (2 images) |
| <img src="amiga-68k/planet_chomp_68k/planet_chomp_68k-gameplay.png" width="200"> | [Planet Chomp (68k)](amiga-68k/planet_chomp_68k/planet_chomp_68k.md) | game | A maze chase on a tiny planet: the maze wraps all the way round a sphere, and you eat every crumb while dodging four spooks, grabbing a golden key to turn the tables. (3 images) |
| <img src="amiga-68k/rj_birthday/rj_birthday-gameplay.png" width="200"> | [RJ's Birthday Bash](amiga-68k/rj_birthday/rj_birthday.md) | game | An arcade party-management game written as a tribute to RJ Mical (Intuition, Amiga, Atari Lynx, 3DO) for his 70th birthday: run the party across six themed rooms of RJ's house, keeping guests happy, catching gifts and serving food. (3 images) |
| <img src="amiga-68k/rock_blaster/rock_blaster-gameplay.png" width="200"> | [Rock Blaster](amiga-68k/rock_blaster/rock_blaster.md) | game | A vector rock shooter: rotate, thrust and blast drifting rocks that split from large to medium to small. (2 images) |
| <img src="amiga-68k/rolling_steel_68k/rolling_steel_68k-gameplay.png" width="200"> | [Rolling Steel](amiga-68k/rolling_steel_68k/rolling_steel_68k.md) | game | A marble-racing game over six 3D courses against one clock, ported from a 3DO original: the classic 68k build (`main_68k.c`, `make ARCH=m68k`) runs the 3DO game code and renderer unchanged, drawing the faces with a CPU software rasteriser with a depth buffer (`glcels_soft.c` on `softcel.c`) in integer maths, so it needs no FPU or 3D library. (3 images) |
| <img src="amiga-68k/rotoball/rotoball-1.png" width="200"> | [Rotoball](amiga-68k/rotoball/rotoball.md) | game | A split-screen futuristic ball sport in the style of Ballblazer: two skimmers on a checkered grid pitch, the top pane showing the CPU opponent's view and the bottom pane the human player's, each skimmer auto-facing the ball. (2 images) |
| <img src="amiga-68k/sky_knights/sky_knights-gameplay.png" width="200"> | [Sky Knights](amiga-68k/sky_knights/sky_knights.md) | game | Aerial jousting on winged mounts for one or two players: strike opponents from above and grab the pods downed foes drop before they hatch. (2 images) |
| <img src="amiga-68k/spectral_keep/spectral_keep-gameplay.png" width="200"> | [Spectral Keep](amiga-68k/spectral_keep/spectral_keep.md) | game | An isometric flip-screen adventure in the style of Knight Lore and Head over Heels: three keeps and 24 rooms, where you carry relics to the throne while avoiding guards, hounds, ghosts, bouncers and spikes. (2 images) |
| <img src="amiga-68k/stakattack/stakattack-gameplay.png" width="200"> | [StakAttack](amiga-68k/stakattack/stakattack.md) | game | A colourful falling-block puzzle in a 12-wide well, with original ProTracker music (`stakattack.mod`) played through ptplayer. (2 images) |
| <img src="amiga-68k/terra_strike/terra_strike-gameplay.png" width="200"> | [Terra Strike](amiga-68k/terra_strike/terra_strike.md) | game | A Zarch / Carrier Command style landscape shooter: lift off from the landing pad, fly over a wrapping fractal island destroying tanks, buildings and ships, and land on the pad again to refuel and repair. (4 images) |
| <img src="amiga-68k/uranus_lander/uranus_lander-gameplay.png" width="200"> | [Uranus Lander](amiga-68k/uranus_lander/uranus_lander.md) | game | A lunar-lander game: rotate and thrust down onto the landing pads of procedurally generated terrain without running out of fuel. (2 images) |
| <img src="amiga-68k/void_trader/void_trader-gameplay.png" width="200"> | [Void Trader](amiga-68k/void_trader/void_trader.md) | game | Space combat and trading in filled 3D: fly with six degrees of freedom, dock at the station to buy and sell, and earn 5000 credits to win. (2 images) |
| <img src="amiga-68k/warden_keep/warden_keep-gameplay.png" width="200"> | [Warden Keep](amiga-68k/warden_keep/warden_keep.md) | game | A clean-room isometric room adventure in the Filmation style (Knight Lore, Head over Heels lineage): walk a single 8x8-tile room, push barrels into place and collect the three jewels. (2 images) |
| <img src="amiga-68k/zork1/zork1-gameplay.png" width="200"> | [Zork I (ZVM)](amiga-68k/zork1/zork1.md) | game | Infocom's Zork I running under ZVM 0.1.0, a Z-machine interpreter, from an AmigaDOS shell window. (2 images) |
| <img src="amiga-68k/boing_ball/boing_ball-1.png" width="200"> | [Boing Ball](amiga-68k/boing_ball/boing_ball.md) | demo | A modern take on the classic Amiga Boing Ball demo: a lit red/white checkered sphere (light from the upper-left-front) bouncing over a perspective grid floor with a depth-scaled shadow, a copper-gradient sky, squash/stretch bounce physics and a synthesised metallic clank. (2 images) |
| <img src="amiga-68k/bouncing_ball/bouncing_ball.png" width="200"> | [Bouncing Ball](amiga-68k/bouncing_ball/bouncing_ball.md) | demo | The simplest bridge demo: a ball bouncing inside a Workbench window, with its whole state exposed for remote tweaking. (1 image) |
| <img src="amiga-68k/disk_benchmark/disk_benchmark.png" width="200"> | [Disk Benchmark](amiga-68k/disk_benchmark/disk_benchmark.md) | tool | A file-system throughput benchmark: it writes and then reads back a test file at a chosen path with dos.library `Write`/`Read`, timing with `DateStamp`, and shows the speeds as bars. (1 image) |
| <img src="amiga-68k/game_of_life/game_of_life-1.png" width="200"> | [Game of Life](amiga-68k/game_of_life/game_of_life.md) | demo | Conway's Game of Life on an 80x60 grid of 5-pixel cells in a Workbench window, double-buffered between two grids. (2 images) |
| <img src="amiga-68k/hubert/hubert-1.png" width="200"> | [hubert](amiga-68k/hubert/hubert.md) | tool | hubert is a small interactive shell for AmigaOS. (2 images) |
| <img src="amiga-68k/launcher/launcher.png" width="200"> | [Launcher](amiga-68k/launcher/launcher.md) | tool | An app launcher in a GadTools ListView window on the Workbench screen. (1 image) |
| <img src="amiga-68k/memory_monitor/memory_monitor.png" width="200"> | [Memory Monitor](amiga-68k/memory_monitor/memory_monitor.md) | tool | A memory monitor that walks Exec's `MemHeader` free lists to report free, total and largest blocks and the number of free fragments for chip and fast RAM, and graphs a history of free chip memory. (1 image) |
| <img src="amiga-68k/plasma/plasma-1.png" width="200"> | [Plasma](amiga-68k/plasma/plasma.md) | demo | Colour-cycling plasma bands on a 320x256, 16-colour screen: 16 horizontal bands whose palette is recomputed from a sine table each frame and loaded with `SetRGB4`. (2 images) |
| <img src="amiga-68k/sfx_player/sfx_player.png" width="200"> | [SFX Player](amiga-68k/sfx_player/sfx_player.md) | tool | A sound-effect player that generates sine, square, sawtooth or noise waveforms (256 samples) in chip RAM and plays them on a Paula channel through audio.device. (1 image) |
| <img src="amiga-68k/starfield/starfield-1.png" width="200"> | [Starfield](amiga-68k/starfield/starfield.md) | demo | A hardware-banging starfield written mostly in 68k assembly (`starfield.asm`): stars radiate from the screen centre on a 320x256, 3-bitplane PAL screen, the Copper draws the gradient background, the Blitter clears the screen, and a starship silhouette crosses periodically. (2 images) |
| <img src="amiga-68k/system_monitor/system_monitor.png" width="200"> | [System Monitor](amiga-68k/system_monitor/system_monitor.md) | tool | A window showing free/total/largest chip and fast memory and the task count, exposed through the bridge as `system_monitor`: variables `frame`, `chip_free`, `fast_free`, `chip_largest`, `fast_largest`, `chip_total`, `fast_total`, `task_count`, `cpu_usage`, `update_delay`, `log_interval` and `status_msg`, hooks `snapshot` and `set_status`, a `stats` memory region, and log lines when chip memory drops or the task count changes. (1 image) |

Not captured: `aga3d` and `ham_raster` (both fail to open their 8-bit LORES screen on this AmiKit setup).

## AmigaOS 4.1 PowerPC

| | Program | Type | About |
|---|---|---|---|
| <img src="amigaos4-ppc/canyon_rescue/canyon_rescue-gameplay.png" width="200"> | [Canyon Rescue](amigaos4-ppc/canyon_rescue/canyon_rescue.md) | game | A rescue flight sim. (2 images) |
| <img src="amigaos4-ppc/emberkeep/emberkeep-gameplay.png" width="200"> | [Emberkeep](amigaos4-ppc/emberkeep/emberkeep.md) | game | A clean-room top-down cavern explorer built around a "lantern in the deep dark": you carry a small burning lantern that lights only a tight area around you. (2 images) |
| <img src="amigaos4-ppc/planet_chomp/planet_chomp-gameplay.png" width="200"> | [Planet Chomp](amigaos4-ppc/planet_chomp/planet_chomp.md) | game | A maze chase that wraps all the way round a small planet: eat every crumb while four spooks (Gloom, Spark, Mist and Moss) hunt you, and grab a golden key to turn the tables. (2 images) |
| <img src="amigaos4-ppc/rolling_steel/rolling_steel-gameplay.png" width="200"> | [Rolling Steel](amigaos4-ppc/rolling_steel/rolling_steel.md) | game | An isometric roll-the-marble racer in the spirit of the 1984 arcade cabinet: six courses share one clock. (2 images) |
| <img src="amigaos4-ppc/spectral_keep/spectral_keep-gameplay.png" width="200"> | [Spectral Keep](amigaos4-ppc/spectral_keep/spectral_keep.md) | game | An isometric flip-screen adventure in the Knight Lore tradition: three keeps and 24 rooms. (2 images) |
| <img src="amigaos4-ppc/void_trader/void_trader-gameplay.png" width="200"> | [Void Trader](amigaos4-ppc/void_trader/void_trader.md) | game | A 3D space trading and combat game in the spirit of Elite: fly between pirates and a trading station, trade cargo, and collect bounties until you reach 5000 credits. (2 images) |
| <img src="amigaos4-ppc/warden_keep/warden_keep-gameplay.png" width="200"> | [Warden Keep](amigaos4-ppc/warden_keep/warden_keep.md) | game | A clean-room isometric "Filmation-style" room puzzle (Fairlight, Knight Lore, Head over Heels lineage): walk an 8×8 stone room tile by tile, push barrels into place and collect the three jewels. (2 images) |
| <img src="amigaos4-ppc/amiga-bridge/amiga-bridge-workbench.png" width="200"> | [AmigaBridge (PPC daemon)](amigaos4-ppc/amiga-bridge/amiga-bridge.md) | app | The Amiga-side half of DevBench: a resident daemon that every app links to through `libbridge` (`ab_init`, `ab_log`, `ab_register_var`, `ab_register_hook`, …) over Exec MsgPorts. (2 images) |
| <img src="amigaos4-ppc/masterwork/masterwork-1.png" width="200"> | [Masterwork](amigaos4-ppc/masterwork/masterwork.md) | app | A two-pane, Directory Opus-style file manager written against plain Intuition/graphics (the button bar is drawn, not gadtools). (2 images) |
| <img src="amigaos4-ppc/networking/networking-virtnet-iperf3.png" width="200"> | [Networking on the OS4 guest: SANA-II drivers](amigaos4-ppc/networking/networking.md) | driver | The QEMU guest runs with two NICs, and Roadshow brings up three interfaces. (3 images) |
| <img src="amigaos4-ppc/organizer/organizer-notes.png" width="200"> | [Organizer](amigaos4-ppc/organizer/organizer.md) | app | A personal notes / tasks / calendar app with three tabs (F1/F2/F3). (3 images) |
| <img src="amigaos4-ppc/python-os4/python-os4-shell.png" width="200"> | [Python 3.12 for AmigaOS 4](amigaos4-ppc/python-os4/python-os4.md) | language port | CPython 3.12.7, cross-compiled for AmigaOS 4.1 PPC with the walkero GCC 11 toolchain in Docker, and shipped as a single stripped executable of about 15 MB (`DH1:python-os4`). (6 images) |
| <img src="amigaos4-ppc/terrain_test/terrain_test-1.png" width="200"> | [Terrain Test](amigaos4-ppc/terrain_test/terrain_test.md) | demo | A one-file voxel landscape flyer with no gameplay. (2 images) |
| <img src="amigaos4-ppc/trapezepdf/trapezepdf-page.png" width="200"> | [TrapezePDF](amigaos4-ppc/trapezepdf/trapezepdf.md) | app | A native PDF viewer for AmigaOS 4, built on MuPDF and cross-compiled in Docker into one static PPC ELF of about 44 MB. (4 images) |

## Atari ST / STE / Falcon

Sister project: the same games ported to the Atari through Amiga-API shim layers, run on a patched Hatari with an agent API. See [atari-st/README.md](atari-st/README.md) and [atari-st/tools](atari-st/tools/README.md).

| | Program | Type | About |
|---|---|---|---|
| <img src="atari-st/ace_pilot/ace_pilot-gameplay.png" width="200"> | [Ace Pilot](atari-st/ace_pilot/ace_pilot.md) | game | A first-person 3D wireframe dogfighting game against enemy biplanes, with ground targets and a split-screen two-player mode. (3 images) |
| <img src="atari-st/bullion_dash/bullion_dash-gameplay.png" width="200"> | [Bullion Dash](atari-st/bullion_dash/bullion_dash.md) | game | A puzzle platformer: collect all the gold, dig traps for the guards and escape, with a built-in level editor (E on the title). (2 images) |
| <img src="atari-st/canyon_rescue/canyon_rescue-gameplay.png" width="200"> | [Canyon Rescue](atari-st/canyon_rescue/canyon_rescue.md) | game | Fly the valleys of a fractal planet and rescue downed pilots, some of whom are Mimics in disguise. (3 images) |
| <img src="atari-st/dot_chase/dot_chase-gameplay.png" width="200"> | [Dot Chase](atari-st/dot_chase/dot_chase.md) | game | A maze chase: a ladybug gathers seeds in a hedge maze while four spiders hunt it, and a flower turns the tables. (3 images) |
| <img src="atari-st/frank_the_frog/frank_the_frog-gameplay.png" width="200"> | [Frank the Frog](atari-st/frank_the_frog/frank_the_frog.md) | game | A road-and-river crossing game: hop Frank through the traffic, then ride logs and lily-pad rafts to the four ponds. (2 images) |
| <img src="atari-st/jump_quest/jump_quest-gameplay.png" width="200"> | [Jump Quest](atari-st/jump_quest/jump_quest.md) | game | RJ and Dale's Jump Quest, a platformer for one or two players taking turns. (3 images) |
| <img src="atari-st/lunar_rider/lunar_rider-gameplay.png" width="200"> | [Lunar Rider](atari-st/lunar_rider/lunar_rider.md) | game | A side-scrolling moon-buggy ride: jump craters, shoot rocks and reach each zone. (3 images) |
| <img src="atari-st/nova_defense/nova_defense-gameplay.png" width="200"> | [Nova Defense](atari-st/nova_defense/nova_defense.md) | game | A fixed-screen alien shooter: 48 aliens in six staggered rows, crystal shields and a passing comet. (3 images) |
| <img src="atari-st/orb_hunter/orb_hunter-gameplay.png" width="200"> | [Orb Hunter](atari-st/orb_hunter/orb_hunter.md) | game | A cavern-exploration platformer with tile-based rooms, power-ups and bosses. (3 images) |
| <img src="atari-st/orbital_patrol/orbital_patrol-gameplay.png" width="200"> | [Orbital Patrol](atari-st/orbital_patrol/orbital_patrol.md) | game | A side-scrolling planet-defence shooter: protect the humans from the abductors across a wraparound world, with a scanner at the top, smart bombs and hyperspace. (3 images) |
| <img src="atari-st/pea_shooter_blast/pea_shooter_blast-gameplay.png" width="200"> | [Pea Shooter Blast](atari-st/pea_shooter_blast/pea_shooter_blast.md) | game | Side-scrolling tank action with platforms, pickups and eight weapon levels over three levels. (3 images) |
| <img src="atari-st/planet_chomp/planet_chomp-gameplay.png" width="200"> | [Planet Chomp](atari-st/planet_chomp/planet_chomp.md) | game | A maze chase on a tiny planet: the maze wraps all the way round a sphere, and you eat every crumb while dodging four spooks, grabbing a golden key to turn the tables. (3 images) |
| <img src="atari-st/rj_birthday/rj_birthday-gameplay.png" width="200"> | [RJ's Birthday Bash](atari-st/rj_birthday/rj_birthday.md) | game | An arcade party-management game written as a tribute to RJ Mical (Intuition, the Amiga, the Atari Lynx, the 3DO) for his 70th birthday: run the party across six themed rooms of RJ's house, keeping guests happy, catching gifts and serving food. (3 images) |
| <img src="atari-st/rock_blaster/rock_blaster-gameplay.png" width="200"> | [Rock Blaster](atari-st/rock_blaster/rock_blaster.md) | game | A vector rock shooter: rotate, thrust and blast drifting rocks that split into smaller ones. (3 images) |
| <img src="atari-st/rolling_steel/rolling_steel-gameplay.png" width="200"> | [Rolling Steel](atari-st/rolling_steel/rolling_steel.md) | game | A marble-racing game over six floating 3D courses against one clock, another of amiga_mcp's 3DO ports (`examples/rolling_steel`). (3 images) |
| <img src="atari-st/sky_knights/sky_knights-gameplay.png" width="200"> | [Sky Knights](atari-st/sky_knights/sky_knights.md) | game | Aerial jousting on winged mounts for one or two players: strike opponents from above and grab the pods they drop before they hatch. (3 images) |
| <img src="atari-st/spectral_keep/spectral_keep-gameplay.png" width="200"> | [Spectral Keep](atari-st/spectral_keep/spectral_keep.md) | game | An isometric flip-screen adventure in the style of Knight Lore: three keeps and 24 rooms, where you carry relics to the throne while avoiding guards, hounds, ghosts, bouncers and spikes. (3 images) |
| <img src="atari-st/stakattack/stakattack-gameplay.png" width="200"> | [StakAttack](atari-st/stakattack/stakattack.md) | game | A falling-gem puzzle game in a 12 x 19 well. (2 images) |
| <img src="atari-st/uranus_lander/uranus_lander-gameplay.png" width="200"> | [Uranus Lander](atari-st/uranus_lander/uranus_lander.md) | game | A lunar-lander game: rotate and thrust down onto the landing pads of generated terrain before the fuel runs out. (3 images) |
| <img src="atari-st/void_trader/void_trader-gameplay.png" width="200"> | [Void Trader](atari-st/void_trader/void_trader.md) | game | Space combat and trading in filled 3D: fly with six degrees of freedom, fight pirates, dock to trade and earn 5000 credits to win. (3 images) |
| <img src="atari-st/st_launcher/st_launcher-1.png" width="200"> | [ST Launcher](atari-st/st_launcher/st_launcher.md) | tool | A menu that runs on the Atari itself: `make_drive.py` reads the same `games.ini` as the host launcher and puts every port on one C: drive (`GAMES\<NAME>\` with each game's files and a 160x100 `THUMB.DAT` made from its screenshot), and `LAUNCHER.PRG` lists them, shows the thumbnail, description and controls, and starts the chosen game with `Pexec`; quitting the game returns to the menu. (3 images) |

## 3DO

Sister project: the games on the 3DO Interactive Multiplayer (ARM60, Portfolio OS), run on a patched, scriptable Opera emulator with its own devbench. See [3do/README.md](3do/README.md) and [3do/devbench](3do/devbench/README.md).

| | Program | Type | About |
|---|---|---|---|
| <img src="3do/ace_pilot/ace_pilot-gameplay.png" width="200"> | [Ace Pilot](3do/ace_pilot/ace_pilot.md) | game | A first-person 3D wireframe dogfighting game: biplanes and blimps over a gridded airfield, with a split-screen two-player mode, ported from the Amiga original (`amiga_mcp examples/ace_pilot`). (2 images) |
| <img src="3do/bullion_dash/bullion_dash-gameplay.png" width="200"> | [Bullion Dash](3do/bullion_dash/bullion_dash.md) | game | A puzzle platformer: collect all the gold, dig traps for the guards and climb out, with a built-in level editor (C on the title). (2 images) |
| <img src="3do/canyon_rescue/canyon_rescue-gameplay.png" width="200"> | [Canyon Rescue](3do/canyon_rescue/canyon_rescue.md) | game | Fly the valleys of a fractal planet and rescue downed pilots, some of whom are Mimics in disguise, ported from the Amiga original (`amiga_mcp examples/canyon_rescue`). (2 images) |
| <img src="3do/dot_chase/dot_chase-gameplay.png" width="200"> | [Dot Chase](3do/dot_chase/dot_chase.md) | game | A dot-eater arcade game: a ladybug gathers seeds in a hedge maze while four spiders hunt it, and a flower turns the tables. (2 images) |
| <img src="3do/frank_the_frog/frank_the_frog-gameplay.png" width="200"> | [Frank the Frog](3do/frank_the_frog/frank_the_frog.md) | game | A road-and-river crossing game: hop Frank through traffic and ride logs and turtles to the homes, with generated music. (2 images) |
| <img src="3do/jump_quest/jump_quest-gameplay.png" width="200"> | [Jump Quest](3do/jump_quest/jump_quest.md) | game | A side-scrolling platformer starring RJ and Dale for one or two players taking turns, with three levels. (2 images) |
| <img src="3do/lunar_rider/lunar_rider-gameplay.png" width="200"> | [Lunar Rider](3do/lunar_rider/lunar_rider.md) | game | A side-scrolling moon-buggy ride: jump craters and rocks and shoot UFOs and meteors on the way to each checkpoint. (2 images) |
| <img src="3do/nova_defense/nova_defense-gameplay.png" width="200"> | [Nova Defense](3do/nova_defense/nova_defense.md) | game | A fixed-screen alien shooter: hold back the descending swarm from behind crystal shields and pick off the comet. (2 images) |
| <img src="3do/orb_hunter/orb_hunter-gameplay.png" width="200"> | [Orb Hunter](3do/orb_hunter/orb_hunter.md) | game | A cavern-exploration platformer: search the caverns room by room and collect power-ups (spring boots, roll form, missiles, bombs) to reach new areas. (4 images) |
| <img src="3do/orbital_patrol/orbital_patrol-gameplay.png" width="200"> | [Orbital Patrol](3do/orbital_patrol/orbital_patrol.md) | game | A side-scrolling planet-defence shooter: protect the humans from abductors across a wrapping world, with a scanner, smart bombs and hyperspace. (2 images) |
| <img src="3do/pea_shooter_blast/pea_shooter_blast-gameplay.png" width="200"> | [Pea Shooter Blast](3do/pea_shooter_blast/pea_shooter_blast.md) | game | Side-scrolling tank action: drive, jump and blast through the enemy lines. (2 images) |
| <img src="3do/planet_chomp/planet_chomp-gameplay.png" width="200"> | [Planet Chomp](3do/planet_chomp/planet_chomp.md) | game | A maze chase on a tiny planet: the maze wraps all the way round a sphere, and you eat every crumb while four spooks (Gloom, Spark, Mist and Moss) hunt you, grabbing a golden key to turn the tables. (3 images) |
| <img src="3do/rj_birthday/rj_birthday-gameplay.png" width="200"> | [RJ's Birthday Bash](3do/rj_birthday/rj_birthday.md) | game | An arcade party game written as a tribute to RJ Mical (Intuition, Amiga, Atari Lynx, 3DO) for his 70th birthday: run the party across six themed rooms of RJ's house. (2 images) |
| <img src="3do/rock_blaster/rock_blaster-gameplay.png" width="200"> | [Rock Blaster](3do/rock_blaster/rock_blaster.md) | game | A vector rock shooter: rotate, thrust and blast drifting rocks that split as they are hit. (2 images) |
| <img src="3do/rolling_steel/rolling_steel-gameplay.png" width="200"> | [Rolling Steel](3do/rolling_steel/rolling_steel.md) | game | A marble racer over six floating courses against one clock that carries over, in the spirit of the 1984 arcade cabinet. (3 images) |
| <img src="3do/rotoball/rotoball-gameplay.png" width="200"> | [Rotoball](3do/rotoball/rotoball.md) | game | A split-screen futuristic ball sport in the style of Ballblazer: the top pane shows the CPU opponent's view and the bottom pane the player's, each skimmer facing the ball. (2 images) |
| <img src="3do/sky_knights/sky_knights-gameplay.png" width="200"> | [Sky Knights](3do/sky_knights/sky_knights.md) | game | Aerial jousting on winged mounts for one or two players: strike opponents from above and collect the eggs. (2 images) |
| <img src="3do/spectral_keep/spectral_keep-gameplay.png" width="200"> | [Spectral Keep](3do/spectral_keep/spectral_keep.md) | game | An isometric flip-screen adventure in the style of Knight Lore and Head over Heels: three keeps and 24 rooms, carrying relics to the throne. (3 images) |
| <img src="3do/stakattack/stakattack-gameplay.png" width="200"> | [StakAttack](3do/stakattack/stakattack.md) | game | A colourful falling-block puzzle in a 12-wide well with original tracker music. (3 images) |
| <img src="3do/uranus_lander/uranus_lander-gameplay.png" width="200"> | [Uranus Lander](3do/uranus_lander/uranus_lander.md) | game | A lunar-lander game: rotate and thrust down onto the landing pads of procedurally generated terrain before the fuel runs out, with ProTracker music. (2 images) |
| <img src="3do/void_trader/void_trader-gameplay.png" width="200"> | [Void Trader](3do/void_trader/void_trader.md) | game | Space combat and trading in filled 3D: fly with six degrees of freedom, fight pirates, dock at the station to trade and earn 5000 credits to win. (3 images) |
| <img src="3do/arcade/arcade-menu.png" width="200"> | [3DO Arcade](3do/arcade/arcade.md) | tool | The arcade disc: a game selector that bundles every Amiga-layer game on one CD. (3 images) |
| <img src="3do/demo/demo-1.png" width="200"> | [CLAUDE x 3DO demo](3do/demo/demo.md) | demo | A small cel-engine demo, written from scratch for the 3DO rather than ported. (2 images) |
| <img src="3do/hello/hello.png" width="200"> | [hello](3do/hello/hello.md) | demo | The starter program every new project is created from (`./3do new` copies it from `sdk/template`): a double-buffered display, controller input and debug logging. (1 image) |

## DevBench web UI

The host side: web UI + MCP server that builds, deploys, launches, logs, inspects and drives
both emulators. See [devbench/README.md](devbench/README.md).

- [DevBench — Dashboard (Classic 68k)](devbench/68k-dashboard.md)
- [DevBench — Files · Browser (Classic 68k)](devbench/68k-files-browser.md)
- [DevBench — FS-UAE native debugger (Classic 68k)](devbench/68k-fsuae.md)
- [DevBench — Inspect · Debug (Classic 68k)](devbench/68k-inspect-debug.md)
- [DevBench — Inspect · Graphics (Classic 68k)](devbench/68k-inspect-graphics.md)
- [DevBench — Settings · Config (Classic 68k)](devbench/68k-settings-config.md)
- [DevBench — Tools · Memory (Classic 68k)](devbench/68k-tools-memory.md)
- [DevBench — About (AmigaOS 4 PPC)](devbench/os4-about.md)
- [DevBench — Dashboard (AmigaOS 4 PPC)](devbench/os4-dashboard.md)
- [DevBench — Debugger (AmigaOS 4 PPC)](devbench/os4-debugger.md)
- [DevBench — Develop (AmigaOS 4 PPC)](devbench/os4-develop.md)
- [DevBench — Files · Browser (AmigaOS 4 PPC)](devbench/os4-files-browser.md)
- [DevBench — Files · Transfer (AmigaOS 4 PPC)](devbench/os4-files-transfer.md)
- [DevBench — Files · File viewer (AmigaOS 4 PPC)](devbench/os4-files-viewer.md)
- [DevBench — Inspect · Debug (AmigaOS 4 PPC)](devbench/os4-inspect-debug.md)
- [DevBench — Inspect · Graphics (AmigaOS 4 PPC)](devbench/os4-inspect-graphics.md)
- [DevBench — Inspect · System (AmigaOS 4 PPC)](devbench/os4-inspect-system.md)
- [DevBench — Logs (AmigaOS 4 PPC)](devbench/os4-logs.md)
- [DevBench — Settings · Config (AmigaOS 4 PPC)](devbench/os4-settings-config.md)
- [DevBench — Settings · Traffic (AmigaOS 4 PPC)](devbench/os4-settings-traffic.md)
- [DevBench — Tools · Memory (AmigaOS 4 PPC)](devbench/os4-tools-memory.md)
- [DevBench — Tools · Shell (AmigaOS 4 PPC)](devbench/os4-tools-shell.md)
- [DevBench — Tools · Tasks (AmigaOS 4 PPC)](devbench/os4-tools-tasks.md)
- [DevBench — Tools · Variables (AmigaOS 4 PPC)](devbench/os4-tools-variables.md)

## How these were captured

`tools/` holds the capture scripts: `shot68k.sh` (FS-UAE window grab, true colour incl. copper
and sprites), `shotos4.sh` (QEMU HMP screendump), `mcp.py` (DevBench MCP calls to launch
programs and inject keys), `capture_devbench.py` + `annotate.py` (headless-Chrome web UI shots
and callout rendering), `write_index.py` (this page).
