# Evidence tiers

The same five tiers as `basic-why` (`../../basic-why/references/epistemics.md`), applied to outside
sources. Every claim sits in exactly one tier. The tier sets its wording.

| Tier | When | Wording |
|---|---|---|
| **Direct** | A primary source states it, and you read the page: official docs, a spec, a changelog or release note, a maintainer's issue comment, a paper's own results, or a vendor's price page | Plain and cited. "X supports Y [1]." |
| **Supported** | Two or more independent secondary sources agree, and no primary source covers it: blog posts, benchmarks by third parties, forum answers, X posts | Confident but visibly derived. "Several sources report X [2, 3]." |
| **Inferred** | A reasonable reading that no source states, built from claims above | Hedged, with the chain shown. "Given A [1] and B [4], C seems likely." |
| **Speculative** | One weak source, or several readings fit the evidence equally | "One report says X [5], but we found nothing to confirm it." |
| **Unknown** | You searched and could not find out | "We searched X, Y, and Z and found no answer." Say exactly what you searched |

## Rules

- **Dates.** Give each source's date: published, last updated, or the release date. When a page
  shows no date, write "undated". Prefer the newest primary source when sources disagree on a
  fact that changes over time, such as a price, a limit, or a default.
- **Versions.** A claim about a library or API names the version it applies to. A claim about an
  older version than the one in use is **Speculative** for the version in use, unless a changelog
  says the behavior did not change.
- **Independence.** Two posts that copy one source count as one source. Trace the claim to its
  origin.
- **Vendors.** A vendor's page is Direct for what the product does and costs. It is not Direct for
  claims that the product is better than others. Those need independent evidence.
- **X posts.** A post by the maintainer or the vendor's official account can be Direct for what
  they announce. Other posts are field reports: Supported at most, and only when several agree.
- **Snippets.** A search snippet alone is at most Speculative. Read the page to rate it higher.
- **No source, no claim.** A claim with no source goes to What we don't know.

## Do not

- Do not pick the source that makes the tidier story. Show the disagreement.
- Do not confirm a guess in the question. Test it like any other claim.
- Do not use "obviously", "clearly", "of course", "I think", or "I believe".
