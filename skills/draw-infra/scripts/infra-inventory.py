#!/usr/bin/env python3
"""List the real infra parts and edges in a repo, so a diagram draws only what exists.

Usage: infra-inventory.py [<repo-root>]      (default: the current directory)

Reads, without running anything:
  docker-compose*.yml / compose*.yml   services, images, networks, ports, volumes, depends_on
  Jenkinsfile*                         stages, and `docker run` flags (--name, --network, -p, -v)
  Caddyfile*                           site address -> reverse_proxy target
  *.tf                                 resources, modules, and references between them
  k8s manifests (YAML with kind:)      kind, name, namespace
  .github/workflows/*.yml              workflow and job names

Prints Markdown sections. Env values print only for address-like names (_URL, _HOST, _ADDR, and a
few deploy names in Jenkinsfiles), never for names that hold a secret, and URLs lose any user:password.
Exit 0 always; an empty section means that source is absent.
"""
import os
import re
import sys

try:
    import yaml
except ImportError:  # the k8s and compose parsers fall back to "not parsed"
    yaml = None

SKIP_DIRS = {".git", "node_modules", ".terraform", "vendor", "dist", "build", ".next",
             "venv", ".venv", "__pycache__", "archive", "coverage", "test-results"}
MAX_BYTES = 400_000


def walk(root):
    for d, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS and not x.startswith(".") or x == ".github"]
        for f in files:
            p = os.path.join(d, f)
            try:
                if os.path.getsize(p) <= MAX_BYTES:
                    yield p
            except OSError:
                pass


def read(p):
    try:
        with open(p, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


SECRET_NAME = re.compile(r"KEY|SECRET|TOKEN|PASS|PWD|CRED|AUTH", re.I)


def safe_env(k, v):
    """Return a printable `K=V`, or None when the name looks secret. Drops URL user:password."""
    k, v = str(k), str(v)
    if SECRET_NAME.search(k):
        return None
    return f"{k}={re.sub(r'://[^/@\s]+@', '://', v)}"


def rel(p, root):
    return os.path.relpath(p, root)


# ---------- compose ----------
def compose(paths, root, out):
    for p in paths:
        out.append(f"\n### `{rel(p, root)}`")
        if not yaml:
            out.append("- not parsed: PyYAML is missing")
            continue
        try:
            doc = yaml.safe_load(read(p)) or {}
        except yaml.YAMLError as e:
            out.append(f"- not parsed: {str(e).splitlines()[0]}")
            continue
        svcs = doc.get("services") or {}
        for name, s in svcs.items():
            s = s or {}
            img = s.get("image") or ("build " + str(s.get("build", {}).get("context", ".")
                                                   if isinstance(s.get("build"), dict) else s.get("build")))
            nets = s.get("networks") or []
            nets = list(nets.keys()) if isinstance(nets, dict) else list(nets)
            ports = [str(x) for x in (s.get("ports") or [])]
            vols = [str(v).split(":")[0] + ":" + str(v).split(":")[1] if isinstance(v, str) and ":" in v
                    else str(v.get("source", v)) if isinstance(v, dict) else str(v)
                    for v in (s.get("volumes") or [])]
            deps = s.get("depends_on") or []
            deps = list(deps.keys()) if isinstance(deps, dict) else list(deps)
            line = f"- service `{name}`: image {img}"
            if s.get("container_name"):
                line += f", container `{s['container_name']}`"
            if nets:
                line += f", networks {nets}"
            if ports:
                line += f", ports {ports}"
            if vols:
                line += f", volumes {vols}"
            if deps:
                line += f", depends_on {deps}"
            env = s.get("environment") or {}
            if isinstance(env, list):
                env = dict(x.split("=", 1) for x in env if isinstance(x, str) and "=" in x)
            links = [safe_env(k, v) for k, v in env.items() if v and (
                re.search(r"(_URL|_ADDR)$", str(k)) and "://" in str(v) or re.search(r"_HOST$", str(k)))]
            links = [x for x in links if x]
            if links:
                line += f", links {links}"
            if s.get("network_mode"):
                line += f", network_mode {s['network_mode']}"
            out.append(line)
        for kind in ("networks", "volumes"):
            top = doc.get(kind) or {}
            if top:
                desc = []
                for n, v in top.items():
                    ext = isinstance(v, dict) and v.get("external")
                    desc.append(f"{n}{' (external)' if ext else ''}")
                out.append(f"- {kind}: {', '.join(desc)}")


# ---------- jenkins ----------
RUN_FLAGS = re.compile(r"(--name|--network|-p|--publish|-v|--volume|--add-host)[ =]+(\S+)")


def jenkins(paths, root, out):
    for p in paths:
        text = read(p)
        out.append(f"\n### `{rel(p, root)}`")
        stages = re.findall(r"stage\s*\(\s*['\"]([^'\"]+)['\"]", text)
        if stages:
            out.append(f"- stages: {' → '.join(stages)}")
        envs = dict(re.findall(r"^\s*([A-Z_]+)\s*=\s*['\"]([^'\"$]{1,60})['\"]\s*$", text, re.M))
        joined = re.sub(r"\\\\?\s*\n\s*", " ", text)
        for m in re.finditer(r"docker run\b([^\n\"']*)", joined):
            args = m.group(1)
            flags = {}
            for k, v in RUN_FLAGS.findall(args):
                k = {"--publish": "-p", "--volume": "-v"}.get(k, k)
                flags.setdefault(k, []).append(v)
            if not flags:
                continue
            links = re.findall(r"-e\s+([A-Z0-9_]*(?:_URL|_HOST|_ADDR))=(\S+)", args)
            if links:
                links = [x for x in (safe_env(k, v) for k, v in links) if x]
            if links:
                flags["links"] = links
            parts = [f"{k} {', '.join(v)}" for k, v in flags.items()]
            out.append(f"- docker run: {'; '.join(parts)}")
        for word in ("docker compose", "docker-compose", "ssh ", "rsync ", "aws s3", "terraform apply",
                     "kubectl apply", "helm upgrade", "docker push"):
            if word in text:
                out.append(f"- uses `{word.strip()}`")
        known = {k: v for k, v in envs.items() if re.search(r"NAME|PORT|NETWORK|IMAGE|PATH|HOST", k)}
        if known:
            shown = [x for x in (safe_env(k, v) for k, v in known.items()) if x]
            if shown:
                out.append("- env: " + ", ".join(shown))


# ---------- caddy ----------
def caddy(paths, root, out):
    for p in paths:
        out.append(f"\n### `{rel(p, root)}`")
        site = None
        depth = 0
        for line in read(p).splitlines():
            s = line.split("#", 1)[0].strip()
            if not s:
                continue
            if depth == 0 and s.endswith("{") and s != "{":
                site = s[:-1].strip()
            if site and "reverse_proxy" in s:
                target = s.split("reverse_proxy", 1)[1].strip().rstrip("{").strip()
                out.append(f"- `{site}` → {target}")
            depth += s.count("{") - s.count("}")
            if depth == 0:
                site = None


# ---------- terraform ----------
BLOCK = re.compile(r'^\s*(resource|module|data)\s+"([^"]+)"(?:\s+"([^"]+)")?\s*\{', re.M)
REF = re.compile(r"\b((?:aws|google|azurerm|cloudflare|kubernetes|helm|random|tls)_[a-z0-9_]+)\.([a-zA-Z0-9_-]+)\b"
                 r"|\bmodule\.([a-zA-Z0-9_-]+)\b")


def blocks(text):
    for m in BLOCK.finditer(text):
        i, depth = m.end(), 1
        while i < len(text) and depth:
            depth += {"{": 1, "}": -1}.get(text[i], 0)
            i += 1
        yield m.group(1), m.group(2), m.group(3), text[m.end():i]


def terraform(paths, root, out):
    by_dir = {}
    for p in paths:
        by_dir.setdefault(os.path.dirname(p), []).append(p)
    for d, files in sorted(by_dir.items()):
        res, edges, mods = [], set(), []
        for p in files:
            for kind, a, b, body in blocks(read(p)):
                if kind == "data":
                    continue
                if kind == "module":
                    src = re.search(r'source\s*=\s*"([^"]+)"', body)
                    me = f"module.{a}"
                    mods.append(f"{me} ({src.group(1) if src else '?'})")
                else:
                    me = f"{a}.{b}"
                    res.append(me)
                for r in REF.finditer(body):
                    to = f"module.{r.group(3)}" if r.group(3) else f"{r.group(1)}.{r.group(2)}"
                    if to != me:
                        edges.add((me, to))
        if not res and not mods:
            continue
        out.append(f"\n### `{rel(d, root) or '.'}/`")
        counts = {}
        for r in res:
            counts.setdefault(r.split(".")[0], []).append(r.split(".")[1])
        for t, names in sorted(counts.items()):
            out.append(f"- {t}: {', '.join(sorted(names))}")
        for m in mods:
            out.append(f"- {m}")
        names = set(res) | {m.split(" ")[0] for m in mods}
        for a, b in sorted(edges):
            if b in names:
                out.append(f"- edge: {a} → {b}")


# ---------- k8s ----------
def k8s(paths, root, out):
    rows = []
    for p in paths:
        if not yaml:
            break
        try:
            docs = list(yaml.safe_load_all(read(p)))
        except yaml.YAMLError:
            continue
        for doc in docs:
            if isinstance(doc, dict) and doc.get("kind") and doc.get("apiVersion"):
                md = doc.get("metadata") or {}
                rows.append(f"- {doc['kind']} `{md.get('name', '?')}` ns={md.get('namespace', 'default')}"
                            f" ({rel(p, root)})")
    out.extend(rows)


# ---------- github actions ----------
def actions(paths, root, out):
    for p in paths:
        if not yaml:
            break
        try:
            doc = yaml.safe_load(read(p)) or {}
        except yaml.YAMLError:
            continue
        jobs = list((doc.get("jobs") or {}).keys())
        out.append(f"- `{rel(p, root)}`: {doc.get('name', '?')}, jobs {jobs}")


def main():
    root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
    found = {"compose": [], "jenkins": [], "caddy": [], "tf": [], "k8s": [], "actions": [], "docker": []}
    for p in walk(root):
        b = os.path.basename(p)
        r = rel(p, root)
        if re.match(r"(docker-)?compose[^/]*\.ya?ml$", b, re.I):
            found["compose"].append(p)
        elif b.startswith("Jenkinsfile"):
            found["jenkins"].append(p)
        elif b.startswith("Caddyfile"):
            found["caddy"].append(p)
        elif b.endswith(".tf"):
            found["tf"].append(p)
        elif b.startswith("Dockerfile"):
            found["docker"].append(p)
        elif r.startswith(".github/workflows/") and b.endswith((".yml", ".yaml")):
            found["actions"].append(p)
        elif b.endswith((".yml", ".yaml")) and re.search(r"^kind:\s*\w+", read(p), re.M) \
                and re.search(r"^apiVersion:", read(p), re.M):
            found["k8s"].append(p)

    out = [f"# Infra inventory: {os.path.basename(root)}", "",
           "Built parts only: what the files define today. Planned parts come from the phase doc."]
    sections = [("Compose", "compose", compose), ("Jenkins", "jenkins", jenkins), ("Caddy", "caddy", caddy),
                ("Terraform", "tf", terraform), ("Kubernetes", "k8s", k8s), ("GitHub Actions", "actions", actions)]
    for title, key, fn in sections:
        paths = sorted(found[key])
        if not paths:
            continue
        out.append(f"\n## {title}")
        fn(paths, root, out)
    if found["docker"]:
        out.append("\n## Dockerfiles")
        out.extend(f"- `{rel(p, root)}`" for p in sorted(found["docker"]))
    if len(out) == 3:
        out.append("\nNo infra files found (compose, Jenkinsfile, Caddyfile, Terraform, k8s, workflows).")
    print("\n".join(out))


if __name__ == "__main__":
    main()
