# Sort prompt

The prompt for one sorting subagent. Fill the `<...>` fields, and send the text from
`You sort code comments` to the end as the prompt.

---

You sort code comments into categories. You do not edit any file.

**Repo root:** `<absolute repo root>`
**Rules:** read `<absolute path to references/categories.md>` first, and follow it exactly.
**Your comments** (TSV: `loc`, `kind`, `tag`, `text`). A loc is `path:line`, `path:start-end`,
or `path:line:col`, relative to the repo root:

```
<the TSV rows for this batch>
```

For each row:

1. Read the comment in its file with the code around it: the whole function, or 15 lines each
   side.
2. Ask the questions in "How to sort" in their order, and stop at the first yes.
3. For `stale`, prove it. Run `rg -n -w '<name>'` from the repo root for each name the comment
   cites, or point to the line that contradicts it. If you cannot prove it, the row is `unsure`.
4. For `adr`, check all three tests. If one fails, the row is `keep`.

The `tag` column is only a hint. A `todo` tag can be `stale`, and a `-` tag can be an `excuse`.

Return only a TSV block, one line for each input row, in input order, with no header:

```
<loc>	<category>	<why, at most 15 words>	<extra>
```

- `category`: `stale`, `excuse`, `tautology`, `adr`, `keep`, or `unsure`.
- `extra`:
  - for `excuse`: `hack: <the shortcut>; fix: <the proper fix>`
  - for `adr`: `decision: <the decision as one short phrase>`
  - for `stale`: the proof, such as `rg legacyFetch: no definition`
  - for `unsure`: what would settle it
  - for the others: `-`

Copy each `loc` exactly. Do not merge, split, or skip rows.
