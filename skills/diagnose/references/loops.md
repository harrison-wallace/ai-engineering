# Loops

A loop is one command that goes red on the bug and green when it is fixed. Pick from the list that
fits the bug. Prefer a loop higher in its list. Any loop must still meet the four checks in §2 of
`SKILL.md`: red, deterministic, fast, and agent-runnable.

## App code

1. **A failing test** at the seam that reaches the bug: unit, integration, or end-to-end.
2. **A curl or HTTP script** against a running dev server. Assert the status and the body field
   that is wrong.
3. **A CLI call** with a fixture input. `diff` its output against a known-good snapshot.
4. **A replayed capture.** Save a real request, payload, or event log to the scratchpad, then run
   it through the code path alone.
5. **A throwaway harness.** Start the smallest part of the system that reaches the bug (one
   service, stubbed dependencies) and call it once.
6. **A property or fuzz loop**, for "sometimes the output is wrong". Run 1000 random inputs and
   catch the failure.
7. **A differential loop.** Run the same input through the old and the new version, or through two
   configs, and `diff` the outputs.

## UI

- **Explore with the Playwright MCP** to find the steps and the selectors.
- **Then save the loop as a script** (`npx playwright test <file>` or a short Node script) that
  asserts the DOM, a console error, or a network response. The agent must be able to run it again
  with one command. MCP clicks are not a loop.

## Infra

Read-only on shared, production, and AWS systems. Ask before any write, restart, or deploy.

| Symptom | Loop |
|---|---|
| A URL fails or returns the wrong thing | `curl -sv --resolve <host>:443:<ip> https://<host>/<path>` for each hop: DNS, proxy, container. Assert the status and a header that says which hop answered |
| A name resolves wrong | `dig +short <name> @<resolver>` against each resolver in the path |
| A container exits or restarts | `docker compose ps` and `docker compose logs --since 10m <service>`. Assert the exit code or the log line |
| A service cannot reach another | `docker compose exec <a> sh -c 'nc -zv <b> <port>'`, or `curl` from inside the container |
| An AWS resource acts wrong | A read-only `aws` call that shows the state (`describe-*`, `get-*`), with `--query` to assert one field |
| An AWS log shows the error | A CloudWatch Logs Insights query through `aws logs start-query` and `get-query-results`, filtered to the symptom |
| A Terraform plan wants an odd change | `terraform plan -no-color -target=<address>`. Assert the attribute that changes. Never `apply` |

## Regression between two known states

Use a **bisection harness**. Write a script that sets up the state, runs the loop, and exits 0 when
green, 1 when red, and 125 when the commit cannot be tested. Then:

```bash
git bisect start <bad> <good>
git bisect run <scratchpad>/bisect.sh
git bisect reset
```

Record the first bad commit in the diagnosis log. Its diff is the lead for §4.

## Flaky bugs

The goal is a higher reproduction rate, not a clean repro. Run the trigger 100 times, run it in
parallel, add load, narrow the timing window, or inject sleeps. A bug that fails 50% of the time
can be diagnosed. One that fails 1% of the time cannot, so keep raising the rate. Record the rate
in the diagnosis log, and use it as the red check.

## Performance

Logs are usually the wrong tool here. Measure first, fix second:

1. **Baseline.** A timing harness (`hyperfine '<command>'`, `performance.now()` around the path, or
   `time` over N runs), a profiler, or a query plan (`EXPLAIN ANALYZE`). Record the median and the
   spread.
2. **Red check.** The loop is red when the median is over a threshold that you agree with the
   user.
3. **Bisect.** Use `git bisect run` with that threshold when the regression has a known good state.
   Otherwise, cut the path in halves and time each half.

## A human must act

Use this as the last resort, when only a human can take a step (sign in, click in a third-party
dashboard, read a device).

1. Copy [`../scripts/hitl-loop.template.sh`](../scripts/hitl-loop.template.sh) to the scratchpad.
2. Edit the steps between the markers. Use `step` for an action and `capture` for an observation.
3. Ask the user to run `bash <path>` in their own terminal, then to say when it is done. Neither
   the Bash tool nor the `!` prefix gives a script an interactive input, so the prompts would read
   nothing.
4. Read `<path>.out`, which the script writes at the end. Its `KEY=VALUE` lines are the loop
   result.

The `.out` file comes back into the chat. Use `capture` only for observations. Make signing in and
anything secret a `step`.
