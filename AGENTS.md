# AGENTS.md — logsayer

CLI open source en Python que scaffoldea y coordina un sistema de 5 capas documentales para proyectos con agentes IA (Especificación, Estado, Bitácora, Verificación y Proceso). Stack: Python 3.11+, Typer, Jinja2, TOML (`logsayer.toml`), empaquetado con `pyproject.toml` + hatchling, distribución vía PyPI (`uv tool install` / `pipx`).

## Idioma y tono
- Responder siempre en español rioplatense, informal ("vos"). Nunca en inglés, aunque el código, logs o skills estén en inglés.
- La superficie pública del framework (rutas `docs/`, comandos, README) va en inglés; el contenido generado puede ir en español.

## Comandos del proyecto
- Instalar: `uv tool install .` (una vez exista `pyproject.toml`)
- Tests: por definir (sin código todavía)
- Lint/formato: por definir (sin código todavía)

## Setup / gotchas
- Fuente de verdad absoluta: `logsayer_especificacion_maestra.md`. Reemplaza y consolida toda decisión previa (capas, roadmap, tema Dune, bot vs subagente, umbrales, estrategia multi-agente).
- `prompts_bootstrap_framework.md` es el flujo de prompts de bootstrap: define la constitución y las features del propio CLI.
- No inventar comandos, config ni estructura que no estén en la especificación maestra: verificar ahí antes de asumir.

## Arquitectura del proyecto
- Estructura que el CLI va a generar para proyectos usuarios (Capa 1): `docs/01_global/`, `docs/02_technical/`, `docs/03_process/`, `docs/04_user_stories/HU-XX/`, `docs/05_agile_methodology/`, `docs/06_audits/`; más `docs/project_state.md` (Capa 2) y `docs/logbooks/logbook_<fase>_NN.md` con `00_index.md` (Capa 3). El repo del CLI todavía no scaffoldea esos directorios.
- Motor único `logsayer/core/` + adaptadores finos por agente (`logsayer/adapters/<agente>/`).
- Comandos con alias plano: `logsayer truthsayer audit run` ≡ `logsayer audit run`.

## Fuente de verdad
- `logsayer_especificacion_maestra.md` es la única fuente de verdad (nombre, 5 capas, estructura, umbrales, comandos, roadmap, stack, riesgos conocidos, disclaimer).
- Si el código real contradice la especificación, avisar antes de asumir.

## Reglas globales (no duplicar, ya cargadas vía config global)
- Git/git flow, anti-alucinación, APA y SOLID viven en `~/.config/opencode/rules/`. No copiarlas acá: si este repo necesita algo distinto, documentarlo JUSTIFICANDO la diferencia.

## Reglas del proyecto (placeholders a completar)
- [ ] `.opencode/rules/stack.md` — convenciones del stack una vez haya código
- [ ] Definir comandos build/test/lint reales cuando exista el primer CLI

## Estado actual
- Fase 0/1 del roadmap: definición prácticamente cerrada (nombre `logsayer` ✅, manifiesto y plan en la especificación maestra).
- Repo en GitHub: `3m1l10j4v13r4qu1n0/logsayer` (público, remote `origin` vía SSH, branch `main`). Sin commits todavía.
- Pendientes: `pyproject.toml` con Typer, schema de `logsayer.toml`, primer `init` funcional (dogfooding desde el commit 1).

## Memoria del proyecto (por definir)
- [ ] Estado del proyecto: `docs/project_state.md` (Capa 2 — Navegante)
- [ ] Bitácora: `docs/logbooks/logbook_<fase>_NN.md` con índice `docs/logbooks/00_index.md` (Capa 3 — Reverenda Madre)