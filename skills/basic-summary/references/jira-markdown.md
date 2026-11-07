# Markdown that pastes into Jira

Jira's editor turns some pasted Markdown into formatting, and it leaves the rest as literal
characters. Older Jira wiki markup also gives special meaning to some characters. Use only the
subset below, so that a paste needs no editing. If a paste still breaks, ask the user what Jira did,
and add the fix to this file.

## Use

- **Bold labels** on their own line for sections: `**Background**`. Do not use `#` headings.
- **Flat lists.** `1.` for steps and `-` for bullets. Put one blank line before a list and no blank
  lines between its items. Never nest a list.
- **Paragraphs** separated by one blank line.
- **Inline code** in single backticks, only for a name the reader must search for.
- **Links** as `[text](https://…)`, or a bare URL.
- **Ticket keys** bare, such as `ABC-123` written as plain text, so that Jira links them itself.

## Do not use

- Tables, HTML, images, footnotes, or task lists (`- [ ]`).
- Code fences inside the output. The terminal wraps the whole output in one fence, so the user
  copies the raw text, and an inner fence would close it early.
- Horizontal rules (`---` or `***`), block quotes (`>`), and nested lists.
- A line break made with two trailing spaces.
- Characters that Jira wiki markup reads as formatting: curly braces (`{…}`), square brackets
  outside a link, and words wrapped in `-`, `+`, `^`, `~`, or `_` (such as `-word-` or `_word_`).
- Single asterisks for emphasis. Use `**bold**` or nothing.
- Emoji, em dashes, and curly quotes.
- Any `<placeholder>` left from a template.

## Check before you print

- Every line starts with plain text, `**`, a number and a period (`1.`), or `- `.
- No line starts with `#`, `>`, `+`, `|`, or four spaces.
- Every `[` belongs to a `[text](url)` link.
