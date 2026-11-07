#!/usr/bin/env python3
"""List the skills installed for this Claude Code profile and project, read fresh from disk.

Usage: python3 -I list.py [<project dir>]     (default: the current directory)

Prints TSV with a header row: source, group, name, description, note.
Skills and slash commands are both listed, because both appear as skills in a session.
  source  repo | mine | local | plugin
  group   the README section for `mine`, the plugin name for `plugin`, else empty
  note    unmanaged | broken | not-installed-here | disabled-plugin, else empty
Built-in harness skills have no files on disk, so they are not listed here. The
`<config>/skills/synced/` folder holds the claude.ai skills (`anthropic-skills:*`), so it is
skipped, and those skills are treated as built-in.
Read-only.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    yaml = None

CONFIG = Path(os.environ.get("CLAUDE_CONFIG_DIR", Path.home() / ".claude")).expanduser()
REPO_ROOT = Path(__file__).resolve().parents[3]  # this skill lives in <ai-engineering>/skills/list-skills/scripts


def one_line(text):
    return " ".join(str(text or "").split()).replace("\t", " ")


def frontmatter(skill_md):
    try:
        text = skill_md.read_text(encoding="utf-8")
    except OSError:
        return {}
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end]
    if yaml:
        try:
            data = yaml.safe_load(block)
            return data if isinstance(data, dict) else {}
        except yaml.YAMLError:
            pass
    # Fallback: `key: value` lines, with `>` or `|` blocks folded into one line.
    data, key, buf = {}, None, []
    for line in block.splitlines():
        if key and (line.startswith(" ") or not line.strip()):
            buf.append(line.strip())
            continue
        if key:
            data[key] = " ".join(buf)
            key, buf = None, []
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            v = v.strip()
            if v in (">", "|", ">-", "|-"):
                key = k.strip()
            else:
                data[k.strip()] = v.strip("'\"")
    if key:
        data[key] = " ".join(buf)
    return data


def command_desc(md):
    """Description of a slash command file: frontmatter `description`, else its first text line."""
    fm = frontmatter(md)
    if fm.get("description"):
        return fm["description"]
    try:
        for line in md.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and line != "---" and ":" not in line[:20]:
                return line.lstrip("# ")
    except OSError:
        pass
    return ""


def git_root(start):
    try:
        out = subprocess.run(["git", "-C", str(start), "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, check=True)
        return Path(out.stdout.strip())
    except (OSError, subprocess.CalledProcessError):
        return Path(start).resolve()


def readme_groups():
    """Map skill name -> README '### ' section, from this repo's README."""
    groups, section = {}, ""
    try:
        lines = (REPO_ROOT / "README.md").read_text(encoding="utf-8").splitlines()
    except OSError:
        return groups
    for line in lines:
        if line.startswith("### "):
            section = line[4:].strip()
        elif line.startswith("## "):
            section = ""
        elif line.startswith("| [") and "](skills/" in line and section:
            name = line.split("](skills/", 1)[1].split("/", 1)[0]
            groups.setdefault(name, section)
    return groups


def load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def enabled_plugins(project):
    """User settings, then project settings, then project local settings. Later wins."""
    state = {}
    for p in (CONFIG / "settings.json", project / ".claude" / "settings.json",
              project / ".claude" / "settings.local.json"):
        state.update(load_json(p).get("enabledPlugins") or {})
    return state


def main():
    project = git_root(Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd())
    rows = []

    def add(source, group, name, desc, note=""):
        rows.append((source, group, name, one_line(desc), note))

    # Repo skills and commands: <project>/.claude/skills/*/SKILL.md, <project>/.claude/commands/*.md
    for md in sorted((project / ".claude" / "skills").glob("*/SKILL.md")):
        fm = frontmatter(md)
        add("repo", project.name, fm.get("name") or md.parent.name, fm.get("description"))
    for md in sorted((project / ".claude" / "commands").glob("*.md")):
        add("repo", project.name, md.stem, command_desc(md))

    # Profile skills: <config>/skills/*
    groups = readme_groups()
    linked = set()
    skills_dir = CONFIG / "skills"
    for entry in sorted(skills_dir.iterdir() if skills_dir.is_dir() else []):
        if entry.name == "synced":
            continue
        md = entry / "SKILL.md"
        if entry.is_symlink() and not entry.exists():
            add("local", "", entry.name, f"link to {os.readlink(entry)} is missing", "broken")
            continue
        if not md.is_file():
            continue
        fm = frontmatter(md)
        name = fm.get("name") or entry.name
        target = entry.resolve()
        if entry.is_symlink() and REPO_ROOT / "skills" in target.parents:
            linked.add(target.name)
            add("mine", groups.get(target.name, "Other"), name, fm.get("description"))
        else:
            add("local", "", name, fm.get("description"), "unmanaged")

    # User commands: <config>/commands/*.md
    for md in sorted((CONFIG / "commands").glob("*.md")):
        add("local", "", md.stem, command_desc(md), "unmanaged")

    # ai-engineering skills that exist but are not linked into this profile
    for md in sorted((REPO_ROOT / "skills").glob("*/SKILL.md")):
        if md.parent.name not in linked:
            fm = frontmatter(md)
            add("mine", groups.get(md.parent.name, "Other"), fm.get("name") or md.parent.name,
                fm.get("description"), "not-installed-here")

    # Plugin skills: installed entries for this project, else the user-scope entry
    installed = load_json(CONFIG / "plugins" / "installed_plugins.json").get("plugins") or {}
    enabled = enabled_plugins(project)
    for key, entries in sorted(installed.items()):
        pick = next((e for e in entries if e.get("scope") == "project"
                     and Path(e.get("projectPath", "")).resolve() == project), None)
        pick = pick or next((e for e in entries if e.get("scope") == "user"), None)
        if not pick:
            continue
        plugin = key.split("@", 1)[0]
        note = "" if enabled.get(key, True) else "disabled-plugin"
        base = Path(pick.get("installPath", ""))
        for md in sorted(base.glob("skills/*/SKILL.md")):
            fm = frontmatter(md)
            add("plugin", plugin, f"{plugin}:{fm.get('name') or md.parent.name}",
                fm.get("description"), note)
        for md in sorted(base.glob("commands/*.md")):
            add("plugin", plugin, f"{plugin}:{md.stem}", command_desc(md), note)

    print("source\tgroup\tname\tdescription\tnote")
    for r in rows:
        print("\t".join(r))
    print(f"# profile={CONFIG} project={project}", file=sys.stderr)


if __name__ == "__main__":
    main()
