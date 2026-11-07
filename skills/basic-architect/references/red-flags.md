# Red flags

Screen every candidate before you merge. A red flag means revise or reject the shape. It is not
a style note. Use the software section, the infra section, or both. The cross-cutting section
always applies.

The test behind every flag: the next contributor is an agent that sees only the files it opened,
copies the nearest example, and takes the shortest path that works. Does the design keep that
agent correct?

## Cross-cutting

- **Split ownership.** Two modules, services, stacks, or pipelines write the same state or the
  same resource. Each one has its own rules, and the rules drift apart. Fix: one owner. The others
  read it, or ask the owner to change it.
- **Copied truth.** The same fact (a schema, a CIDR, a port, a feature flag, a list of tenants)
  is kept in two places and synced by hand. Fix: one source, and derive the rest from it.
- **Not idempotent.** Running it twice, or resuming after a crash halfway, gives a different
  result.
- **No way back.** A change has no rollback path, or the only rollback is "restore from backup"
  and nobody has tested the restore.
- **Cache later.** The main access pattern only works after a cache, index, or map that is not
  in the design yet. The structure is wrong.

## Software

- **Shallow module.** The interface is large compared to what it hides. Signs: callers
  coordinate several calls to finish one operation, options expose internal stages, and learning
  the interface does not save the caller from learning the implementation. Do not confuse a deep
  module with a deep call chain. A chain of layers spreads the understanding out. A deep module
  concentrates it.
- **Information leakage.** Several modules depend on the same internal decision (a
  representation, a format, a protocol detail), so one change needs edits in many places.
  Re-exporting wire or transport types on the public API counts.
- **Split by time, not by knowledge.** Separate load, validate, transform, and save modules
  that each carry the same representation and its invariants. Group code by the knowledge it
  owns instead.
- **Pass-through.** A method or layer forwards the same arguments to something of the same shape
  and adds nothing: no policy, no adaptation, no abstraction.
- **Escape hatches.** The types only compile with `any`, casts, non-null assertions, or optional
  fields that are always set in practice.
- **Callers must know the rules.** Using it correctly needs knowledge that is not in its
  signature, such as "call init first" or "never pass both".

## Infra

- **Managed in two places.** A resource is in IaC and also changed by hand, by a second stack,
  or by a script. Includes rules attached inline and also as separate resources.
- **Hardcoded environment.** Account IDs, regions, CIDRs, hostnames, or bucket names are
  written into modules instead of passed in or looked up.
- **Pass-through module.** A module takes 20 variables only to set 20 resource arguments. It
  hides nothing. Use the resource directly, or give the module opinions.
- **Shared state across environments.** One state file, compose project, or namespace serves
  more than one environment, so a mistake in one breaks all of them.
- **IAM at the wrong layer.** Wildcard actions or resources, long-lived user keys where a role
  would do, or permissions granted to a broad group for one service's needs.
- **Secrets in plain config.** Secrets in `.tf` files, compose files, `.env` files committed to
  git, CI logs, or state without encryption.
- **Untested backup.** Backups exist but no restore has ever been run, or the backup lives on the
  same host, disk, or account as the data.
- **Snowflake.** A setting that lives only on the box, or only in a console, with no IaC and no
  runbook.
- **Unpinned versions.** `:latest` images, unpinned providers or modules, or CI actions pinned
  to a branch.
- **Public by default.** A port, bucket, or endpoint is reachable from the internet without a
  stated reason and a stated control (Cloudflare Access, auth, an allow-list).
- **Cost cliff.** A design that is cheap at rest but expensive under normal use: NAT gateway data
  charges, cross-AZ or egress traffic, per-request pricing on a hot path, or logs with no
  retention.
- **Single point, unstated.** A single host, disk, AZ, or token that everything depends on, and
  the ADR does not say this was accepted on purpose.

Some complexity is real. A flag that fires but is accepted on purpose goes in the ADR's
tradeoffs, with the reason.
