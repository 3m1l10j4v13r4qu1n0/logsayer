# Example — `hello-logsayer`

A complete, real session against a project scaffolded with `examples` output. Every block below is the actual output from logsayer 0.5.0.

## Setup

```bash
logsayer init hello-logsayer
# Scaffold listo en hello-logsayer/hello-logsayer
cd hello-logsayer
```

The generated tree:

```
.
├── AGENTS.md
├── docs/
│   ├── project_state.md          # layer 2 — state (read at session start)
│   ├── logbooks/
│   │   └── 00_index.md           # layer 3 — master index
│   ├── 01_global/                # layer 1 — vision, scope, business rules
│   ├── 02_technical/             # layer 1 — technical decisions, models
│   ├── 03_process/               # layer 5 — DoR, merge checklist
│   ├── 04_user_stories/          # layer 1 — HU-01..HU-N
│   ├── 05_agile_methodology/     # layer 5 — working methodology
│   └── 06_audits/                # layer 4 — Suk Doctor + Truthsayer
└── logsayer.toml                 # thresholds
```

## 1. Definition of Ready (layer 5 — Fremen)

`logsayer process check` (alias: `logsayer fremen verify`):

```
Fremen — verificación de proceso de hello-logsayer

✔ estado_documentado: OK
✔ proceso_desplegado: OK
✔ acuerdo_coordinacion: OK
✔ definition_of_ready: OK

Estado: sano.
```

## 2. Define a user story (layer 1 — Mentat)

`logsayer spec new HU-01` (alias: `logsayer mentat spec new HU-01`):

```
HU HU-01 creada en docs/04_user_stories/HU-01/README.md
```

The template, kept deliberately minimal (spec §10):

```markdown
# HU-01 — Título de la historia

> Template mínimo: completar solo lo indispensable (spec §10).

## Qué hay que construir

_(Descripción concisa de la HU y su alcance.)_

## Cómo se valida

- _(Criterio de aceptación verificable.)_
```

## 3. Check the anchor (layer 2 — Navigator)

`logsayer state show` (alias: `logsayer navigator state show`) — the only thing the agent reads at session start:

```
# Estado del proyecto — hello-logsayer

> Snapshot operativo para el agente al iniciar cada sesión. No es acumulativo: ...

## Fase actual del roadmap

_(Definir la fase en la que está el proyecto.)_

## Decisiones activas (últimas 3-5)

- _(vacío)_

## HUs cerradas desde la última auditoría

0
```

## 4. Append decisions (layer 3 — Reverend Mother)

`logsayer log add "…"` (alias: `logsayer reverend-mother log add "…"`):

```
$ logsayer log add "Se decide el stack: Python 3.11 + Typer para el CLI."
Entrada registrada en docs/logbooks/logbook_general_01.md

$ logsayer log add "Se consume la API de pagos con idempotencia."
Entrada registrada en docs/logbooks/logbook_general_01.md
```

The append-only file:

```markdown
# Logbook — general (01)

- 2026-09-24 16:37 — Se decide el stack: Python 3.11 + Typer para el CLI.
- 2026-09-24 16:37 — Se consume la API de pagos con idempotencia.
```

`logsayer log index` rebuilds the master index from the real files:

```
Índice actualizado en docs/logbooks/00_index.md
```

```markdown
# Bitácoras — índice

| Archivo | Fase | Rango | Decisiones clave |
|---|---|---|---|
| logbook_general_01.md | general | 1 | 2026-09-24 16:37 — Se decide el stack: Python 3.11 + Typer para el CLI. |
```

## 5. Mechanical verification (layer 4 — Suk Doctor)

`logsayer check` (alias: `logsayer suk doctor`):

```
Suk Doctor — verificación mecánica de hello-logsayer

✔ marcadores_raiz: OK
✔ estructura_capas: OK
✔ estado_capa2: OK
✔ bitacora_indice: OK
✔ hus_ubicacion: OK
✔ capas_mezcladas: OK

Estado: sano.
```

## 6. Semantic verification (layer 4 — Truthsayer)

`logsayer audit status` (alias: `logsayer truthsayer audit status`):

```
HUs cerradas desde la última auditoría: 0 (umbral: 3)
Última auditoría: ninguna reportada.
Estado: no corresponde auditar (faltan 3 HUs).
```

`logsayer audit run` generates the report structure and the semantic prompt; the judgment itself is produced by the Truthsayer subagent (spec §10 — honest about the non-deterministic result):

```
Estructura y prompt generados en docs/06_audits/audit_2026-09-24.md
Contador intacto. Al aprobar, corre de nuevo con --reset-counter.
```

```
docs/06_audits/
├── audit_2026-09-24.md
└── audit_2026-09-24.prompt.md
```

## 7. Agent adapters (openocode / Claude Code)

`logsayer agent add opencode` and `logsayer agent add claude` generate thin per-role subagents that call the CLI:

```
Generado: .opencode/agents/mentat.md
Generado: .opencode/agents/navigator.md
Generado: .opencode/agents/reverend-mother.md
Generado: .opencode/agents/truthsayer.md
```

```
Generado: .claude/agents/mentat.md
Generado: .claude/agents/navigator.md
Generado: .claude/agents/reverend-mother.md
Generado: .claude/agents/truthsayer.md
```

## Why this is all there is

Each layer answers one question, and every document lives in exactly one layer. The logbook holds the *why* (episodic), the state holds the *now* (snapshot, non-accumulative), and the verification loop confirms what was built still matches what was specified. Nothing more — that is the whole system.