# Atari ST / STE / Falcon ports

The Amiga games from `examples/` (the [amiga_games](https://github.com/geekychris/amiga_games) submodule) ported to Atari machines in a sister project, [atari_st_games](https://github.com/geekychris/atari_st_games), and run in a patched Hatari, [hatari_augmented](https://github.com/geekychris/hatari_augmented), with an HTTP agent API. Each folder has the game's PNGs and one markdown file describing every image. Captured 2026-10-20 in Hatari through the agent API (`GET /screen`, scaled 2x), each game on the machine `games.ini` gives it.

## How the ports work

The Amiga versions are the originals. The ports keep their game logic and, mostly, their drawing code, and run it on small Atari layers that stand in for the AmigaOS pieces the games use:

- **`st_port`** (ST and STE): Amiga header shims so unmodified code compiles; the graphics.library subset (`SetAPen`, `Move`, `Draw`, `RectFill`, `Text`...) on ST low resolution, keeping the 320x256 Amiga coordinates and mapping Y to 200 lines; its own IKBD interrupt handler for keys and joysticks; a Paula emulation on STE DMA sound (the real register offsets, so code poking `custom.aud[]` works) with a C ProTracker player; AmigaDOS `Open`/`Read`/`Seek` on GEMDOS with 8.3 names; STE blitter helpers for scrolling; NatFeats logging. The plain-ST ports (Uranus Lander, Nova Defense, Frank the Frog) replace Paula with YM2149 sound.
- **`falcon_port`** (Falcon030): 16-bit true-colour screens (320x240 VGA, triple buffered) with the same graphics subset through a 256-pen RGB565 table, plus polygon fills for the 3D games. Canyon Rescue, Void Trader and Ace Pilot are AGA games, so they go to the Falcon.
- **`falcon_3do`**: Spectral Keep, Rolling Steel and Planet Chomp are 3DO games with a classic 68k AmigaOS build in amiga_mcp. This layer supplies that build's two machine files on the Falcon, so the games and their `main_68k.c` compile unchanged. Rolling Steel and Planet Chomp draw their 3D in software sized for an Amiga 68060, so they run on an accelerated Falcon: 68060 at 32 MHz with 64 MB TT-RAM, CT60-style (`--cpulevel 6 --cpuclock 32 --addr24 off --ttram 64`).

Machines: ST (EmuTOS 192k), STE (EmuTOS 1024k), Falcon030 (14 MB, VGA, no DSP) and the 68060 Falcon. Work was done and tested through the agent API: bots and autopilots (`nova_defense/bot.py`, `uranus_lander/autopilot.py`), scenario tests (`canyon_rescue/rescue_test.py`), NatFeats log lines that give the address of each game's state, `/mem` writes in place of the Amiga bridge hooks, and the Hatari profiler for speed work. [Hatari agent tooling](tools/README.md) has the API and its two Tk windows.

- [Games and the launcher](#entries): 21 entries
- [Hatari agent tooling](tools/README.md): 5 screens, each plain and annotated

## Entries

| | Program | Machine | Type | About |
|---|---|---|---|---|
| <img src="uranus_lander/uranus_lander-gameplay.png" width="200"> | [Uranus Lander](uranus_lander/uranus_lander.md) | ST | game | A lunar-lander game: rotate and thrust down onto the landing pads of generated terrain before the fuel runs out. (3 images) |
| <img src="nova_defense/nova_defense-gameplay.png" width="200"> | [Nova Defense](nova_defense/nova_defense.md) | ST | game | A fixed-screen alien shooter: 48 aliens in six staggered rows, crystal shields and a passing comet. (3 images) |
| <img src="frank_the_frog/frank_the_frog-gameplay.png" width="200"> | [Frank the Frog](frank_the_frog/frank_the_frog.md) | ST | game | A road-and-river crossing game: hop Frank through the traffic, then ride logs and lily-pad rafts to the four ponds. (2 images) |
| <img src="rock_blaster/rock_blaster-gameplay.png" width="200"> | [Rock Blaster](rock_blaster/rock_blaster.md) | STE | game | A vector rock shooter: rotate, thrust and blast drifting rocks that split into smaller ones. (3 images) |
| <img src="orbital_patrol/orbital_patrol-gameplay.png" width="200"> | [Orbital Patrol](orbital_patrol/orbital_patrol.md) | STE | game | A side-scrolling planet-defence shooter: protect the humans from the abductors across a wraparound world, with a scanner at the top, smart bombs and hyperspace. (3 images) |
| <img src="jump_quest/jump_quest-gameplay.png" width="200"> | [Jump Quest](jump_quest/jump_quest.md) | STE | game | RJ and Dale's Jump Quest, a platformer for one or two players taking turns. (3 images) |
| <img src="stakattack/stakattack-gameplay.png" width="200"> | [StakAttack](stakattack/stakattack.md) | STE | game | A falling-gem puzzle game in a 12 x 19 well. (2 images) |
| <img src="dot_chase/dot_chase-gameplay.png" width="200"> | [Dot Chase](dot_chase/dot_chase.md) | STE | game | A maze chase: a ladybug gathers seeds in a hedge maze while four spiders hunt it, and a flower turns the tables. (3 images) |
| <img src="lunar_rider/lunar_rider-gameplay.png" width="200"> | [Lunar Rider](lunar_rider/lunar_rider.md) | STE | game | A side-scrolling moon-buggy ride: jump craters, shoot rocks and reach each zone. (3 images) |
| <img src="pea_shooter_blast/pea_shooter_blast-gameplay.png" width="200"> | [Pea Shooter Blast](pea_shooter_blast/pea_shooter_blast.md) | STE | game | Side-scrolling tank action with platforms, pickups and eight weapon levels over three levels. (3 images) |
| <img src="sky_knights/sky_knights-gameplay.png" width="200"> | [Sky Knights](sky_knights/sky_knights.md) | STE | game | Aerial jousting on winged mounts for one or two players: strike opponents from above and grab the pods they drop before they hatch. (3 images) |
| <img src="orb_hunter/orb_hunter-gameplay.png" width="200"> | [Orb Hunter](orb_hunter/orb_hunter.md) | STE | game | A cavern-exploration platformer with tile-based rooms, power-ups and bosses. (3 images) |
| <img src="bullion_dash/bullion_dash-gameplay.png" width="200"> | [Bullion Dash](bullion_dash/bullion_dash.md) | STE | game | A puzzle platformer: collect all the gold, dig traps for the guards and escape, with a built-in level editor (E on the title). (2 images) |
| <img src="rj_birthday/rj_birthday-gameplay.png" width="200"> | [RJ's Birthday Bash](rj_birthday/rj_birthday.md) | STE | game | An arcade party-management game written as a tribute to RJ Mical (Intuition, the Amiga, the Atari Lynx, the 3DO) for his 70th birthday: run the party across six themed rooms of RJ's house, keeping guests happy, catching gifts and serving food. (3 images) |
| <img src="canyon_rescue/canyon_rescue-gameplay.png" width="200"> | [Canyon Rescue](canyon_rescue/canyon_rescue.md) | Falcon030 | game | Fly the valleys of a fractal planet and rescue downed pilots, some of whom are Mimics in disguise. (3 images) |
| <img src="void_trader/void_trader-gameplay.png" width="200"> | [Void Trader](void_trader/void_trader.md) | Falcon030 | game | Space combat and trading in filled 3D: fly with six degrees of freedom, fight pirates, dock to trade and earn 5000 credits to win. (3 images) |
| <img src="ace_pilot/ace_pilot-gameplay.png" width="200"> | [Ace Pilot](ace_pilot/ace_pilot.md) | Falcon030 | game | A first-person 3D wireframe dogfighting game against enemy biplanes, with ground targets and a split-screen two-player mode. (3 images) |
| <img src="spectral_keep/spectral_keep-gameplay.png" width="200"> | [Spectral Keep](spectral_keep/spectral_keep.md) | Falcon030 | game | An isometric flip-screen adventure in the style of Knight Lore: three keeps and 24 rooms, where you carry relics to the throne while avoiding guards, hounds, ghosts, bouncers and spikes. (3 images) |
| <img src="rolling_steel/rolling_steel-gameplay.png" width="200"> | [Rolling Steel](rolling_steel/rolling_steel.md) | Falcon + 68060 (CT60) | game | A marble-racing game over six floating 3D courses against one clock, another of amiga_mcp's 3DO ports (`examples/rolling_steel`). (3 images) |
| <img src="planet_chomp/planet_chomp-gameplay.png" width="200"> | [Planet Chomp](planet_chomp/planet_chomp.md) | Falcon + 68060 (CT60) | game | A maze chase on a tiny planet: the maze wraps all the way round a sphere, and you eat every crumb while dodging four spooks, grabbing a golden key to turn the tables. (3 images) |
| <img src="st_launcher/st_launcher-1.png" width="200"> | [ST Launcher](st_launcher/st_launcher.md) | STE | tool | A menu that runs on the Atari itself: `make_drive.py` reads the same `games.ini` as the host launcher and puts every port on one C: drive (`GAMES\<NAME>\` with each game's files and a 160x100 `THUMB.DAT` made from its screenshot), and `LAUNCHER.PRG` lists them, shows the thumbnail, description and controls, and starts the chosen game with `Pexec`; quitting the game returns to the menu. (3 images) |

| <img src="tools/agent-console-debugger.png" width="200"> | [Hatari agent tooling](tools/README.md) | host (macOS) | tool | The agent API, the Tk agent console (`hatari_gui.py`) and the host game launcher (`launcher.py`). (10 images) |

Not captured: `gemdemo` (a GEM VDI showcase) and `interact` (the agent-API test target) have no prebuilt `PRG`, and `make` failed on this Mac because the m68k-atari-mint cross compiler in `~/computers/atari-cc` is an x86_64 binary and doesn't run here ("Bad CPU type in executable").
