# Vocabulary

Adapted from Matt Pocock's `codebase-design` skill (its glossary, principles, and `DEEPENING.md`),
with an infra section added. Use these terms exactly. Consistent words are the point.

## Terms

| Term | Means | Do not say |
|---|---|---|
| **Module** | Anything with an interface and an implementation, at any size: a function, a class, a package, a Terraform module, a compose service, a script | unit, component, service |
| **Interface** | Everything a caller must know to use the module correctly: the types, and also the invariants, the ordering rules, the error modes, the required config and env vars, and the performance limits | API, signature |
| **Implementation** | The code inside a module | |
| **Depth** | How much behaviour a caller or a test gets for each thing it must learn about the interface. **Deep**: much behaviour behind a small interface. **Shallow**: the interface is nearly as complex as the implementation | |
| **Seam** | The place where a module's interface lives, where you can change behaviour without editing in that place | boundary |
| **Adapter** | A concrete thing that fills an interface at a seam, such as an HTTP client in production and an in-memory fake in tests | |
| **Leverage** | What callers get from depth: more behaviour for each thing they learn. One implementation pays back across N callers and M tests | |
| **Locality** | What maintainers get from depth: change, bugs, and tests concentrate in one place. Fix it once, and it is fixed everywhere | |

## Principles

- **The deletion test.** Imagine you delete the module. If its complexity disappears, or moves
  into one place, it was a pass-through: merge it. If the complexity comes back in N callers, the
  module earns its keep.
- **The interface is the test surface.** Callers and tests cross the same seam. A test that must
  reach past the interface shows that the module has the wrong shape.
- **One adapter is a guess. Two adapters make a real seam.** Do not add a seam unless something
  varies across it, usually production and test.
- **Depth is a property of the interface.** A deep module can have small parts inside, with
  internal seams for its own tests. Do not expose them in the interface.
- **Replace tests, do not add layers.** When the deepened module has tests at its interface, delete
  the old tests on the shallow parts. Tests check results through the interface, not internal
  state, so they survive internal refactors.

## Signs of a shallow module

- To understand one concept, you open five small files.
- The interface is nearly as large as the implementation.
- A pure function was pulled out only to test it, but the bugs are in how callers use it. There is
  no locality.
- Modules depend on each other's internals across a seam.
- The code is hard to test through its current interface, or has no tests.

## Dependency kinds

The kind decides how the deepened module is tested.

| Kind | Software | Infra | Test it with |
|---|---|---|---|
| **in-process** | Pure logic, in-memory state, no I/O | `locals`, templates, rendered config | Merge, and test through the new interface. No adapter |
| **local-substitutable** | A dependency with a local stand-in (PGLite, an in-memory filesystem) | A stack that `terraform test` with mock providers, `docker compose up`, or LocalStack can run | The stand-in, inside the test suite. The seam stays internal |
| **ports & adapters** | Your own service across a network | Another stack's remote state or outputs that you own | A port at the seam, a real adapter in production, and an in-memory adapter in tests |
| **true external** | A third party (Stripe, Twilio) | A cloud or vendor API (AWS, Cloudflare) | An injected port, and a mock adapter in tests |

## Infra

- **Module** can be a Terraform module, a stack, a compose file or service, a Helm chart, an
  Ansible role, a shell script, or a `Makefile` target.
- **Interface** includes the variables and outputs, the required providers, the env vars, the
  ports and volumes, and every **ordering rule** ("apply network before app", "run `init.sh`
  first"). A rule only a README states is still part of the interface.
- **Shallow infra signs:**
  - A Terraform module that takes nearly every resource argument as a variable and passes it
    through.
  - The same stack or resource blocks copied across environments or repos, with no shared module.
  - The same compose service copied across files, with small edits.
  - A wrapper script that calls one command with the same flags.
  - A value (a port, a hostname, a bucket name) that must change in several places at once.
- **Deepening moves state.** Plan `moved` blocks or `terraform state mv` for renamed resources.
  Renamed containers, networks, volumes, and hostnames ripple to other repos, so name
  `/trace-impact` for those.
