#!/usr/bin/env python3
"""webui_shot.py - screenshots of the devbench web UI from a headless Chrome.

Portfolio copy of demo_recording/webui_shot.py with a configurable CDP port,
profile dir and scale, usable both as a CLI and as a library (CDP class).

  webui_shot.py start                      launch headless Chrome on $DEVBENCH_UI
  webui_shot.py shot TAB [SUBTAB] OUT.png [--js CODE]
  webui_shot.py stop

Env: DEVBENCH_UI (default http://localhost:3000/), CDP_PORT (default 9334),
     CHROME_PROFILE (default $TMPDIR/portfolio-webui-chrome-<CDP_PORT>),
     SCALE (deviceScaleFactor, default 2), VIEW_W / VIEW_H (default 1600x1000).
Nothing appears on screen. macOS Chrome path.
"""
import base64, json, os, subprocess, sys, tempfile, time, urllib.request
import websocket   # websocket-client

PORT = int(os.environ.get("CDP_PORT", "9334"))
URL = os.environ.get("DEVBENCH_UI", "http://localhost:3000/")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PROFILE = os.environ.get("CHROME_PROFILE", os.path.join(tempfile.gettempdir(), f"portfolio-webui-chrome-{PORT}"))
SCALE = float(os.environ.get("SCALE", "2"))
VIEW_W = int(os.environ.get("VIEW_W", "1600"))
VIEW_H = int(os.environ.get("VIEW_H", "1000"))


def page_ws(port=PORT):
    tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json"))
    return [t for t in tabs if t["type"] == "page"][0]["webSocketDebuggerUrl"]


class CDP:
    def __init__(self, port=PORT):
        self.ws = websocket.create_connection(page_ws(port), timeout=60)
        self.n = 0

    def __call__(self, method, **params):
        self.n += 1
        self.ws.send(json.dumps({"id": self.n, "method": method, "params": params}))
        while True:
            m = json.loads(self.ws.recv())
            if m.get("id") == self.n:
                if "error" in m:
                    raise RuntimeError(f"{method}: {m['error']}")
                return m.get("result", {})

    def js(self, code, await_promise=False):
        r = self("Runtime.evaluate", expression=code, returnByValue=True, awaitPromise=await_promise)
        if "exceptionDetails" in r:
            raise RuntimeError(f"JS error: {r['exceptionDetails'].get('exception', {}).get('description', r['exceptionDetails'])}")
        return r.get("result", {}).get("value")

    def viewport(self, w=VIEW_W, h=VIEW_H, scale=SCALE):
        self("Emulation.setDeviceMetricsOverride", width=w, height=h, deviceScaleFactor=scale, mobile=False)

    def wait_for(self, cond_js, timeout=15.0, interval=0.3):
        """Poll a JS boolean expression until true; returns True/False."""
        end = time.time() + timeout
        while time.time() < end:
            try:
                if self.js(f"!!({cond_js})"):
                    return True
            except RuntimeError:
                pass
            time.sleep(interval)
        return False

    def goto_tab(self, tab, sub=None, settle=0.8):
        self.js(f"document.querySelector('#tabBar [data-tab=\"{tab}\"]').click()")
        time.sleep(settle)
        if sub:
            self.js(f"document.querySelector('#panel-{tab} .sub-tab[data-subtab=\"{sub}\"]').click()")
            time.sleep(settle)

    def screenshot(self, out):
        png = self("Page.captureScreenshot", format="png")["data"]
        with open(out, "wb") as f:
            f.write(base64.b64decode(png))
        return out


def start():
    os.makedirs(PROFILE, exist_ok=True)
    subprocess.Popen([CHROME, "--headless=new", f"--remote-debugging-port={PORT}", f"--user-data-dir={PROFILE}",
                      f"--remote-allow-origins=http://127.0.0.1:{PORT}", f"--window-size={VIEW_W},{VIEW_H}",
                      "--hide-scrollbars", URL],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(60):
        try:
            page_ws(); break
        except Exception:
            time.sleep(0.25)
    c = CDP()
    c.viewport()
    return c


def stop():
    subprocess.run(["pkill", "-f", f"remote-debugging-port={PORT}"])


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "start":
        start(); print(f"headless devbench UI up on CDP :{PORT} ({URL})")
    elif cmd == "stop":
        stop()
    elif cmd == "shot":
        args = sys.argv[2:]
        js = None
        if "--js" in args:
            i = args.index("--js"); js = args[i + 1]; del args[i:i + 2]
        tab, out = args[0], args[-1]
        sub = args[1] if len(args) == 3 else None
        c = CDP(); c.viewport()
        c.goto_tab(tab, sub)
        if js:
            c.js(js); time.sleep(0.8)
        print("saved", c.screenshot(out))
