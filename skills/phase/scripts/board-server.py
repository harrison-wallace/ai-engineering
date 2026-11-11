#!/usr/bin/env python3
"""Serve live phase boards on the LAN. Needs only Python 3.

Usage:
  board-server.py add <repo>...       register repos (a repo needs docs/plans/BOARD.md)
  board-server.py remove <repo>...    unregister
  board-server.py list                registered repos, and the running server's URL
  board-server.py render [<repo>...]  render once (all registered repos by default)
  board-server.py serve [--ports 38090-38099] [--bind <ip>] [--interval 3]
  board-server.py unit [serve flags]  print a systemd user unit that runs serve at boot

serve renders every registered repo, serves the boards at http://<ip>:<port>/<repo>/, and
re-renders a board when its files change: docs/plans/, docs/phases/, map.json, the infra files
(compose, Jenkinsfile, Caddyfile, Terraform), and new commits. Open pages reload themselves.
It takes the first free port in the range, so several servers can run side by side.

Files: registry  ${XDG_CONFIG_HOME:-~/.config}/phase-board/repos.txt
       boards    ${XDG_CACHE_HOME:-~/.cache}/phase-board/<repo>/index.html
       running   ${XDG_CACHE_HOME:-~/.cache}/phase-board/server-<port>.json, one per running server
"""
import html
import http.server
import importlib.util
import json
import os
import signal
import re
import socket
import sys
import threading
import time

HERE = os.path.dirname(os.path.realpath(__file__))
CONFIG = os.path.join(os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config"), "phase-board")
CACHE = os.path.join(os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache"), "phase-board")
REGISTRY = os.path.join(CONFIG, "repos.txt")


def running_file(port):
    return os.path.join(CACHE, f"server-{port}.json")


def running():
    """Servers that are still alive, from their running files. Stale files are removed."""
    out = []
    for f in sorted(os.listdir(CACHE)) if os.path.isdir(CACHE) else []:
        if re.match(r"server-\d+\.json$", f):
            path = os.path.join(CACHE, f)
            try:
                info = json.load(open(path))
                os.kill(info["pid"], 0)
                out.append(info)
            except (OSError, ValueError, KeyError):
                try:
                    os.remove(path)
                except OSError:
                    pass
    return out
INFRA = re.compile(r"^((docker-)?compose[^/]*\.ya?ml|Jenkinsfile.*|Caddyfile.*|.*\.tf|Dockerfile.*)$", re.I)
SKIP = {".git", "node_modules", ".terraform", "dist", "build", ".next", "vendor", "data", "coverage"}

spec = importlib.util.spec_from_file_location("render_board", os.path.join(HERE, "render-board.py"))
rb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rb)


def repos():
    try:
        with open(REGISTRY) as fh:
            return [l.strip() for l in fh if l.strip() and not l.startswith("#")]
    except OSError:
        return []


def save(paths):
    os.makedirs(CONFIG, exist_ok=True)
    with open(REGISTRY, "w") as fh:
        fh.write("".join(p + "\n" for p in paths))


def slug(repo, taken):
    base = re.sub(r"[^a-z0-9-]+", "-", os.path.basename(repo.rstrip("/")).lower()).strip("-") or "repo"
    name, n = base, 2
    while name in taken:
        name, n = f"{base}-{n}", n + 1
    return name


def names():
    out, taken = {}, set()
    for r in repos():
        s = slug(r, taken)
        taken.add(s)
        out[r] = s
    return out


def signature(repo):
    """Latest mtime of everything a board depends on."""
    latest = 0.0
    for sub in ("docs/plans", "docs/phases", "docs/adr"):
        for d, dirs, files in os.walk(os.path.join(repo, sub)):
            dirs[:] = [x for x in dirs if x not in ("archive", "board")]
            for f in files:
                try:
                    latest = max(latest, os.path.getmtime(os.path.join(d, f)))
                except OSError:
                    pass
    for d, dirs, files in os.walk(repo):
        depth = d[len(repo):].count(os.sep)
        dirs[:] = [x for x in dirs if x not in SKIP and not x.startswith(".") and depth < 3]
        for f in files:
            if INFRA.match(f):
                try:
                    latest = max(latest, os.path.getmtime(os.path.join(d, f)))
                except OSError:
                    pass
    for f in (".git/HEAD", ".git/logs/HEAD"):
        try:
            latest = max(latest, os.path.getmtime(os.path.join(repo, f)))
        except OSError:
            pass
    return latest


def error_page(out, msg):
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "index.html"), "w") as fh:
        fh.write(f"<!DOCTYPE html><meta charset=utf-8><title>Board error</title><p>{html.escape(msg)}</p>")
    try:
        os.remove(os.path.join(out, "stamp.txt"))  # the next good render then writes the page again
    except OSError:
        pass


def render_one(repo, name, live):
    out = os.path.join(CACHE, name)
    try:
        path, changed = rb.render(repo, out, live=live)
        return ("rendered" if changed else "unchanged"), path
    except SystemExit as e:  # no board yet, or another stop from the renderer
        error_page(out, str(e))
        return "error", str(e)
    except Exception as e:  # keep serving the other boards
        msg = f"render-board failed: {type(e).__name__}: {e}"
        error_page(out, msg)
        return "error", msg


def write_index():
    os.makedirs(CACHE, exist_ok=True)
    rows = "".join(f'<li><a href="/{n}/">{html.escape(n)}</a> <small>{html.escape(r)}</small></li>'
                   for r, n in names().items())
    with open(os.path.join(CACHE, "index.html"), "w") as fh:
        fh.write("<!DOCTYPE html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,"
                 "initial-scale=1'><title>Phase boards</title><style>body{font:16px system-ui;margin:24px;"
                 "max-width:640px}li{margin:10px 0}small{color:#888;display:block}</style></head><body>"
                 f"<h1>Phase boards</h1><ul>{rows or '<li>No repos. Run <code>board-server.py add &lt;repo&gt;</code>.</li>'}"
                 "</ul></body></html>")
    with open(os.path.join(CACHE, ".phase-board"), "w") as fh:
        fh.write("phase-board\n")


def lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("192.0.2.1", 9))  # no packet is sent; this picks the outbound interface
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=CACHE, **k)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *a):
        pass

    def list_directory(self, path):  # never list folders
        self.send_error(404)
        return None


def watch(interval):
    seen = {}
    while True:
        write_index()
        for repo, name in names().items():
            sig = signature(repo)
            if seen.get(repo) != sig:
                state, info = render_one(repo, name, live=True)
                if state != "unchanged":
                    print(f"{time.strftime('%H:%M:%S')} {state:9} {name}" + (f": {info}" if state == "error" else ""),
                          flush=True)
                seen[repo] = sig
        time.sleep(interval)


def serve(args):
    lo, hi = 38090, 38099
    bind, interval = lan_ip(), 3.0
    i = 0
    while i < len(args):
        if args[i] == "--ports":
            lo, hi = (int(x) for x in args[i + 1].split("-"))
            i += 1
        elif args[i] == "--bind":
            bind = args[i + 1]
            i += 1
        elif args[i] == "--interval":
            interval = float(args[i + 1])
            i += 1
        i += 1
    write_index()
    httpd = None
    for port in range(lo, hi + 1):
        try:
            httpd = http.server.ThreadingHTTPServer((bind, port), Handler)
            break
        except OSError:
            continue
    if not httpd:
        raise SystemExit(f"board-server: every port from {lo} to {hi} is in use on {bind}. Use --ports.")
    url = f"http://{lan_ip() if bind == '0.0.0.0' else bind}:{port}/"
    others = [s["url"] for s in running()]
    with open(running_file(port), "w") as fh:
        json.dump({"url": url, "pid": os.getpid(), "port": port}, fh)
    if others:
        print("Other board servers: " + ", ".join(others), flush=True)
    signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt))
    print(f"Phase boards at {url}  (Ctrl-C to stop)", flush=True)
    print("Any device on your LAN can open them while this runs.", flush=True)
    threading.Thread(target=watch, args=(interval,), daemon=True).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
        try:
            os.remove(running_file(port))
        except OSError:
            pass
        print("Stopped.", flush=True)


def unit(args):
    if "--bind" not in args:  # at boot the LAN address may not be up yet, so listen on every interface
        args = ["--bind", "0.0.0.0"] + args
    flags = "".join(" " + a for a in args)
    print(f"""# Save as ~/.config/systemd/user/phase-board.service, then:
#   systemctl --user daemon-reload && systemctl --user enable --now phase-board
#   loginctl enable-linger "$USER"    # keep it running when you are logged out
[Unit]
Description=Live phase boards on the LAN
After=network-online.target
Wants=network-online.target

[Service]
ExecStart={sys.executable} {os.path.realpath(__file__)} serve{flags}
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target""")


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        print(__doc__)
        return
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == "add":
        cur = repos()
        for a in args:
            p = os.path.realpath(a)
            if not os.path.isfile(os.path.join(p, "docs", "plans", "BOARD.md")):
                print(f"skip   {p}: no docs/plans/BOARD.md (run /phase init there)")
            elif p in cur:
                print(f"have   {p}")
            else:
                cur.append(p)
                print(f"add    {p}")
        save(cur)
    elif cmd == "remove":
        gone = {os.path.realpath(a) for a in args}
        save([r for r in repos() if r not in gone])
        print("removed " + ", ".join(sorted(gone)))
    elif cmd == "list":
        for r, n in names().items():
            print(f"{n}\t{r}")
        live = running()
        for info in live:
            print(f"running: {info['url']} (pid {info['pid']})")
        if not live:
            print("running: no")
    elif cmd == "render":
        targets = [os.path.realpath(a) for a in args] or repos()
        nm = names()
        for r in targets:
            state, info = render_one(r, nm.get(r) or slug(r, set(nm.values())), live=True)
            print(f"{state:9} {info}")
        write_index()
    elif cmd == "serve":
        serve(args)
    elif cmd == "unit":
        unit(args)
    else:
        raise SystemExit(f"board-server: unknown command {cmd}. Run with --help.")


if __name__ == "__main__":
    main()
