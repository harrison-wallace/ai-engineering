# Pitch

## Fields

| Field | Values | Owner |
|---|---|---|
| `kind` | `x-post`, `article`, `video` | the model picks it, `showcase.sh` checks it |
| `topic` | `^[a-z0-9]+(-[a-z0-9]+){0,4}$` | the model picks it, `showcase.sh` checks it |
| `status` | `kept`, then `used` or `dropped`. `dropped` can go back to `kept`. `used` is final | `showcase.sh` only |
| `repo` | basename of `git rev-parse --show-toplevel`, else of the cwd, in kebab-case | `showcase.sh` only |
| `date` | the minute it was kept, `yy-mm-dd-hh-mm` | `showcase.sh` only |
| `teach` | `/teach <topic>` for `article` and `video`, else empty | the model writes it in the body |

A pitch the user does not keep stays in the chat. It is never a file.

## Chat shape

```
Showcase: 3 pitches from this session. Grok X: used. Drafts to rewrite in your voice.

1. [x-post] "<draft, at most 280 characters>"
   Proof: <what in the work backs it>. X today: <one line from Grok>.
2. [article] "<title A>" / "<title B>"
   Outline: <point>; <point>; <point>. Show: <diff, clip, diagram>.
   Outline it: /teach <topic>
3. [video] ...

Keep which? (e.g. "1 3", or "none")
```

## File

Path: `~/showcase/capture-<yy-mm-dd-hh-mm>-<repo>-<topic>.md`. The date and time lead, so the
names sort by time (`sort -V` puts `-2` after the first file). When the name is taken,
`showcase.sh keep` adds `-2`, then `-3`, before `.md`. It never replaces a file. It writes the
frontmatter. The model supplies the body on stdin. `SHOWCASE_DIR` moves the folder.

```markdown
---
kind: x-post
status: kept
repo: ai-engineering
topic: readme-row-limit
date: 26-11-08-14-32
---

# <one-line title>

**Draft:** <the X draft, or the two titles and the outline>

**Proof:** <the number, the before-and-after, the short commit hash or file that shows it>

**X today:** <the Grok line, or "not checked">

**Show:** <what to put on screen>

**Next:** /teach <topic>   (article and video only)
```

`mark` changes only the `status:` line. The user can edit the body by hand.

## Grok brief

`showcase.sh brief` makes a new folder, `$TMPDIR/showcase-XXXXXX/`, and writes `brief.md` in it,
with one numbered hook for each argument. It prints `brief=`, `dir=`, and `log=` for the Grok run.

```markdown
You are a read-only researcher. Do not edit files or run shell commands.

For each numbered post hook below, search X posts only. Report, in at most 80 words for each hook:
how many recent posts make the same point (none, few, many), one example post URL with its date,
and one angle that no post you found takes. Do not write drafts.
If you cannot search X, say exactly that, and name the tool you used.

1. <hook>
2. <hook>
```

## Secret patterns

`showcase.sh brief` and `keep` refuse text, and `digest` drops a line, that matches `SECRETS` in
[`../scripts/showcase.sh`](../scripts/showcase.sh), case-insensitive. The script is the only copy of
the patterns. They cover cloud and API keys, private keys, a password or token assignment, an IPv4
address, and a run of 40 or more base64 characters (a full commit hash is one). An X post URL is
masked first, so a long handle does not count as a key. `digest` prints the count it dropped. A
host name or a customer name in plain words passes the check, so the model must keep them out.
