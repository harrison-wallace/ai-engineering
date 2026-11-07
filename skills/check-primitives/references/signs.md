# Signs

A sign is code where the domain lives in conditionals instead of in a data structure. Each sign
has a stable ID, what it looks like, a lead to search for, and the primitive that removes it. A
lead is a place to read, not a finding. §3 of `SKILL.md` proves each one.

The primitive is the data structure that encodes the rule, so that the wrong state cannot be
written, or the next kind needs no new branch.

## State

| ID | Sign | Lead | Primitive |
|---|---|---|---|
| S1 | **Flags that must agree.** Two or more booleans or nullable fields describe one lifecycle (`isLoading`, `isError`, `data`; `isOpen`, `isClosing`). Some combinations are wrong, but the type allows them | Two or more `is[A-Z]`, `has[A-Z]`, or `should[A-Z]` fields or variables set in the same handler | A discriminated union (`{ status: "idle" } \| { status: "loading" } \| { status: "error"; error: E } \| { status: "done"; data: T }`), or a state machine |
| S2 | **Phase checks spread out.** Code in several places asks what phase it is in (`step === 2`, `status !== "done" && !cancelled`) and decides on its own what may happen next | The same status or step name compared in two or more files | A state machine, with the allowed transitions in one place |
| S3 | **Ad hoc mutation.** Many handlers change parts of one object or store, each with its own rules | Three or more sites that assign fields of the same object or call the same set of setters | A reducer, or a command and event model with one function that applies each change |

## Data shape

| ID | Sign | Lead | Primitive |
|---|---|---|---|
| D1 | **A branch for each kind.** The diff adds one more `else if`, `case`, or ternary for a new kind, type, plan, provider, or role | An added `case "..."` or `else if (x.type === "...")` | A registry or lookup map keyed by kind, or a union with an exhaustive `switch` that fails to compile when a kind is missing |
| D2 | **The same switch twice.** Two or more files branch on the same discriminant, and must be changed together | `git grep -n` for the discriminant's literal values across files | One registry that every site reads, or a method on the kind |
| D3 | **Optional fields that depend on each other.** `{ data?: T; error?: string }` where exactly one is set, or `{ kind: string; url?: string; file?: File }` where `kind` says which | An added type with two or more optional fields and a comment or check that says when each is set | A discriminated union, one member for each valid shape |
| D4 | **A loose shape repeated.** The same group of fields travels together, the same raw shape is checked in several files (`user.address?.city ?? ""`), or a plain `string` or `number` stands for a domain idea (a money amount, an ID, a slug, an email) | The same three or more parameters in several signatures, or the same optional chain in two or more files | A typed model, parsed once at the boundary and trusted inside |
| D5 | **The wrong collection.** The main access pattern scans or joins by hand (`.find` in a loop, nested loops to match IDs), or a copy is kept in sync with its source | `.find(` or `.filter(` inside a loop or a render, or two arrays updated together | A map or index keyed by the lookup, or a normalized collection with IDs |

## Modules

| ID | Sign | Lead | Primitive |
|---|---|---|---|
| M1 | **Split by time, not by knowledge.** Files or functions named for steps (`load`, `validate`, `transform`, `save`) each repeat the same rules about one domain thing | Step-named files that import the same types and check the same fields | One module that owns that domain thing and its rules. Execution order is not ownership |
| M2 | **Two writers.** Two actors (components, a server action and a client cache, two jobs) write the same state, and the result depends on which one runs last | Two or more writers of one store key, context value, table row, or file | Separate state for each actor, merged where it is read, or one owner that the others ask |

## React and Next.js

| ID | Sign | Lead | Primitive |
|---|---|---|---|
| R1 | **A `useState` cluster.** Three or more `useState` calls in one component that the same handlers set together, often S1 in hooks | Three or more `useState` in one component, set in the same handler | `useReducer` with a union state, or one `useState` that holds a union |
| R2 | **Stored derived state.** A `useState` plus a `useEffect` that copies a prop or computes a value from other state, so the two can disagree for one render or more | `useEffect(() => { set...(` that reads only props or state | Compute it during render. Use `useMemo` only when a measurement shows the cost |
| R3 | **State with two owners.** A filter, tab, page, or selection lives in `useState` and also in the URL, or in a component and also in a store or context | `useState` next to `useSearchParams`, or the same value in a store and a prop | One owner: the URL (`searchParams`) for state a user can share or reload, or the component for state nobody else reads |
| R4 | **Boolean props that exclude each other.** `primary`, `secondary`, `danger`, or `compact` and `large`, where only one may be true | Two or more boolean props on one component that are never true together | One union prop (`variant: "primary" \| "secondary" \| "danger"`) |

## Do not flag

The primitive must remove something: a branch, a repeated rule, an invalid state, or a lifecycle
risk. Drop a lead when:

- The shape is already clear, local to one function or component, and not likely to grow.
- The structure would add a layer of indirection and remove none of the four.
- There are two kinds and no sign of a third. A plain `if` is fine.
- The flags are independent. Every combination is valid (`isDarkMode`, `isSidebarOpen`).
- The code is generated, vendored, a test fixture, or a one-off script.
