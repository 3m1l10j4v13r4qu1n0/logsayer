# logsayer

> **Spec-kit tells you what to build. logsayer tells you where you stand, how you got there, and whether what you built is still what you said you would build.**

A Python CLI that scaffolds and coordinates a 5-layer documentary system for AI-agent projects: Specification, State, Logbook, Verification (mechanical + semantic), and Process.

Everything the agent needs to know about a project is written down by the same system that uses it — each layer answers one question, each document lives in exactly one layer, and every judgment lives in the CLI, not in the generated files.

## Disclaimer (Dune homage)

> This project uses names and concepts from Frank Herbert's *Dune* saga exclusively as a thematic reference and role metaphor. It is not affiliated with, sponsored by, or officially associated with Herbert Properties LLC, Legendary Entertainment, or any rights holders of the franchise. No art, logos, or protected material is reproduced — only concept/role names as a design analogy.

## Why logsayer

The spec-driven pattern (as popularized by GitHub Spec Kit) governs the *first* generation of code. After that, its authority over the code is by convention, not verification. logsayer closes the loop that pattern leaves open:

- **State continuity** between sessions — an anchor snapshot the agent reads (and only that) at session start.
- **A partitioned, append-only logbook** for the *"why"* of past decisions.
- **A mechanical + semantic verification loop** that checks whether the code still matches the spec — both structurally and in meaning.
- **Multi-agent coordination** through the standard `AGENTS.md` convention, with thin native adapters per tool (opencode and Claude Code today).

## The 5 layers

| # | Layer | Question it answers | Dune role |
|---|-------|--------------------|-----------|
| 1 | Specification (normative) | What must be built? | Mentat |
| 2 | State (anchor) | Where is the project right now? | Guild Navigator |
| 3 | Logbook (historical) | How did we get here, and why? | Reverend Mother |
| 4 | Verification | Does what was built still match the spec? | Suk Doctor (mechanical) + Truthsayer (semantic) |
| 5 | Process (operational) | How do we work here? | Fremen |

Every layer has a plain-English alias, so you can use logsayer without knowing any of the lore.

## Incoming documents

A document arrives from somewhere else — a teammate's delivery, a contract, a
meeting minute, a Swagger file. **Where does it go?**

Put it in `inbox/`. That is the declared drop zone: it lives at the project
root, *outside* `docs/`, it is not versioned, and `logsayer check` tells you
when something is sitting there unprocessed. The CLI moves and names; your
agent derives the content.

```bash
# 1. Drop it in (from anywhere — Downloads, a chat, an email attachment)
logsayer inbox add ~/Downloads/contrato_backend.md

# 2. See where it can go. Prints the candidates; writes nothing. The CLI does
#    NOT pick the layer: it only decides when the signal is unambiguous
#    (a non-markdown extension, or a HU in the file name).
logsayer doc route inbox/contrato_backend.md
→ sin decisión automática. El nombre no dice si el documento es global o
  técnico. Eso lo decide Mentat; el CLI no lo clasifica.
→ pista:      el nombre tiene términos técnicos (contrato): 02_technical/ es el
  primer candidato, pero eso no lo decide el CLI.

Candidatos:
  · 1 — Especificación → docs/02_technical/ — crear con: logsayer doc new technical <nombre>
  · 1 — Especificación → docs/01_global/ — crear con: logsayer doc new global <nombre>
  · 1 — Especificación → docs/04_user_stories/<HU>/ — crear con: logsayer spec new <HU>

# 3. Create the document in the layer that was decided. The original is
#    archived in inbox/_done/ and its provenance is recorded in "## Fuente".
logsayer doc new technical contrato_api_backend --from inbox/contrato_backend.md

# 4. The agent (Mentat subagent) fills in the content. The CLI never writes
#    layer 1 prose for you — it scaffolds, you decide.
```

`logsayer check` is where you find out this is pending:

```
! bandeja_entrada: 1 sin ubicar (umbral de aviso: 14 días)
   - inbox/contrato_backend.md
   siguiente: logsayer doc route <archivo>  (Mentat decide la capa)
```

A pending document is a `warn`, not a `fail`: the check still exits 0, because
a project with something unprocessed is healthy, not sick.

### Where does my document go?

| Entrada                                                          | Va a                                                       | ¿Se versiona?                            | Crear con                           |
|------------------------------------------------------------------|------------------------------------------------------------|------------------------------------------|-------------------------------------|
| Documento de un equipo externo, entrega, acta o informe recibido | fuera de `docs/` (bandeja `inbox/`), y su derivado en Capa 1 | el original no; el documento derivado sí | `logsayer inbox add <archivo>`     |
| Contrato transversal: API, DTOs, modelo de datos, stack          | 1 — Especificación → `docs/02_technical/`                    | sí                                       | `logsayer doc new technical <nombre>` |
| Visión, alcance, regla de negocio o requisito global             | 1 — Especificación → `docs/01_global/`                       | sí                                       | `logsayer doc new global <nombre>` |
| Contrato o criterio que aplica a una HU puntual                  | 1 — Especificación → `docs/04_user_stories/<HU>/`            | sí                                       | `logsayer spec new <HU>`            |
| Informe de auditoría sobre un documento externo                  | Capa 4 → `docs/06_audits/audit_<fecha>-<area>.md`            | sí                                       | `logsayer audit run`                |
| El "por qué" o el "cómo" de lo que ya se hizo                    | Capa 3 → bitácora (append-only)                            | sí                                       | `logsayer log add "…"`              |

The table is generated from `core/routing.py` and a test keeps this README and
the core in sync. Print it any time with `logsayer doc route`.

Never a loose `.md` inside `docs/` — that is exactly what `check` rejects as
`capas_mezcladas`.

### The gotcha worth knowing

A `.md` file dropped at the **project root** is invisible to logsayer: it is in
no layer, so no check reports it. The root is not a layer, and a file there is
nobody's job. If a document arrives, route it through `inbox/` — that is the
only path the framework watches.

## Installation

Requires Python 3.11+.

```bash
uv tool install logsayer
# or
pipx install logsayer
```

## Quick start

```bash
# 1. Scaffold a new project
logsayer init my-project
cd my-project

# 2. Write the spec for a user story
logsayer spec new HU-01

# 3. Add an agent adapter (opencode, claude)
logsayer agent add opencode

# 4. Start a session: check state, work the story
logsayer state show
logsayer check        # mechanical, and reports any unprocessed inbox/ document
# ... implement HU-01 ...

# 5. Close the session: log it, audit when threshold is hit
logsayer log add "HU-01 done: API + tests"
logsayer check          # mechanical: structure, no mixed layers
logsayer audit run      # semantic: spec vs real code report
```

For an existing project:

```bash
logsayer init --here
```

A document arrived from another team? See
[Incoming documents](#incoming-documents).

## Commands

| Command | Dune alias | Layer | Purpose |
|---------|-----------|-------|---------|
| `logsayer init [name]` | — | scaffold | Creates `docs/` + `inbox/` + `AGENTS.md` + `logsayer.toml` |
| `logsayer init --here` | — | scaffold | Scaffolds into the current directory |
| `logsayer agent add <opencode\|claude>` | — | coordination | Generates per-role subagents for a tool |
| `logsayer inbox` | — | 1 | Lists documents waiting to be placed |
| `logsayer inbox add <file>` | — | 1 | Moves an external document into `inbox/` |
| `logsayer spec new <hu>` | `logsayer mentat spec new` | 1 | Creates a minimal HU template |
| `logsayer doc route [file]` | `logsayer mentat doc route` | 1 | Prints the routing table (or the row for a file) |
| `logsayer doc new <layer> <name>` | `logsayer mentat doc new` | 1 | Creates a layer-1 document (`--from` archives the source) |
| `logsayer state show` | `logsayer navigator state show` | 2 | Prints the project snapshot |
| `logsayer memory index` | `logsayer navigator memory index` | transversal | Regenerates `00_memory_index.md` from the real files |
| `logsayer memory status` | `logsayer navigator memory status` | transversal | Inventory of the index (what it covers, how many tags) |
| `logsayer log add "…"` | `logsayer reverend-mother log add` | 3 | Appends a logbook entry (auto-partition) |
| `logsayer log index` | `logsayer reverend-mother log index` | 3 | Rebuilds `00_index.md` from real files |
| `logsayer check` | `logsayer suk doctor` | 4 | Mechanical checks: structure, no layer mixing, pending inbox |
| `logsayer audit run` | `logsayer truthsayer audit run` | 4 | Generates the audit report + semantic prompt |
| `logsayer audit status` | `logsayer truthsayer audit status` | 4 | Shows HU counter vs threshold, last report |
| `logsayer process check` | `logsayer fremen verify` | 5 | Process checks: Dor, coordination agreement |

## Configuration (`logsayer.toml`)

Generated by `logsayer init`, tuned in a single file:

```toml
[logsayer]
session_close_context_threshold = 0.70   # % context used → propose session close
bitacora_max_lines = 400                 # lines/logbook file before partitioning
audit_threshold_hus = 3                  # HUs closed since last audit → trigger audit
inbox_max_age_days = 14                 # days unprocessed in inbox/ → warn about it aging
```

## How a session flows

1. **Session start** — the agent reads *only* the state layer (`docs/project_state.md`). Cheap in tokens, enough to orient.
2. **Audit check** — if the closed-HUs counter meets the threshold, the agent proactively proposes an audit (semantic verification).
3. **Work** — the agent works a HU reading only its folder under `docs/04_user_stories/`, and only opens a logbook entry when it needs the *"why"* of a past decision.
4. **Close / commit** — with your prior approval, the agent overwrites the state snapshot and appends to the active logbook.
5. **Auto-partition** — when the active logbook exceeds the line limit, the next file is created and the master index updated.

## Example session

A full, real transcript — run against a freshly scaffolded project — lives in [`examples/hello-logsayer/`](examples/hello-logsayer/README.md). It walks through scaffold, story creation, logbook entries, verification, and agent adapters, with the actual output of every command.

## Multi-agent design

A single engine (`logsayer/core/`) plus one thin adapter per agent (`logsayer/adapters/<agent>/`) that only translates each tool's native file convention and calls the CLI. Adding a new agent means a new adapter, not new logic. See [`docs/` of this repo](logsayer_especificacion_maestra.md) (master spec) for the full architecture.

## Roadmap

- **0–6 (done):** naming & manifest, `init`, core commands (`spec`, `state`, `log`, `audit`), opencode/Claude adapters, mechanical validation (`check`, `process check`), docs & publishing, incoming documents (`inbox/`, `doc route`, `doc new`).
- **7:** community presets, more agents on demand (copilot, cursor, gemini, hermes).
- **8 (current):** selective memory — a generated index over `docs/`, a `tags` frontmatter contract, and a deterministic `memory search`. You are here.

## Acknowledgment & license

- MIT — see [LICENSE](LICENSE).
- Built around the 5-layer documentary system described in the master spec.
- Names and concepts from *Dune* are used as a thematic role metaphor only (full disclaimer at the top of this document).