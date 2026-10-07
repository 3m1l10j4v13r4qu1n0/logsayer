# Example — `hello-logsayer`

A complete, real session against a project scaffolded with logsayer 0.8.0. Every
block below is the actual output from the CLI — nothing is hand-written or
edited. Working directory is shown as `~/projects` for brevity.

## Setup

```bash
logsayer init hello-logsayer
# Scaffold listo en ~/projects/hello-logsayer
# Generado: inbox/.gitignore
# Generado: AGENTS.md
# Generado: logsayer.toml
# Generado: docs/project_state.md
# Generado: docs/logbooks/00_index.md
cd hello-logsayer
```

`init` materializes a preset into `logsayer.toml` once — the preset is a
snapshot, not a live inheritance (`--preset default` is the behavior above,
`--preset minimal` picks looser thresholds):

```bash
logsayer init hello-logsayer --preset minimal
```

The generated tree:

```
.
├── AGENTS.md
├── docs
│   ├── 01_global               # layer 1 — vision, scope, business rules
│   │   └── .gitkeep
│   ├── 02_technical            # layer 1 — technical decisions, models
│   │   └── .gitkeep
│   ├── 03_process              # layer 5 — DoR, merge checklist
│   │   └── .gitkeep
│   ├── 04_user_stories         # layer 1 — HU-01..HU-N
│   │   └── .gitkeep
│   ├── 05_agile_methodology    # layer 5 — working methodology
│   │   └── .gitkeep
│   ├── 06_audits               # layer 4 — Suk Doctor + Truthsayer
│   │   └── .gitkeep
│   ├── logbooks
│   │   ├── 00_index.md         # layer 3 — master index
│   │   └── .gitkeep
│   └── project_state.md        # layer 2 — state (read at session start)
├── inbox
│   └── .gitignore              # incoming documents — not a layer, not versioned
└── logsayer.toml               # thresholds
```

## 1. Definition of Ready (layer 5 — Fremen)

`logsayer process check` (alias: `logsayer fremen verify`):

```
Fremen — verificación de proceso de hello-logsayer

✔ estado_documentado: OK
✔ proceso_desplegado: OK
✔ acuerdo_coordinacion: OK
✔ definition_of_ready: OK
✔ indice_al_dia: sin índice (opcional)

Estado: sano.
```

## 2. Define a user story (layer 1 — Mentat)

`logsayer spec new HU-01` (alias: `logsayer mentat spec new HU-01`):

```
HU HU-01 creada en ~/projects/hello-logsayer/docs/04_user_stories/HU-01/README.md
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

`logsayer state show` (alias: `logsayer navigator state show`) — the only thing
the agent reads at session start:

```
---
fase: _(slug de la fase)_
---
# Estado del proyecto — hello-logsayer

> Snapshot operativo para el agente al iniciar cada sesión. No es acumulativo: se
> sobrescribe al cerrar sesión con aprobación previa. No dupliques contenido de
> specs ni repitas el roadmap completo.

## Fase actual del roadmap

_(Definir la fase en la que está el proyecto. El slug de arriba manda: es lo que
`logsayer log add` usa para elegir la bitácora. Solo se acepta un identificador
corto —letras, dígitos, `-`, `_` o `.`— sin espacios ni frases.)_

## Decisiones activas (últimas 3-5)

- _(vacío)_

## HUs cerradas desde la última auditoría

0
```

The `fase:` value in the frontmatter is what picks the logbook name.

## 4. Append decisions (layer 3 — Reverend Mother)

A fresh project has a placeholder there, so `log add` warns and falls back to
`general` instead of partitioning silently (D17):

```bash
logsayer log add "Se decide el stack: Python 3.11 + Typer para el CLI."
```

```
Entrada registrada en docs/logbooks/logbook_general_01.md

! Sin fase declarada en docs/project_state.md: la entrada cayó en 'general'.
  Declarala en el frontmatter (campo 'fase:') o pasá --fase para no partir la bitácora.
```

Declare the phase once, then append freely:

```bash
logsayer log add --fase general "Se decide el stack: Python 3.11 + Typer para el CLI."
logsayer log add --fase general "Se consume la API de pagos con idempotencia."
# Entrada registrada en docs/logbooks/logbook_general_01.md   (x2)
```

The append-only file:

```markdown
# Logbook — general (01)

- 2026-10-07 13:04 — Se decide el stack: Python 3.11 + Typer para el CLI.
- 2026-10-07 13:04 — Se consume la API de pagos con idempotencia.
```

`logsayer log index` rebuilds the master index from the real files:

```
Índice actualizado en docs/logbooks/00_index.md
```

```markdown
# Bitácoras — índice

| Archivo | Fase | Rango | Decisiones clave |
|---|---|---|---|
| logbook_general_01.md | general | 1 | 2026-10-07 13:04 — Se decide el stack: Python 3.11 + Typer para el CLI. |
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
✔ header_capa1: OK
✔ bandeja_entrada: vacía
✔ estado_al_dia: OK
✔ auditoria_completa: sin auditoría (opcional)
✔ contador_hus_al_dia: sin auditoría sellada; no se mide
✔ preset_conocido: sin preset declarado
✔ adaptadores_declarados: sin adaptadores declarados

Estado: sano.
```

## 5b. An incoming document (layer 1 — Mentat)

The backend team delivered a contract. It arrives as a file with no home in the
project. `inbox/` is where it goes.

```bash
logsayer inbox add ~/Downloads/contrato_api_backend.md
# Movido a inbox/contrato_api_backend.md
# Siguiente: logsayer doc route inbox/contrato_api_backend.md
```

A PDF comes in too — the CLI flags it instead of pretending it can read it:

```bash
logsayer inbox add ~/Downloads/acta_reunion.pdf
# Movido a inbox/acta_reunion.pdf
# Aviso: acta_reunion.pdf no es markdown. Convertilo antes de derivarlo (el CLI no
# convierte PDF ni docx); el documento derivado va en Capa 1 y este archivo queda
# en la bandeja.
# Siguiente: logsayer doc route inbox/acta_reunion.pdf
```

`logsayer inbox` on its own shows what is waiting:

```
Bandeja — 2 documento(s) esperando ubicación:
  - inbox/acta_reunion.pdf
  - inbox/contrato_api_backend.md
siguiente: logsayer doc route <archivo>  (Mentat decide la capa)
```

Now the session opens, and `check` reports them. A pending document is a `warn`,
not a `fail` — the exit code stays 0:

```bash
logsayer check
```

```
Suk Doctor — verificación mecánica de hello-logsayer

✔ marcadores_raiz: OK
✔ estructura_capas: OK
✔ estado_capa2: OK
✔ bitacora_indice: OK
✔ hus_ubicacion: OK
✔ capas_mezcladas: OK
✔ header_capa1: OK
! bandeja_entrada: 2 sin ubicar (umbral de aviso: 14 días)
   - inbox/acta_reunion.pdf
   - inbox/contrato_api_backend.md
   siguiente: logsayer doc route <archivo>  (Mentat decide la capa)
! estado_al_dia: Capa 1 cambió después del último estado (1): docs/04_user_stories/HU-01/README.md
   → actualizá docs/project_state.md al cierre de la sesión
✔ auditoria_completa: sin auditoría (opcional)
✔ contador_hus_al_dia: sin auditoría sellada; no se mide
✔ preset_conocido: sin preset declarado
✔ adaptadores_declarados: sin adaptadores declarados

Estado: sano con 2 chequeo(s) en aviso. No bloquea, pero atendelos.
```

The host agent delegates to the **Mentat** subagent, whose job is to answer "which
layer?". `doc route` deliberately does *not* answer that for it. Given a `.md`
whose name does not declare a HU, the CLI says so and hands over the candidates
without repeating the layer prefix (the layering is the judge's business, not the
scaffold's):

```bash
logsayer doc route inbox/contrato_api_backend.md
```

```
→ sin decisión automática. El nombre no dice si el documento es global o técnico. Eso lo decide Mentat; el CLI no lo clasifica.
→ pista:      el nombre tiene términos técnicos (contrato, api): 02_technical/ es el primer candidato, pero eso no lo decide el CLI.

Candidatos:
  · docs/02_technical/ — crear con: logsayer doc new technical <nombre>
  · docs/01_global/ — crear con: logsayer doc new global <nombre>
  · docs/04_user_stories/<HU>/ — crear con: logsayer spec new <HU>

Elegí la fila que corresponde y creá el documento con ese comando. Si ninguna aplica, la fila es 'El por qué o el cómo de lo que ya se hizo' (bitácora).
```

Mentat reads the delivered file, sees it is an API contract, and picks the first
candidate. `doc new` then scaffolds the document. The original is archived —
never deleted — and its provenance is recorded, so this document becomes the
version of reference:

```bash
logsayer doc new technical contrato_api_backend --from inbox/contrato_api_backend.md
# Documento creado en docs/02_technical/contrato_api_backend.md
# Origen archivado en inbox/_done/contrato_api_backend.md
# El contenido lo deriva el subagente Mentat: el CLI solo lo scaffoldeó.
```

`docs/02_technical/contrato_api_backend.md`:

```markdown
---
# Tags del índice de memoria (D13): el CLI las scaffoldea, el Mentat ajusta.
tags:
  - contrato
  - api
  - backend
---

# Contrato api backend

> Documento de Capa 1 — Especificación. Completa solo lo indispensable (spec §10).

Fecha: 2026-10-07 · Estado: borrador

## Resumen

_(Una o dos líneas: qué establece este documento.)_

## Fuente

- Origen: `inbox/_done/contrato_api_backend.md` (recibido el 2026-10-07)

## Qué establece

_(Alcance, supuestos y límites. Si aplica a una sola HU, linkeala.)_

## Cómo se valida

- _(Criterio verificable. El CLI no redacta esto: lo escribís vos o el Mentat.)_
```

Mentat now fills in *Qué establece* and *Cómo se valida* from the delivered
file. That is the split: **the CLI moves and names, the agent derives.**

A re-delivery of the same document is caught instead of duplicated:

```bash
logsayer doc route inbox/contrato_api_backend.md
# → sin destino: Ya existe un documento con ese nombre: docs/02_technical/contrato_api_backend.md.
#   No lo dupliques: actualizá ese, o renombrá el entrante.
```

And after the session, `check` also points at the other kind of drift — a
layer-1 document newer than the snapshot. That one is `warn` too, because the
honest fix is at the end of the session, not in the middle of the work:

```
! bandeja_entrada: 2 sin ubicar (umbral de aviso: 14 días)
   - inbox/acta_reunion.pdf
   - inbox/contrato_api_backend.md
   siguiente: logsayer doc route <archivo>  (Mentat decide la capa)
! estado_al_dia: Capa 1 cambió después del último estado (2): docs/02_technical/contrato_api_backend.md; docs/04_user_stories/HU-01/README.md
   → actualizá docs/project_state.md al cierre de la sesión

Estado: sano con 2 chequeo(s) en aviso. No bloquea, pero atendelos.
```

The full table is one command away, any time someone asks "where does this
go?":

```bash
logsayer doc route
```

```
¿Dónde va mi documento?

| Entrada                                                          | Va a                                                       | ¿Se versiona?                            | Crear con                           |
|------------------------------------------------------------------|------------------------------------------------------------|------------------------------------------|-------------------------------------|
| Documento de un equipo externo, entrega, acta o informe recibido | fuera de docs/ (bandeja `inbox/`), y su derivado en Capa 1 | el original no; el documento derivado sí | logsayer inbox add <archivo>        |
| Contrato transversal: API, DTOs, modelo de datos, stack          | 1 — Especificación → docs/02_technical/                    | sí                                       | logsayer doc new technical <nombre> |
| Visión, alcance, regla de negocio o requisito global             | 1 — Especificación → docs/01_global/                       | sí                                       | logsayer doc new global <nombre>    |
| Contrato o criterio que aplica a una HU puntual                  | 1 — Especificación → docs/04_user_stories/<HU>/            | sí                                       | logsayer spec new <HU>              |
| Informe de auditoría sobre un documento externo                  | Capa 4 → docs/06_audits/audit_<fecha>-<area>.md            | sí                                       | logsayer audit run                  |
| El "por qué" o el "cómo" de lo que ya se hizo                    | Capa 3 → bitácora (append-only)                            | sí                                       | logsayer log add "…"                |

Nunca: un .md suelto en docs/. Es lo que `logsayer check` rechaza como capas_mezcladas.

El CLI no redacta el contenido: elige la capa y creá el documento con el comando de la fila.
```

## 6. Semantic verification (layer 4 — Truthsayer)

`logsayer audit status` (alias: `logsayer truthsayer audit status`):

```
HUs cerradas desde la última auditoría: 0 (umbral: 3)
Última auditoría: ninguna
Derivadas del disco: no se mide (sin auditoría sellada).
Estado: en pausa. Restan 3 HUs para proponer auditoría.
```

`logsayer audit run` generates the report structure and the semantic prompt; the
judgment itself is produced by the Truthsayer subagent (spec §10 — honest about
the non-deterministic result):

```
Estructura y prompt generados en docs/06_audits/audit_2026-10-07.md
Contador intacto. Al aprobar, corre logsayer audit reset.
```

The report ships with a worklist table — every row the Decidora must fill — and
a synthesis section that is only read at the end:

```
docs/06_audits/
├── audit_2026-10-07.md
└── audit_2026-10-07.prompt.md
```

`docs/06_audits/audit_2026-10-07.md`:

```markdown
# Auditoría 2026-10-07 — hello-logsayer

> Estructura generada por el CLI. No es un resultado: la ejecuta la Decidora de
> Verdad comparando spec vs código real. No rellenar con "todo ok".

## HUs cerradas desde la última auditoría

0

## Alcance

Las filas de la tabla las generó el CLI enumerando `docs/04_user_stories/HU-*/`
(sin reporte previo).
El alcance lo decide el disco, no el agente: **agregá el veredicto de cada fila,
no borres ni agregues filas**. Un hueco es una auditoría que pasó por omisión
(D14), y `logsayer check` lo señala con `auditoria_completa`.

Es la primera auditoría con worklist: ninguna HU hereda veredicto.

## Veredicto por HU

| HU | Veredicto | Evidencia |
| --- | --- | --- |
| HU-01 | — | — |

## Sintesis entre HUs

_(Se completa al final, leyendo solo los veredictos de la tabla. Si no hay
ninguna contradicción, escribí "sin contradicciones detectadas": un vacío no
distingue "no encontré nada" de "no corrí".)_

## Resultado

_(Resumen y próximos pasos.)_
```

A single row can be re-run in isolation — the worklist stays the input, so the
scope never shrinks by accident (D22):

```bash
logsayer audit run --hu HU-01
# Brief de la pasada HU-01 generado en docs/06_audits/audit_2026-10-07-hu-01.prompt.md
# El alcance no cambia: es el input de repetir una fila.
```

Approval step is a dedicated command, not a flag: `audit reset` only resets the
counter, and refuses while any verdict is still pending (D20 — a gap would be an
audit that passed by omission):

```bash
logsayer audit reset
# Usage: python -m logsayer audit reset [OPTIONS]
# ╭─ Error ─────────────────────────────────────────────────────────────────────╮
# │ Invalid value: Hay HUs con veredicto pendiente: HU-01. Completalas antes de │
# │ resetear.                                                                    │
# ╰──────────────────────────────────────────────────────────────────────────────╯
```

## 7. Agent adapters (opencode / Claude Code / Copilot)

`logsayer agent add <agente>` generates thin per-role subagents that call the
CLI. Adapters differ per agent because the permission surface follows what the
tool can actually enforce (D24):

```
$ logsayer agent add opencode
Generado: .opencode/agents/mentat.md
Generado: .opencode/agents/navigator.md
Generado: .opencode/agents/reverend-mother.md
Generado: .opencode/agents/truthsayer.md

$ logsayer agent add claude
Generado: .claude/agents/mentat.md
Generado: .claude/agents/navigator.md
Generado: .claude/agents/reverend-mother.md
Generado: .claude/agents/truthsayer.md
```

Copilot writes **two files per role** — the profile and the path-scoped
instruction — so the Decidora's rules never leak into every context of the repo
(D36):

```
$ logsayer agent add copilot
Generado: .github/agents/mentat.agent.md
Generado: .github/agents/navigator.agent.md
Generado: .github/agents/reverend-mother.agent.md
Generado: .github/agents/truthsayer.agent.md
Generado: .github/instructions/logsayer/mentat.instructions.md
Generado: .github/instructions/logsayer/navigator.instructions.md
Generado: .github/instructions/logsayer/reverend-mother.instructions.md
Generado: .github/instructions/logsayer/truthsayer.instructions.md
```

Nothing (including Copilot's `.github/copilot-instructions.md`) is generated
beyond these: `AGENTS.md` is the project prompt and Copilot consumes it natively
(D37), so a second file would be a second source of truth for the same thing.

## 8. Memory (transversal — not a layer)

The memory index is a navigation roadmap over the five layers, not a sixth
layer. It is generated, never curated by hand:

```bash
logsayer memory index
# Índice actualizado en docs/00_memory_index.md (7 documentos)
```

```bash
logsayer memory status
# Índice de memoria
#   artefacto: docs/00_memory_index.md
#   documentos: 7
#   tags: 1 declaradas en frontmatter, 6 derivadas
#   generado: 2026-10-07 13:07
# 
# Regenerar con: logsayer memory index
```

The tags come from the frontmatter `tags:` block that `doc new` scaffolded (D13)
plus derivations from the paths:

```markdown
# Índice de memoria

<!-- Generado por 'logsayer memory index'. No editar a mano. -->

project_state.md                     · nivel 0 · — · — · project, state
02_technical/contrato_api_backend.md · nivel 1 · borrador · 2026-10-07 · contrato, api, backend
04_user_stories/HU-01/README.md      · nivel 2 · — · — · hu-01
06_audits/audit_2026-10-07.md        · nivel 3 · — · — · audit
06_audits/audit_2026-10-07.prompt.md · nivel 3 · — · — · audit, prompt
logbooks/00_index.md                 · nivel 3 · — · —
logbooks/logbook_general_01.md       · nivel 3 · — · — · logbook, general
```

`memory search` orders what to read first — it never decides what is auditable
(D14):

```bash
logsayer memory search "contrato"
# 1 de 7 documentos · 'contrato'
#   1. 02_technical/contrato_api_backend.md · nivel 1 · contrato
```

And `process check` now confirms the index is fresh:

```
Fremen — verificación de proceso de hello-logsayer

✔ estado_documentado: OK
✔ proceso_desplegado: OK
✔ acuerdo_coordinacion: OK
✔ definition_of_ready: OK
✔ indice_al_dia: OK

Estado: sano.
```

## Tree after the session

```
.
├── AGENTS.md
├── .claude
│   └── agents
│       ├── mentat.md
│       ├── navigator.md
│       ├── reverend-mother.md
│       ├── truthsayer.md
├── docs
│   ├── 00_memory_index.md
│   ├── 01_global
│   │   └── .gitkeep
│   ├── 02_technical
│   │   ├── contrato_api_backend.md
│   │   └── .gitkeep
│   ├── 03_process
│   │   └── .gitkeep
│   ├── 04_user_stories
│   │   ├── .gitkeep
│   │   └── HU-01
│   │       └── README.md
│   ├── 05_agile_methodology
│   │   └── .gitkeep
│   ├── 06_audits
│   │   ├── audit_2026-10-07.md
│   │   ├── audit_2026-10-07.prompt.md
│   │   └── .gitkeep
│   ├── logbooks
│   │   ├── 00_index.md
│   │   ├── .gitkeep
│   │   └── logbook_general_01.md
│   └── project_state.md
├── .github
│   ├── agents
│   │   ├── mentat.agent.md
│   │   ├── navigator.agent.md
│   │   ├── reverend-mother.agent.md
│   │   └── truthsayer.agent.md
│   └── instructions
│       └── logsayer
│           ├── mentat.instructions.md
│           ├── navigator.instructions.md
│           ├── reverend-mother.instructions.md
│           └── truthsayer.instructions.md
├── inbox
│   ├── acta_reunion.pdf
│   ├── contrato_api_backend.md
│   ├── _done
│   │   └── contrato_api_backend.md
│   └── .gitignore
├── logsayer.toml
└── .opencode
    └── agents
        ├── mentat.md
        ├── navigator.md
        ├── reverend-mother.md
        └── truthsayer.md
```

## Why this is all there is

Each layer answers one question, and every document lives in exactly one layer.
The logbook holds the *why* (episodic), the state holds the *now* (snapshot,
non-accumulative), and the verification loop confirms what was built still
matches what was specified. The memory index navigates it without competing with
it, and the agents only translate the convention to each tool's files. Nothing
more — that is the whole system.