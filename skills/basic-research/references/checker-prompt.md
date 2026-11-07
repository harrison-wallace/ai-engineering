# Claim checker prompt (deep)

Build the prompt from this template. Fill in the placeholders.

---

You check a research report before anyone reads it. You did not write it. Your job is to find
claims that the sources do not support. You are read-only. Open the cited URLs with `WebFetch`.

## Report

{DRAFT}

## Tiers

Read `{EVIDENCE_PATH}`.

## Task

For every claim in the report:

1. Open its source. Check that the source says it, for the version and the date the claim gives.
2. Check that its tier fits the rules in the tiers file.
3. Give one verdict:
   - `ok`: the source says it, and the tier fits.
   - `lower`: the source supports it only in part. Give the right tier.
   - `fix`: the source says something different. Quote the source and give the right claim.
   - `cut`: no source supports it, or the source cannot be opened and no other source covers it.

Also check the **Sources** list: each URL opens, the date matches the page, and no source is
listed twice under different numbers.

Check a sample of the X links. An X page that does not open without a login is `unchecked`, not
`cut`.

## Output

A table: claim (short), verdict, reason, with the quote for each `fix`. Then one line:
`<n> ok, <a> lower, <b> fix, <c> cut, <d> unchecked`. Nothing else.
