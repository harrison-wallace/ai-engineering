# Where grep stops

A symbol search finds callers. These are the places it misses. Work through the items that fit
the change's domain. Skip the ones that do not apply, and do not report "checked N/A" lines.

## Software

- **The library itself.** Read the source of what you call, at the **pinned** version in the
  lockfile, and check for a local patch (`patches/`, `patch-package`, a vendored copy). The docs
  can describe a newer version.
- **Timing.** When does it run? Consider microtasks against macrotasks, unmount and teardown,
  in-flight async work after a cancel, effect order (React against Solid), retries, debounce, and
  startup order.
- **Shapes that cross a boundary.** JSON an API returns, a DB column, a file format, a queue
  message, a cache entry, a URL or query param, a cookie, `localStorage`. Old data, old clients,
  and other services still hold the **old** shape.
- **Other readers of the same bytes.** Another language, a script, a cron job, an analytics
  query, a backup and restore, or a migration that reads the field.
- **Strings, not symbols.** Routes, event names, feature flags, env vars, config keys, CSS
  classes, test IDs, i18n keys. Dynamic access (`obj[key]`, string templates) hides them from a
  word search, so search for fragments too.
- **Defaults and widening.** A changed default reaches every caller that did not pass the value.
  A widened type lets in values that downstream code never handled.
- **Several hops away.** Something that consumes a consumer: an export re-exported, a generated
  client (OpenAPI, tRPC) built from the type, docs or examples that people copy.
- **Tests that hide it.** Mocks or fixtures that still return the old shape, so the suite
  passes while the real path breaks.

## Infra

- **Replace, not update.** Check whether Terraform will destroy and recreate the resource (a
  renamed resource address, a `ForceNew` argument, a changed `name`, `count` turned into
  `for_each`). For data stores, replacement means the data is gone. Look for `moved {}` blocks,
  `lifecycle`, and `prevent_destroy`.
- **Who reads the outputs.** `terraform_remote_state` and data sources in **other** stacks,
  and scripts that call `terraform output`.
- **Shared Docker resources.** External networks (for example `proxy`), named volumes, and
  container names that other compose projects reference. Reverse-proxy labels or configs that
  route to a container name or port.
- **Names in the outside world.** DNS records, Cloudflare tunnels, Access policies, and redirect
  rules that point at a hostname. TLS certificates issued for a name.
- **Identity.** IAM policies, bucket policies, and KMS key policies that name an ARN. Roles
  assumed by CI. A rename breaks all of these silently.
- **Paths and schedules.** Cron jobs, systemd timers, backup scripts, log rotation, and
  monitoring that use a path, a container name, or a bucket. Backups that will now silently back
  up nothing.
- **Pipelines.** Jenkinsfiles and GitHub Actions that read an env var, a secret name, an image
  tag, or a branch name.
- **Versions.** Provider, module, and image upgrades: read the changelog between the pinned and
  the new version for breaking changes and changed defaults. Check for `:latest` that will float.
- **Ordering and drift.** Something created by hand or outside IaC that the change now
  conflicts with. The current live state may already differ from the code. A read-only `plan`
  shows this.
- **Cost and limits.** A change that adds NAT, cross-AZ, or egress traffic, more log volume, or
  more instances. A quota or rate limit the new shape reaches.
