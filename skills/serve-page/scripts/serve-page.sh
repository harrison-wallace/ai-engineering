#!/usr/bin/env bash
# Serve one HTML page folder on the LAN, on the first free port from 38081 to 38089.
# Usage:
#   serve-page.sh plan  <dir>               print ip=, port=, url=, path= (starts nothing)
#   serve-page.sh start <dir> <port> <ip>   run the server in the foreground (use a background task)
#   serve-page.sh check <port>              wait up to 5 s for the port to listen; exit 0 when it does
#   serve-page.sh stop  <port> <dir>        stop the http.server on <port> only if it serves <dir>
# Exit codes: 1 usage or failed check, 2 no free port, 3 no LAN address.
set -euo pipefail

FIRST=38081
LAST=38089
usage() { sed -n '2,9p' "$0" >&2; exit 1; }

listening() { # <port> → exit 0 when something listens on it
  if command -v ss >/dev/null; then
    [ -n "$(ss -Hltn "sport = :$1" 2>/dev/null)" ]
  else
    lsof -nP -iTCP:"$1" -sTCP:LISTEN >/dev/null 2>&1
  fi
}

lan_ip() {
  if command -v ip >/dev/null; then
    ip -4 route get 1.1.1.1 2>/dev/null | awk '{for (i = 1; i < NF; i++) if ($i == "src") print $(i + 1)}'
  else
    ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || true
  fi
}

pid_on() { # <port> → the PID that listens on it
  if command -v ss >/dev/null; then
    ss -Hltnp "sport = :$1" 2>/dev/null | grep -oE 'pid=[0-9]+' | head -1 | cut -d= -f2
  else
    lsof -nP -t -iTCP:"$1" -sTCP:LISTEN 2>/dev/null | head -1
  fi
}

cmdline_of() {
  if [ -r "/proc/$1/cmdline" ]; then tr '\0' ' ' < "/proc/$1/cmdline"; else ps -o command= -p "$1"; fi
}

cmd=${1:-}; shift || true
case "$cmd" in
  plan)
    [ $# -eq 1 ] || usage
    [ -f "$1/index.html" ] || { echo "serve-page: $1/index.html not found" >&2; exit 1; }
    dir=$(cd "$1" && pwd)
    ip=$(lan_ip)
    [ -n "$ip" ] || { echo "path=$dir/index.html"; echo "serve-page: no LAN address" >&2; exit 3; }
    for p in $(seq "$FIRST" "$LAST"); do
      if ! listening "$p"; then
        printf 'ip=%s\nport=%s\nurl=http://%s:%s/\npath=%s/index.html\n' "$ip" "$p" "$ip" "$p" "$dir"
        exit 0
      fi
    done
    echo "path=$dir/index.html"; echo "serve-page: ports $FIRST-$LAST are all in use" >&2; exit 2 ;;
  start)
    [ $# -eq 3 ] || usage
    exec python3 -m http.server "$2" --bind "$3" --directory "$1" ;;
  check)
    [ $# -eq 1 ] || usage
    for _ in 1 2 3 4 5 6 7 8 9 10; do listening "$1" && exit 0; sleep 0.5; done
    echo "serve-page: nothing listens on port $1" >&2; exit 1 ;;
  stop)
    [ $# -eq 2 ] || usage
    dir=$(cd "$2" && pwd)
    pid=$(pid_on "$1")
    [ -n "$pid" ] || { echo "serve-page: nothing listens on port $1"; exit 0; }
    line="$(cmdline_of "$pid") "
    case "$line" in
      *http.server*"--directory $dir "*) kill "$pid" && echo "stopped pid $pid on port $1" ;;
      *) echo "serve-page: port $1 is held by another process (pid $pid). Not stopping it." >&2; exit 1 ;;
    esac ;;
  *) usage ;;
esac
