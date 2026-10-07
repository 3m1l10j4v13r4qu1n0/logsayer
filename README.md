# logsayer

> **Spec-kit tells you what to build. logsayer tells you where you stand, how you got there, and whether what you built is still what you said you would build.**

[![CI](https://github.com/3m1l10j4v13r4qu1n0/logsayer/actions/workflows/ci.yml/badge.svg)](https://github.com/3m1l10j4v13r4qu1n0/logsayer/actions/workflows/ci.yml) [![PyPI](https://img.shields.io/pypi/v/logsayer.svg)](https://pypi.org/project/logsayer/)

A Python CLI that scaffolds and coordinates a 5-layer documentary system for AI-agent projects: Specification, State, Logbook, Verification (mechanical + semantic), and Process.

Everything the agent needs to know about a project is written down by the same system that uses it — each layer answers one question, each document lives in exactly one layer, and every judgment lives in the CLI, not in the generated files.

The public surface (this README, command names, the docs) is in English; CLI output and generated content follow the templates, which are in Spanish — the language of generated content is a project decision, not a framework flag.

## Why logsayer

The spec-driven pattern (as popularized by GitHub Spec Kit) governs the *first* generation of code. After that, its authority over the code is by convention, not verification. logsayer closes the loop that pattern leaves open:

- **State continuity** between sessions — an anchor snapshot the agent reads (and only that) at session start.
- **A partitioned, append-only logbook** for the *"why"* of past decisions.
- **A mechanical + semantic verification loop** that checks whether the code still matches the spec — both structurally and in meaning.
- **Multi-agent coordination** through the standard `AGENTS.md` convention, with thin native adapters per tool (opencode, Claude Code and GitHub Copilot today).

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
  · docs/02_technical/ — crear con: logsayer doc new technical <nombre>
  · docs/01_global/ — crear con: logsayer doc new global <nombre>
  · docs/04_user_stories/<HU>/ — crear con: logsayer spec new <HU>

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
# ... or with a preset of conventions: logsayer init my-project --preset minimal

# 2. Write the spec for a user story
logsayer spec new HU-01

# 3. Add an agent adapter (opencode, claude, copilot)
logsayer agent add opencode

# 4. Start a session: check state, work the story
logsayer state show
logsayer check        # mechanical: structure, pending inbox/ documents, no mixed layers
# ... implement HU-01 ...

# 5. Close the session: log it, audit when threshold is hit
logsayer log add "HU-01 done: API + tests"
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
| `logsayer init [name] --preset <default\|minimal>` | — | scaffold | Same, plus a preset of project conventions written into `logsayer.toml` |
| `logsayer init --here` | — | scaffold | Scaffolds into the current directory |
| `logsayer agent add <opencode\|claude\|copilot>` | — | coordination | Generates the per-role agents of a tool in its native convention |
| `logsayer inbox` | — | 1 | Lists documents waiting to be placed |
| `logsayer inbox add <file>` | — | 1 | Moves an external document into `inbox/` |
| `logsayer spec new <hu>` | `logsayer mentat spec new` | 1 | Creates a minimal HU template |
| `logsayer doc route [file]` | `logsayer mentat doc route` | 1 | Prints the routing table (or the row for a file) |
| `logsayer doc new <layer> <name>` | `logsayer mentat doc new` | 1 | Creates a layer-1 document (`--from` archives the source) |
| `logsayer state show` | `logsayer navigator state show` | 2 | Prints the project snapshot |
| `logsayer memory index` | `logsayer navigator memory index` | transversal | Regenerates `00_memory_index.md` from the real files |
| `logsayer memory status` | `logsayer navigator memory status` | transversal | Inventory of the index (what it covers, how many tags) |
| `logsayer memory search "…"` | `logsayer navigator memory search` | transversal | Ranked candidates by tag (`--capa`, `--limit`) |
| `logsayer log add "…"` | `logsayer reverend-mother log add` | 3 | Appends a logbook entry (auto-partition) |
| `logsayer log index` | `logsayer reverend-mother log index` | 3 | Rebuilds `00_index.md` from real files |
| `logsayer check` | `logsayer suk doctor` | 4 | Mechanical checks: structure, no layer mixing, pending inbox, preset and declared adapters |
| `logsayer audit run` | `logsayer truthsayer audit run` | 4 | Generates the audit report + semantic prompt |
| `logsayer audit run --hu <HU>` | `logsayer truthsayer audit run --hu <HU>` | 4 | Re-emits the brief for one pass, to repeat a failed one (writes no report) |
| `logsayer audit status` | `logsayer truthsayer audit status` | 4 | Shows HU counter vs threshold, last report |
| `logsayer process check` | `logsayer fremen verify` | 5 | Process checks: Dor, coordination agreement, index freshness |

## Configuration (`logsayer.toml`)

Generated by `logsayer init`, tuned in a single file:

```toml
[logsayer]
session_close_context_threshold = 0.70   # % context used → propose session close
bitacora_max_lines = 400                 # lines/logbook file before partitioning
audit_threshold_hus = 3                  # HUs closed since last audit → trigger audit
inbox_max_age_days = 14                 # days unprocessed in inbox/ → warn about it aging
```

With `--preset`, two more blocks are written:

```toml
[project]
preset = "minimal"   # which preset produced this file — informational

[adapters]
enabled = ["claude"]   # what the preset declares; `agent add` is what generates them
```

### Presets

`init --preset <name>` resolves a bundle of conventions and writes it **once**, into
`logsayer.toml`. Two ship with the package:

| Preset | Adapters declared | Thresholds |
|---|---|---|
| `default` | none | the defaults — it overrides nothing |
| `minimal` | `claude` | looser: propose session close later, partition the logbook later, audit every 5 HUs, let `inbox/` age 30 days |

The preset is a **snapshot, not a live inheritance**: after `init` copies the values,
the preset stops existing for that project, so there is no "what if the preset changes
in the next version" to resolve, and the TOML stays editable without surprises. The
price is that upgrading logsayer does not upgrade the thresholds of a project already
scaffolded — which is what the two checks below are for.

To update an old project's thresholds by hand: edit the values under `[logsayer]`
in its `logsayer.toml`. That is the whole procedure — no migration command, no
preset re-application; the file is the interface.

Two mechanical checks keep the new keys honest, and neither corrects, only warns:

- **`preset_conocido`** — the declared preset no longer ships in the installed
  package. That is the real failure mode of a snapshot, and the warning names the
  version so you can tell when it happened.
- **`adaptadores_declarados`** — a name in `enabled` has no adapter implemented, or it
  has one but its files are not in the project yet. `init` declares and `agent add`
  generates: that distance is structural, and the check is what shows it.

`init --here` on a project that already has a `logsayer.toml` does **not** apply the
preset and says so — the project's TOML wins. Applying it halfway would be worse than
not applying it.

## How a session flows

1. **Session start** — the agent reads *only* the state layer (`docs/project_state.md`). Cheap in tokens, enough to orient.
2. **Audit check** — if the closed-HUs counter meets the threshold, the agent proactively proposes an audit (semantic verification).
3. **Work** — the agent works a HU reading only its folder under `docs/04_user_stories/`, and only opens a logbook entry when it needs the *"why"* of a past decision.
4. **Close / commit** — with your prior approval, the agent overwrites the state snapshot and appends to the active logbook.
5. **Auto-partition** — when the active logbook exceeds the line limit, the next file is created and the master index updated.

## Example session

A full transcript — run against a freshly scaffolded project — lives in [`examples/hello-logsayer/`](examples/hello-logsayer/README.md). It walks through scaffold, story creation, logbook entries, verification, agent adapters, and memory, with the actual output of every command.

## Multi-agent design

A single engine (`logsayer/core/`) plus one thin adapter per agent (`logsayer/adapters/<agent>/`) that only translates each tool's native file convention and calls the CLI. Adding a new agent means a new adapter, not new logic. See the [master spec](logsayer_especificacion_maestra.md) for the full architecture.

## Roadmap

- **0–2 (done):** naming & manifest, `init`, core commands (`spec`, `state`, `log`, `audit`).
- **3 (done):** the adapter layer, one engine and three thin adapters. Copilot was the last one, and it was the only one that needed a decision: Copilot separates the agent profile from the path-scoped instructions, so `agent add copilot` writes eight files — four profiles in `.github/agents/` and four instructions in `.github/instructions/logsayer/`.
- **4–6 (done):** mechanical validation (`check`, `process check`), docs & publishing, incoming documents (`inbox/`, `doc route`, `doc new`).
- **7 (done):** community presets — `init --preset <default|minimal>` writes a bundle of conventions once, as TOML inside the package. Further adapters are added on demand, not on a schedule: `agent add` names the ones not yet implemented.
- **8 (done):** selective memory — a generated index over `docs/`, a `tags` frontmatter contract, and a deterministic `memory search` (what to read first, never what is auditable).
- **9 (done):** audit by pass — the scope stops being a promise in the prompt and becomes a table the CLI counts, one row per HU on disk, with the `auditoria_completa` check.
- **10 (deferred):** extended frontmatter — it only lands if it hurts.

## Disclaimer (Dune homage)

> This project uses names and concepts from Frank Herbert's *Dune* saga exclusively as a thematic reference and role metaphor. It is not affiliated with, sponsored by, or officially associated with Herbert Properties LLC, Legendary Entertainment, or any rights holders of the franchise. No art, logos, or protected material is reproduced — only concept/role names as a design analogy.

## Acknowledgment & license

- MIT — see [LICENSE](LICENSE).
- Built around the 5-layer documentary system described in the [master spec](logsayer_especificacion_maestra.md).
- Names and concepts from *Dune* are used as a thematic role metaphor only (full disclaimer above).