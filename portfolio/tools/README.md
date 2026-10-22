# Portfolio capture tools

| Tool | What it does |
|---|---|
| `shot68k.sh OUT.png` | Grabs the FS-UAE window (true colours, copper and sprites included), crops the macOS title bar, scales to 1024 wide |
| `shotos4.sh OUT.png` | QEMU HMP `screendump` of the AmigaOS 4 guest (1280x720) |
| `hmp.sh 'cmd' ...` | Sends QEMU monitor commands (`sendkey ret`, `mouse_move dx dy`, `mouse_button 1`) |
| `mcp.py TOOL '{json}'` | Calls a devbench MCP tool. Default :3001 (68k); `DEVBENCH_MCP=http://localhost:3000/mcp` for OS4 |
| `winid` | Prints the CGWindowID of an app's largest window (`swiftc -O -o winid winid.swift`) |

Rawkeys for `amiga_input_key` (hex): Space 40, Return 44, Esc 45, Up 4C, Down 4D, Right 4E, Left 4F, Left Alt 64, Left Shift 60.
