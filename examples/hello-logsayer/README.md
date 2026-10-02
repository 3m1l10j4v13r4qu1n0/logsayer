# Example — `hello-logsayer`

A complete, real session against a project scaffolded with `examples` output. Every block below is the actual output from logsayer 0.6.0.

## Setup

```bash
logsayer init hello-logsayer
# Scaffold listo en hello-logsayer/hello-logsayer
# Generado: inbox/.gitignore
# Generado: AGENTS.md
# Generado: logsayer.toml
# Generado: docs/project_state.md
# Generado: docs/logbooks/00_index.md
cd hello-logsayer
```

The generated tree:

```
.
├── AGENTS.md
├── inbox/                         # incoming documents — not a layer, not versioned
│   └── .gitignore                 # ignores its own contents
├── docs/
│   ├── project_state.md           # layer 2 — state (read at session start)
│   ├── logbooks/
│   │   └── 00_index.md            # layer 3 — master index
│   ├── 01_global/                 # layer 1 — vision, scope, business rules
│   ├── 02_technical/              # layer 1 — technical decisions, models
│   ├── 03_process/                # layer 5 — DoR, merge checklist
│   ├── 04_user_stories/           # layer 1 — HU-01..HU-N
│   ├── 05_agile_methodology/      # layer 5 — working methodology
│   └── 06_audits/                 # layer 4 — Suk Doctor + Truthsayer
└── logsayer.toml                  # thresholds
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
✔ bandeja_entrada: vacía

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
! bandeja_entrada: 2 sin ubicar (umbral de aviso: 14 días)
   - inbox/acta_reunion.pdf
   - inbox/contrato_api_backend.md
   siguiente: logsayer doc route <archivo>  (Mentat decide la capa)

Estado: sano con 1 chequeo(s) en aviso. No bloquea, pero atendelos.
```

The host agent delegates to the **Mentat** subagent, whose job is to answer "which
layer?". `doc route` deliberately does *not* answer that for it. Given a `.md`
whose name does not declare a HU, the CLI says so and hands over the candidates —
it only decides when the signal is unambiguous (a non-markdown extension, or a HU
in the name):

```bash
logsayer doc route inbox/contrato_api_backend.md
```

```
→ sin decisión automática. El nombre no dice si el documento es global o técnico. Eso lo decide Mentat; el CLI no lo clasifica.
→ pista:      el nombre tiene términos técnicos (contrato, api): 02_technical/ es el primer candidato, pero eso no lo decide el CLI.

Candidatos:
  · 1 — Especificación → docs/02_technical/ — crear con: logsayer doc new technical <nombre>
  · 1 — Especificación → docs/01_global/ — crear con: logsayer doc new global <nombre>
  · 1 — Especificación → docs/04_user_stories/<HU>/ — crear con: logsayer spec new <HU>

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
# Contrato api backend

> Documento de Capa 1 — Especificación. Completa solo lo indispensable (spec §10).

Fecha: 2026-09-25 · Estado: borrador

## Resumen

_(Una o dos líneas: qué establece este documento.)_

## Fuente

- Origen: `inbox/_done/contrato_api_backend.md` (recibido el 2026-09-25)

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
! bandeja_entrada: 1 sin ubicar (umbral de aviso: 14 días)
   - inbox/acta_reunion.pdf
   siguiente: logsayer doc route <archivo>  (Mentat decide la capa)
! estado_al_dia: Capa 1 cambió después del último estado (1): docs/02_technical/contrato_api_backend.md
   → actualizá docs/project_state.md al cierre de la sesión

Estado: sano con 2 chequeo(s) en aviso. No bloquea, pero atendelos.
```

The full table is one command away, any time someone asks "where does this
go?":

```bash
logsayer doc route
```


igdónde va mi documento?

| Entrada                                                          | Va a                                                       | ¿Se versiona?                            | Crear con                           |
|------------------------------------------------------------------|------------------------------------------------------------|------------------------------------------|-------------------------------------|
| Documento de un equipo externo, entrega, acta o informe recibido | fuera de docs/ (bandeja `inbox/`), y su derivado en Capa 1 | el original no; el documento derivado sí | logsayer inbox add <archivo>        |
| Contrato transversal: API, DTOs, modelo de datos, stack          | 1 — Especificación → docs/02_technical/                    | sí                                       | logsayer doc new technical <nombre> |
| Visión, alcance, regla de negocio o requisito global             | 1 — Especificación → docs/01_global/                       | sí                                       | logsayer doc new global <nombre>    |
| Contrato o criterio que aplica a una HU puntual                  | 1 — Especificación → docs/04_user_stories/<HU>/            | sí                                       | logsayer spec new <HU>              |
| Informe de auditoría sobre un documento externo                  | Capa 4 → docs/06_audits/audit_<fecha>-<area>.md            | sí                                       | logsayer audit run                  |
| El 'por qué' o el 'cómo' de lo que ya se hizo                    | Capa 3 → bitácora (append-only)                            | sí                                       | logsayer log add "…"                |

Nunca: un .md suelto en docs/. Es lo que `logsayer check` rechaza como capas_mezcladas.

El CLI no redacta el contenido: elige la capa y creá el documento con el comando de la fila.


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