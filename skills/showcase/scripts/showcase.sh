#!/usr/bin/env bash
# showcase.sh: the only writer of ~/showcase. Output is for the model. Exit 1 on misuse.
# Usage:
#   showcase.sh list                            table: status kind repo topic date file, oldest first
#   showcase.sh keep <kind> <topic>             body on stdin; writes capture-<yy-mm-dd-hh-mm>-<repo>-<topic>.md
#   showcase.sh mark <topic> used|dropped|kept  legal transitions only, on the newest file for the topic
#   showcase.sh brief "<hook>" ["<hook>" ...]   check hooks for secrets, write the Grok brief, print its path
#   showcase.sh digest [days] [project-path]    sessions of the last <days> (7), at most 20, via reflect/digest.sh -b
#   showcase.sh projects [days]                 other projects with sessions in the last <days>: name, count, path
# Invariants:
#   kind is x-post|article|video; topic matches ^[a-z0-9]+(-[a-z0-9]+){0,4}$. Else exit 1 and write nothing.
#   keep never replaces a file: a taken name gets -2, then -3, before .md. Names sort by time (sort -V).
#   keep and brief refuse text that matches $SECRETS. digest drops such lines and counts them.
#   mark: kept->used, kept->dropped, dropped->kept. used is final. Same state is a no-op.
#   Writes go to a temp file in ~/showcase, then mv. Nothing outside ~/showcase is written,
#   except the brief folder under $TMPDIR. Nothing leaves the machine: the model runs Grok, not this script.
set -euo pipefail

DIR="${SHOWCASE_DIR:-$HOME/showcase}"
CONFIG="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
HERE="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
DIGEST="$(readlink -f "$HERE/../../reflect/digest.sh" 2>/dev/null || true)"
MAX_SESSIONS=20
MAX_HOOK=140
TOPIC_RE='^[a-z0-9]+(-[a-z0-9]+){0,4}$'
SECRETS='AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY|gh[pousr]_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9_-]{20,}|xox[abpr]-|(password|secret|token|api_?key)[[:space:]]*[:=]|([0-9]{1,3}\.){3}[0-9]{1,3}|[A-Za-z0-9+/]{40,}'
# An X post URL is not a key. Mask it before the check, or a long handle trips the 40-character run.
XURL='https?://(www\.)?(x|twitter)\.com/[A-Za-z0-9_]{1,15}/status/[0-9]+'
mask() { sed -E "s#$XURL#<x-post-url>#g"; }

usage() { sed -n '3,9p' "$0" >&2; exit 1; }
die() { echo "showcase.sh: $*" >&2; exit 1; }
slug() { tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//'; }
repo() { basename "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" | slug; }
projdir() { echo "$CONFIG/projects/$(printf '%s' "$1" | sed 's|[^A-Za-z0-9]|-|g')"; }
is_days() { [[ "$1" =~ ^[1-9][0-9]{0,2}$ ]] || die "days must be a number from 1 to 999: $1"; }

# fm <file> <field>: one field from the first frontmatter block.
fm() { awk -v k="$2" 'NR==1 && $0!="---" {exit} NR>1 && $0=="---" {exit} NR>1 && index($0, k": ")==1 {print substr($0, length(k)+3); exit}' "$1"; }

# captures: every capture file, oldest first.
captures() { [ -d "$DIR" ] || return 0; find "$DIR" -maxdepth 1 -type f -name 'capture-*.md' -printf '%f\n' | sort -V | sed "s|^|$DIR/|"; }

cmd_list() {
  local f n=0
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    [ $n -eq 0 ] && printf 'status\tkind\trepo\ttopic\tdate\tfile\n'
    printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$(fm "$f" status)" "$(fm "$f" kind)" "$(fm "$f" repo)" \
      "$(fm "$f" topic)" "$(fm "$f" date)" "$f"
    n=$((n + 1))
  done < <(captures)
  [ $n -gt 0 ] || echo "No kept pitches in $DIR."
}

cmd_keep() {
  local kind=$1 topic=$2 r ts base f n body tmp
  case "$kind" in x-post|article|video) ;; *) die "kind must be x-post, article, or video: $kind" ;; esac
  [[ "$topic" =~ $TOPIC_RE ]] || die "topic must be kebab-case, at most 5 words: $topic"
  body="$(cat)"
  [ -n "${body//[[:space:]]/}" ] || die "keep needs the pitch body on stdin"
  if hit="$(grep -niE -m1 "$SECRETS" <<<"$(mask <<<"$body")")"; then
    die "the body has a line that looks like a secret, an IP, or a long key (line ${hit%%:*}). Rewrite it. Nothing written."
  fi
  r="$(repo)"; ts="$(date +%y-%m-%d-%H-%M)"
  mkdir -p "$DIR"
  base="$DIR/capture-$ts-$r-$topic"; f="$base.md"; n=2
  while [ -e "$f" ]; do f="$base-$n.md"; n=$((n + 1)); done
  tmp="$(mktemp "$DIR/.keep.XXXXXX")"
  printf -- '---\nkind: %s\nstatus: kept\nrepo: %s\ntopic: %s\ndate: %s\n---\n\n%s\n' \
    "$kind" "$r" "$topic" "$ts" "$body" > "$tmp"
  mv -n "$tmp" "$f"
  [ ! -e "$tmp" ] || { rm -f "$tmp"; die "$f appeared during the write. Nothing written."; }
  echo "Kept: $f"
}

cmd_mark() {
  local topic=$1 to=$2 r f mine="" any="" repos="" from tmp
  [[ "$topic" =~ $TOPIC_RE ]] || die "topic must be kebab-case, at most 5 words: $topic"
  case "$to" in used|dropped|kept) ;; *) die "status must be used, dropped, or kept: $to" ;; esac
  r="$(repo)"
  while IFS= read -r f; do
    [ -n "$f" ] && [ "$(fm "$f" topic)" = "$topic" ] || continue
    any="$f"; repos="$repos $(fm "$f" repo)"
    [ "$(fm "$f" repo)" = "$r" ] && mine="$f"
  done < <(captures)
  [ -n "$any" ] || die "no kept pitch has the topic $topic. Run: showcase.sh list"
  if [ -n "$mine" ]; then f="$mine"
  elif [ "$(echo "$repos" | tr ' ' '\n' | sed '/^$/d' | sort -u | wc -l)" -eq 1 ]; then f="$any"
  else die "the topic $topic is in more than one repo ($(echo "$repos" | tr ' ' '\n' | sed '/^$/d' | sort -u | paste -sd " " -)). Run it from the repo you mean."
  fi
  from="$(fm "$f" status)"
  if [ "$from" = "$to" ]; then echo "No change: $f is already $to."; return 0; fi
  case "$from>$to" in
    "kept>used"|"kept>dropped"|"dropped>kept") ;;
    "used>"*) die "$f is used, and used is final." ;;
    *) die "$from to $to is not allowed. Allowed: kept to used, kept to dropped, dropped to kept." ;;
  esac
  tmp="$(mktemp "$DIR/.mark.XXXXXX")"
  awk -v to="$to" 'NR>1 && $0=="---" && !done {done=1} !done && /^status: / {$0="status: " to} {print}' "$f" > "$tmp"
  mv "$tmp" "$f"
  echo "$from -> $to: $f"
}

cmd_brief() {
  local i=0 h out
  for h in "$@"; do
    i=$((i + 1))
    [ -n "${h//[[:space:]]/}" ] || die "hook $i is empty. Nothing written."
    [ "${#h}" -le $MAX_HOOK ] || die "hook $i has ${#h} characters, more than $MAX_HOOK. Nothing written."
    if grep -qiE "$SECRETS" <<<"$(mask <<<"$h")"; then
      die "hook $i looks like it holds a secret, an IP, or a long key. Rewrite it, and do not send it. Nothing written."
    fi
  done
  out="$(mktemp -d "${TMPDIR:-/tmp}/showcase-XXXXXX")"
  {
    echo "You are a read-only researcher. Do not edit files or run shell commands."
    echo
    echo "For each numbered post hook below, search X posts only. Report, in at most 80 words for each hook:"
    echo "how many recent posts make the same point (none, few, many), one example post URL with its date,"
    echo "and one angle that no post you found takes. Do not write drafts."
    echo "If you cannot search X, say exactly that, and name the tool you used."
    echo
    i=0
    for h in "$@"; do i=$((i + 1)); printf '%d. %s\n' "$i" "$h"; done
  } > "$out/brief.md"
  echo "brief=$out/brief.md"
  echo "dir=$out"
  echo "log=$out/grok-x.log"
}

cmd_digest() {
  local days=${1:-7} target=${2:-} pd files=() raw kept dropped
  is_days "$days"
  [ -n "$DIGEST" ] && [ -x "$DIGEST" ] || die "reflect/digest.sh is missing next to this skill"
  if [ -n "$target" ]; then pd="$(projdir "$target")"
  else
    pd="$(projdir "$(pwd)")"
    [ -d "$pd" ] || pd="$(projdir "$(git rev-parse --show-toplevel 2>/dev/null || pwd)")"
  fi
  [ -d "$pd" ] || { echo "No sessions folder for ${target:-$(pwd)}."; return 0; }
  mapfile -t files < <(find "$pd" -maxdepth 1 -type f -name '*.jsonl' -size +5k -mtime "-$days" -printf '%T@ %p\n' \
    | sort -rn | head -n $MAX_SESSIONS | cut -d' ' -f2-)
  [ ${#files[@]} -gt 0 ] || { echo "No sessions over 5 KB in the last $days days in $pd."; return 0; }
  raw="$("$DIGEST" -b "${files[@]}" | mask)"
  kept="$(grep -viE "$SECRETS" <<<"$raw" || true)"
  dropped="$(grep -ciE "$SECRETS" <<<"$raw" || true)"
  printf '%s\n\n' "$kept"
  echo "digest: ${#files[@]} sessions from the last $days days, $dropped secret-like lines dropped."
}

cmd_projects() {
  local days=${1:-7} hist="$CONFIG/history.jsonl" here top since
  is_days "$days"
  command -v jq >/dev/null || die "jq is required"
  [ -f "$hist" ] || { echo "No history at $hist."; return 0; }
  here="$(pwd)"; top="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
  since=$(( ($(date +%s) - days * 86400) * 1000 ))
  jq -r --argjson since "$since" --arg here "$here" --arg top "$top" '
      select(.timestamp? and .timestamp >= $since and .project? and .sessionId?)
      | select(.project != $here and .project != $top) | [.project, .sessionId] | @tsv' "$hist" \
    | sort -u | cut -f1 | sort | uniq -c | sort -rn \
    | awk '{n=$1; $1=""; sub(/^ /, ""); p=$0; m=split(p, a, "/"); printf "%s\t%d\t%s\n", a[m], n, p}' \
    | { printf 'name\tsessions\tpath\n'; cat; } | awk 'NR==1 {h=$0; next} {if (!s) print h; s=1; print} END {if (!s) print "No other projects with sessions in the last '"$days"' days."}'
}

cmd=${1:-}; shift || true
case "$cmd" in
  list)     [ $# -eq 0 ] || usage; cmd_list ;;
  keep)     [ $# -eq 2 ] || usage; cmd_keep "$@" ;;
  mark)     [ $# -eq 2 ] || usage; cmd_mark "$@" ;;
  brief)    [ $# -ge 1 ] || usage; cmd_brief "$@" ;;
  digest)   [ $# -le 2 ] || usage; cmd_digest "$@" ;;
  projects) [ $# -le 1 ] || usage; cmd_projects "$@" ;;
  *)        usage ;;
esac
