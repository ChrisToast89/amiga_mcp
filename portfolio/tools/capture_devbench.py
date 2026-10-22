#!/usr/bin/env python3
"""capture_devbench.py - capture every devbench web-UI screen + write annotation specs.

  capture_devbench.py os4|68k [screen-name ...]

Needs headless Chrome already started by webui_shot.py start:
  DEVBENCH_UI=http://localhost:3000/ CDP_PORT=9334 webui_shot.py start   # os4
  DEVBENCH_UI=http://localhost:3001/ CDP_PORT=9335 webui_shot.py start   # 68k

For each screen: switch tab/sub-tab, run read-only "prep" JS (list/refresh
calls only - nothing that launches, writes, injects input or touches the
emulator), poll until the data is on screen, screenshot at SCALE=2, then read
each callout element's getBoundingClientRect() and write
portfolio/devbench/annotations/<name>.json for annotate.py.
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import webui_shot as w

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "devbench")
ANN = os.path.join(OUT, "annotations")
TARGETS = {
    "os4": dict(port=9334, label="AmigaOS 4 PPC", sub="AmigaOS 4.1 on QEMU sam460ex · profile qemu-os4 · :3000"),
    "68k": dict(port=9335, label="Classic 68k", sub="AmigaOS 3.x on FS-UAE · profile local-fsuae · :3001"),
}

# Resolve a callout spec to a CSS-px rect (union of all matched, visible elements).
#   "sel"            querySelectorAll(sel)
#   "card:sel"       closest .card of the first match
#   "up:N:sel"       N-th ancestor of the first match
#   "a || b"         union of several specs
RESOLVE_JS = r"""
(function(specs){
  function els(s){
    s=s.trim();
    if(s.startsWith('card:')){const e=document.querySelector(s.slice(5));return e?[e.closest('.card')||e]:[];}
    if(s.startsWith('up:')){const m=s.match(/^up:(\d+):(.*)$/);let e=document.querySelector(m[2]);for(let i=0;e&&i<+m[1];i++)e=e.parentElement;return e?[e]:[];}
    return [...document.querySelectorAll(s)];
  }
  return specs.map(spec=>{
    let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;
    spec.split('||').forEach(p=>els(p).forEach(e=>{const r=e.getBoundingClientRect(); if(r.width<1||r.height<1)return;
      x0=Math.min(x0,r.left);y0=Math.min(y0,r.top);x1=Math.max(x1,r.right);y1=Math.max(y1,r.bottom);}));
    return x1<0?null:[x0,y0,x1-x0,y1-y0];
  });
})(%s)
"""

HEADER = [
    ("#platformLabel", "Platform badge",
     "Which Amiga this devbench drives, from the active profile's build arch; the stripe along the top uses the same colour (orange = PPC, blue = 68k)."),
    ("#sysInfo", "Free memory",
     "Free chip and fast RAM from the last bridge heartbeat (HB line)."),
    ("up:1:#emuDot", "Emulator status", "Whether the devbench-managed emulator process is running."),
    ("#archBadge", "Arch · profile", "Target CPU architecture and active devbench.toml profile."),
    ("up:1:#connDot", "Bridge tri-state",
     "Red = serial disconnected, yellow = serial linked but no bridge traffic, green = bridge heartbeats flowing (pulses on each heartbeat), amber = bridge silent."),
]


def S(name, tab, sub=None, prep=None, wait=None, items=(), tall=False, targets=("os4", "68k"), title=None, settle=1.0):
    return dict(name=name, tab=tab, sub=sub, prep=prep, wait=wait, items=list(items), tall=tall,
                targets=targets, title=title, settle=settle)


def file_name(target, s):
    if s["name"] in ("dashboard", "logs", "develop", "debugger", "fsuae", "about", "files-viewer"):
        return f"{target}-{s['name']}"
    return f"{target}-{s['tab']}-{s['sub'].split('-', 1)[1]}"



MEM_ITEMS = [
          ("#memAddr || #memSize", "Address & size", "Start address (hex) and byte count to read."),
          ("up:1:#memAnnotate || .mem-controls .toggle-wrap", "Annotate registers", "Labels known custom-chip / CIA registers in the dump."),
          (".mem-bookmarks", "Bookmarks", "One-click addresses: CIA-A/B, ExecBase pointer, ROM start, vectors."),
          ("up:1:#memWriteAddr", "Write", "Write hex bytes to an address (RAM only, validated with TypeOfMem) (MCP: amiga_write_memory)."),
          ("#hexDump", "Hex dump", "Hex + ASCII view of the bytes read through the bridge (MCP: amiga_inspect_memory)."),
      ]

SCREENS = [
    S("dashboard", "dashboard", title="Dashboard",
      prep="(async()=>{await refreshCapabilities(); cmdQuick('PING');})()",
      wait="document.getElementById('dashCaps').textContent.includes('Version') && !document.getElementById('cmdOutput').textContent.startsWith('Sending')",
      items=HEADER + [
          ("#tabBar", "Tab bar", "Dashboard, Logs, Files, Tools, Inspect, Develop, Debugger, Settings (plus FS-UAE when a patched FS-UAE's debug RPC is reachable)."),
          ("card:#dashSerial", "Connection", "Serial/TCP link to the bridge daemon: host, port, log-buffer size and number of tracked variables."),
          ("card:#dashHbTick", "System status", "Latest heartbeat tick and free chip / fast memory reported by the daemon."),
          ("card:#dashClients", "Clients", "Programs registered with the bridge via ab_init() (MCP: amiga_list_clients)."),
          ("card:#dashCaps", "Bridge capabilities", "Daemon version, protocol level, max line length and every supported command, from CAPABILITIES (MCP: amiga_capabilities)."),
          ("card:#emuStartBtn", "Emulator control", "Status, PID and uptime of the emulator, with Start / Restart / Stop (MCP: amiga_emulator_*)."),
          ("card:#cmdInput", "Send command", "Raw bridge protocol console with one-click PING, LISTTASKS, LISTLIBS, MEMMAP… and the reply shown underneath."),
      ]),
    S("logs", "logs", title="Logs", targets=("os4",),
      wait="document.querySelectorAll('#logContainer > *').length > 5",
      items=[
          (".log-filter-btn", "Level filters", "Toggle ALL / DEBUG / INFO / WARN / ERROR messages."),
          ("#logClientFilter", "Client filter", "Show only one bridge client's messages."),
          ("#logSearch", "Search", "Live text filter over the buffered log."),
          ("up:1:#logAutoScroll", "Auto-scroll", "Follow new messages as they stream in over SSE."),
          ("#logContainer", "Live log stream", "CLOG lines from apps (AB_I/AB_W/AB_E…) plus daemon messages, with timestamp, level and client (MCP: amiga_log / amiga_watch_logs / amiga_tail)."),
      ]),
    S("files-browser", "files", "files-browser", title="Files · Browser",
      prep="(async()=>{navigateDir('SYS:');})()",
      wait="document.querySelectorAll('#fileList .file-row, #fileList > div').length > 3 && !document.getElementById('fileList').textContent.includes('Loading')",
      settle=1.5,
      items=[
          ("#fileTree", "Volumes & assigns", "Mounted volumes and standard assigns; click one to list it (MCP: amiga_list_volumes)."),
          ("#fileBreadcrumb", "Current path", "Breadcrumb of the directory being listed."),
          (".file-header", "Columns", "Name, size, date, protection bits and per-file actions."),
          ("#fileList .file-row", "Directory listing", "LISTDIR result from the bridge (MCP: amiga_list_dir)."),
          ("up:0:#fileList .file-row:not(.dir) > :last-child", "File actions", "Per-file buttons: View, Edit (text), Run (executables), CRC, Ren(ame), Copy (MCP: amiga_read_file / amiga_run / amiga_checksum / amiga_rename / amiga_copy)."),
      ]),
    S("files-viewer", "files", "files-browser", title="Files · File viewer", targets=("os4",),
      prep="(async()=>{navigateDir('S:'); await new Promise(r=>setTimeout(r,2500)); fileView('S:Startup-Sequence', true);})()",
      wait="document.querySelector('.file-modal-overlay .file-modal-body') && document.querySelector('.file-modal-overlay .file-modal-body').textContent.length>50",
      settle=1.5,
      items=[
          (".file-modal-overlay .file-modal-header", "File & close", "Path of the Amiga file being viewed, and Close."),
          (".file-modal-overlay .file-modal-body", "Contents", "The file read over the bridge — here S:Startup-Sequence (MCP: amiga_read_file)."),
      ]),
    S("files-transfer", "files", "files-transfer", title="Files · Transfer", targets=("os4",),
      items=[
          ("up:1:input[name=xferDir]", "Direction", "Push host → Amiga or pull Amiga → host."),
          ("up:1:#xferSource", "Source", "Host path or glob (push), or Amiga path (pull)."),
          ("up:1:#xferDest", "Destination", "Amiga path such as DH2:Dev/ (push) or host path (pull)."),
          ("#xferBtn", "Transfer", "Sends the file(s) over the serial bridge — for setups with no shared folder (MCP: amiga_transfer / amiga_push_file / amiga_pull_file)."),
          ("card:#xferHistory", "History", "Transfers done in this session."),
      ]),
    S("tools-memory", "tools", "tools-memory", title="Tools · Memory", targets=("os4",),
      items=MEM_ITEMS),
    S("tools-memory", "tools", "tools-memory", title="Tools · Memory", targets=("68k",),
      prep="(async()=>{document.getElementById('memAddr').value='00F80000'; await readMemory();})()",
      wait="!/Reading|No data/.test(document.getElementById('hexDump').textContent)",
      items=MEM_ITEMS),
    S("tools-variables", "tools", "tools-variables", title="Tools · Variables", targets=("os4",),
      items=[
          ("up:1:#varAutoRefresh", "Auto-refresh", "Re-reads registered variables periodically."),
          ("#varTable thead", "Variable table", "Client, name, type, value and a Set action for every variable apps expose with ab_register_var()."),
          ("#varBody", "Values", "Empty here: the running clients registered no variables (MCP: amiga_get_var / amiga_set_var)."),
      ]),
    S("tools-shell", "tools", "tools-shell", title="Tools · Shell", targets=("os4",),
      wait="document.getElementById('shellNotRunning').style.display!='none' || document.getElementById('shellRunning').style.display!='none'",
      items=[
          ("#shellNotRunning .card || #shellRunning", "Shell proxy", "Interactive AmigaDOS shell via the shell_proxy bridge client. It isn't running in this capture, so the tab offers to launch it."),
      ]),
    S("tools-tasks", "tools", "tools-tasks", title="Tools · Tasks", targets=("os4",),
      prep="(async()=>{await refreshTasks();})()",
      wait="document.querySelectorAll('#taskBody tr').length > 5",
      items=[
          ("up:2:#taskAutoRefresh", "Refresh / auto-refresh", "Re-read the Exec task list on demand or every few seconds."),
          ("#taskCount", "Count", "Number of tasks and processes."),
          ("#taskTable thead", "Task table", "Name, priority, state (ready / waiting / running) and stack size for every Exec task (MCP: amiga_list_tasks)."),
          ("#taskBody tr:first-child", "Task row", "One row per task or process from LISTTASKS."),
      ]),
    S("inspect-graphics", "inspect", "inspect-graphics", title="Inspect · Graphics", targets=("os4",),
      items=[
          ("card:#toolScrWindow", "Screenshot", "Capture the whole screen or one window via the bridge (MCP: amiga_screenshot)."),
          ("card:#toolPalResult", "Palette", "Read the screen's colour registers (MCP: amiga_get_palette)."),
          ("card:#toolCopperResult", "Copper list", "Decodes the active copper list (MOVE/WAIT/SKIP) — a classic-chipset feature (MCP: amiga_copper_list)."),
          ("card:#toolSprResult", "Sprite inspector", "Hardware sprite state (MCP: amiga_sprites)."),
          ("card:#bmpAddr", "Bitmap viewer", "Render raw planar memory at an address as an image."),
          ("card:#iffPicker", "IFF viewer", "Decode an ILBM file on the Amiga and show it."),
          ("card:#vdiffThreshold", "Visual diff", "Capture A and B and highlight changed pixels."),
      ]),
    S("inspect-graphics", "inspect", "inspect-graphics", title="Inspect · Graphics", targets=("68k",),
      prep="(async()=>{await toolPalette(); await toolCopper(); await toolSprites();})()",
      wait="!/Reading/.test(document.getElementById('toolPalResult').textContent+document.getElementById('toolCopperResult').textContent+document.getElementById('toolSprResult').textContent) && document.getElementById('toolCopperResult').textContent.length>20",
      settle=1.5,
      items=[
          ("card:#toolScrWindow", "Screenshot", "Capture the whole screen or one window via the bridge (MCP: amiga_screenshot)."),
          ("#toolPalResult", "Palette", "The screen's colour registers as swatches (MCP: amiga_get_palette / amiga_set_palette)."),
          ("#toolCopperResult", "Copper list", "The active copper list (GfxBase ActiView → LOFCprList) decoded instruction by instruction (MCP: amiga_copper_list)."),
          ("#toolSprResult", "Sprite inspector", "Hardware sprite state, including the Intuition mouse pointer (MCP: amiga_sprites)."),
          ("card:#bmpAddr", "Bitmap viewer", "Render raw planar memory at an address as an image."),
          ("card:#iffPicker", "IFF viewer", "Decode an ILBM file on the Amiga and show it."),
          ("card:#vdiffThreshold", "Visual diff", "Capture A and B and highlight changed pixels."),
      ]),
    S("inspect-system", "inspect", "inspect-system", title="Inspect · System", tall=True, targets=("os4",),
      prep="""(async()=>{const f=[toolSysInfo,toolBridgeInfo,toolVolumesExt,toolExecPorts,intuiRefreshScreens,libdevRefresh,assignRefresh,fontRefresh,localeRefresh,arexxListPorts];
               for(const fn of f){try{await fn();}catch(e){}}})()""",
      wait="document.getElementById('sysinfoResult').textContent.length>20 && document.getElementById('libdevList').textContent.length>20",
      settle=2.0,
      items=[
          ("card:#sysinfoResult", "System info", "Free chip / fast RAM, bridge client count, the task list and the loaded libraries in one view (MCP: amiga_sysinfo)."),
          ("card:#bridgeInfoResult", "Bridge info", "Daemon version and uptime (MCP: amiga_version / amiga_uptime)."),
          ("card:#volumesExtResult", "Volumes", "Mounted volumes with size and free space (MCP: amiga_list_volumes)."),
          ("card:#execPortsResult", "Exec ports", "Public message ports (MCP: amiga_list_ports)."),
          ("card:#intuiScreens", "Intuition inspector", "Screens → windows → gadgets, with front/back/move/size actions (MCP: amiga_list_screens / amiga_list_screen_windows / amiga_list_gadgets)."),
          ("card:#inputRawKey", "Input injection", "Send key presses and mouse moves/clicks through input.device (MCP: amiga_input_key / amiga_input_click)."),
          ("card:#libdevList", "Library / device inspector", "Loaded libraries or devices with version and open count; click for details (MCP: amiga_list_libs / amiga_lib_info)."),
          ("card:#assignList", "Assign manager", "Logical assigns and their targets; add or change them (MCP: amiga_list_assigns / amiga_assign)."),
          ("card:#fontList || card:#localeList || card:#arexxPort || card:#clipText", "Fonts, locale, ARexx, clipboard", "Font and catalog browsers, ARexx port list + command sender, clipboard get/set (MCP: amiga_arexx_ports / amiga_arexx_send)."),
          ("card:#startupFile || card:#prefsList || card:#bootlogResult || card:#tailPicker || card:#checksumPicker || card:#protectPicker", "Files & boot",
           "Startup-sequence editor, ENV: prefs, boot log, live file tail, checksum and protection bits (MCP: amiga_tail / amiga_checksum / amiga_protect)."),
      ]),
    S("inspect-debug", "inspect", "inspect-debug", title="Inspect · Debug", tall=True, targets=("os4",),
      prep="(async()=>{try{await toolMemMap();}catch(e){} try{await toolCrash();}catch(e){}})()",
      wait="document.getElementById('memmapResult').textContent.length>20",
      settle=1.5,
      items=[
          ("card:#symProject", "Symbol table", "Load a project's symbols, look up addresses, list functions and structs (MCP: amiga_load_symbols / amiga_lookup_symbol)."),
          ("card:#toolDisasmAddr", "Disassembler", "Disassemble memory, annotated with symbols when loaded (MCP: amiga_disassemble)."),
          ("card:#toolCrashResult", "Crash report", "Bridge crash handler: enable, check the last crash (MCP: amiga_last_crash)."),
          ("card:#memmapResult", "Memory map", "Exec memory lists: regions, attributes and free/used (MEMMAP)."),
          ("card:#searchPattern || card:#stackTask || card:#snapAddr", "Memory search / stack / diff", "Search for a byte pattern, check a task's stack use, snapshot and diff memory."),
          ("card:#chipRegsResult || card:#audioChannels", "Chip registers & audio", "Classic custom-chip state (DMACON, INTENA…) and Paula channels — meaningful on 68k targets."),
          ("card:#snoopLog || card:#chiplogResult", "SnoopDos & chip logger", "Trace OpenLibrary/Open/Lock… calls via SetFunction patches; log custom-chip writes."),
          ("card:#toolResClient || card:#toolPerfClient || card:#poolResult", "Resources, profiler, pools", "Per-client resource tracking, performance report and memory-pool tracking (MCP: amiga_list_resources / amiga_perf_report)."),
      ]),
    S("inspect-debug", "inspect", "inspect-debug", title="Inspect · Debug", tall=True, targets=("68k",),
      prep="(async()=>{for(const fn of [toolMemMap,toolChipRegs,audioRefresh,toolDisasm,toolCrash]){try{await fn();}catch(e){}}})()",
      wait="document.getElementById('memmapResult').textContent.length>20 && document.getElementById('chipRegsResult').textContent.length>20 && document.getElementById('toolDisasmResult').textContent.length>20",
      settle=1.5,
      items=[
          ("card:#symProject", "Symbol table", "Load a project's symbols, look up addresses, list functions and structs (MCP: amiga_load_symbols / amiga_lookup_symbol)."),
          ("#toolDisasmResult", "Disassembler", "68k disassembly of Kickstart ROM at $FC0000 (MCP: amiga_disassemble)."),
          ("card:#toolCrashResult", "Crash report", "Bridge crash handler: enable, check the last crash (MCP: amiga_last_crash)."),
          ("#memmapResult", "Memory map", "Exec memory lists: chip, fast and ROM regions with free/used (MEMMAP)."),
          ("#chipRegsResult", "Chip registers", "Read-safe custom-chip registers (DMACONR, INTENAR, INTREQR, VHPOSR, …) with bit decoding."),
          ("card:#audioChannels", "Audio inspector", "Paula's four channels: DMA state, period, volume; read sample data from chip RAM (MCP: amiga_audio_channels / amiga_audio_sample)."),
          ("card:#snoopLog || card:#chiplogResult", "SnoopDos & chip logger", "Trace OpenLibrary/Open/Lock… calls via SetFunction patches; log custom-chip writes."),
          ("card:#toolResClient || card:#toolPerfClient || card:#poolResult", "Resources, profiler, pools", "Per-client resource tracking, performance report and memory-pool tracking (MCP: amiga_list_resources / amiga_perf_report)."),
      ]),
    S("develop", "develop", title="Develop", targets=("os4",),
      wait="document.getElementById('toolRunProject').options.length > 1",
      items=[
          ("card:#toolRunProject", "Build & run", "Pick a project from examples/ and run it on the Amiga (MCP: amiga_run; amiga_build_deploy_run for the full loop)."),
          ("card:#toolNewName", "New project", "Scaffold a new bridge-enabled app from a template (MCP: amiga_create_project)."),
          ("card:#testResults", "Test harness", "Live results from apps using ab_test_begin() / AB_ASSERT() / ab_test_end() (MCP: amiga_run_tests)."),
      ]),
    S("debugger", "debugger", title="Debugger", targets=("os4",),
      items=[
          ("up:1:#dbgTarget", "Target & symbols", "Pick a bridge client, Launch / Attach / Launch & Attach / Detach, and load the project's symbols (MCP: amiga_debug_attach / amiga_load_symbols)."),
          ("up:1:#dbgContBtn", "Run control", "Continue (F5), Break (F9), Step Into (F11), Step Over (F10) (MCP: amiga_continue / amiga_step / amiga_next)."),
          ("#dbgStatus", "State", "Detached here: no program is attached in this capture."),
          ("up:1:#dbgSourceView", "Source view", "Source files from the symbols; click the gutter to set breakpoints."),
          ("up:1:#dbgRegs", "Registers", "CPU registers when the target is stopped."),
          ("up:1:#dbgCallStack || up:1:#dbgVars", "Call stack & variables", "Backtrace and locals at the stop (MCP: amiga_backtrace)."),
          ("up:1:#dbgBpList", "Breakpoints", "Add by address or function name (MCP: amiga_set_breakpoint)."),
      ]),
    S("settings-config", "settings", "settings-config", title="Settings · Config",
      wait="document.getElementById('cfgSerialHost').value.length>0 && document.getElementById('emuConfigEditor').value.length>0",
      settle=1.5,
      items=[
          ("#cfgSerialMode || #cfgSerialHost || #cfgSerialPort", "Serial link", "TCP or PTY, and the host:port the emulator exposes the Amiga serial port on."),
          ("#cfgEmuBin || #cfgEmuConf || #cfgAutoStart", "Emulator", "Emulator binary / launcher, its config file, and whether devbench starts it."),
          ("#cfgCrashAutoEnable", "Crash handler", "Enable the bridge's crash handler automatically when the daemon starts."),
          ("#cfgDeployDir", "Deploy dir", "Where builds are deployed: a shared folder (68k) or the dev HDF written with xdftool (OS4)."),
          ("card:#emuConfigEditor", "Emulator config editor", "Edits the emulator config file named in the profile; Save, Reload, or Save & Restart."),
      ]),
    S("settings-traffic", "settings", "settings-traffic", title="Settings · Traffic", targets=("os4",),
      prep="""(async()=>{document.getElementById('trafficKind').value='mcp'; await trafficLoad();
               const rows=[...document.querySelectorAll('#trafficList tr')];
               const r=rows.find(r=>/list_tasks|list_clients|ping|status|sysinfo|log/.test(r.textContent))||rows[0];
               if(r) r.click();})()""",
      wait="document.getElementById('trafficDetail').textContent.includes('Request') || document.getElementById('trafficDetail').textContent.includes('Response')",
      settle=1.5,
      items=[
          ("#trafficKind", "Kind filter", "All, MCP tool calls only, or REST API calls only."),
          ("#trafficSearch", "Search", "Free-text search over the logged requests."),
          ("#trafficCount", "Entry count", "Total entries in the traffic log."),
          ("up:3:#trafficList", "Request list", "Every MCP call (e.g. from Claude Code) and REST call: time, type, tool/path, duration, status."),
          ("up:1:#trafficDetail", "Entry detail", "The selected call's arguments (Request) and the result returned (Response)."),
          ("#trafficDetail button", "Replay", "Re-issue the same call — handy for repeating an MCP request Claude made."),
      ]),
    S("about", "dashboard", title="About", targets=("os4",),
      prep="(async()=>{showAbout();})()",
      wait="document.querySelector('.file-modal-overlay')",
      items=[
          (".file-modal-overlay .file-modal", "About AmigaDevBench", "Opened from the logo or About button: a tribute to the people behind the Amiga."),
      ]),
    S("fsuae", "fsuae", title="FS-UAE native debugger", targets=("68k",),
      wait="document.getElementById('fsuaeStatusInline') && document.getElementById('fsuaeStatusInline').textContent.length>0",
      items=[
          ("#fsuaeUnavailable", "RPC not available",
           "This tab drives a patched FS-UAE's debug RPC (CPU, breakpoints, watchpoints, memory, chipset, save states). The FS-UAE running here doesn't expose it, so the tab shows how to enable it; the tab is normally hidden in that case."),
      ]),
]


def capture(target, only=None):
    t = TARGETS[target]
    c = w.CDP(t["port"])
    os.makedirs(ANN, exist_ok=True)
    done = []
    for s in SCREENS:
        if target not in s["targets"] or (only and s["name"] not in only):
            continue
        name = file_name(target, s)
        c.viewport()
        c.js("document.querySelectorAll('.file-modal-overlay').forEach(e=>e.remove())")
        if s["tab"] == "fsuae":
            c.js("document.querySelectorAll('#tabBar > .tab').forEach(t=>t.classList.remove('active'));"
                 "document.querySelectorAll('.content > .tab-panel').forEach(p=>p.classList.remove('active'));"
                 "document.getElementById('panel-fsuae').classList.add('active'); fsuaeProbe();")
            time.sleep(1.5)
        else:
            c.goto_tab(s["tab"], s["sub"], settle=1.0)
        if s["prep"]:
            try:
                c.js(s["prep"], await_promise=True)
            except Exception as e:
                print("  prep error:", e)
        ok = c.wait_for(s["wait"], timeout=40) if s["wait"] else True
        time.sleep(s["settle"])
        if s["tall"]:
            top = c.js(f"document.getElementById('panel-{s['tab']}').getBoundingClientRect().top")
            sh = c.js(f"document.getElementById('panel-{s['tab']}').scrollHeight")
            c.viewport(h=int(top + sh + 4))
            time.sleep(1.0)
        c.js(f"document.getElementById('panel-{s['tab']}').scrollTop=0")
        png = os.path.join(OUT, name + ".png")
        c.screenshot(png)
        rects = c.js(RESOLVE_JS % json.dumps([i[0] for i in s["items"]]))
        vh = c.js("window.innerHeight")
        items = []
        for (spec, label, text), r in zip(s["items"], rects):
            if r is None:
                print(f"  !! {name}: no element for {spec}")
                continue
            if r[1] > vh - 30:
                print(f"  !! {name}: {spec} is below the fold, skipped")
                continue
            if r[1] + r[3] > vh - 6:          # clip to the visible area
                r = [r[0], r[1], r[2], vh - 6 - r[1]]
            p = 5
            items.append(dict(box=[round((r[0] - p) * w.SCALE), round((r[1] - p) * w.SCALE),
                                   round((r[2] + 2 * p) * w.SCALE), round((r[3] + 2 * p) * w.SCALE)],
                              label=label, text=text))
        spec = dict(image=f"../{name}.png", output=f"../{name}-annotated.png",
                    title=f"DevBench — {s['title']}", subtitle=t["sub"], items=items)
        json.dump(spec, open(os.path.join(ANN, name + ".json"), "w"), indent=2, ensure_ascii=False)
        print(f"{name}: {'ok' if ok else 'WAIT TIMED OUT'} ({len(items)} callouts)")
        done.append(name)
    c.viewport()
    return done


if __name__ == "__main__":
    capture(sys.argv[1], sys.argv[2:] or None)
