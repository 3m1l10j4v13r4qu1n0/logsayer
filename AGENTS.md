# AGENTS.md — logsayer

CLI open source en Python que scaffoldea y coordina un sistema de 5 capas documentales para proyectos con agentes IA (Especificación, Estado, Bitácora, Verificación y Proceso). Stack: Python 3.11+, Typer, Jinja2, TOML (`logsayer.toml`), empaquetado con `pyproject.toml` + hatchling, distribución vía PyPI (`uv tool install` / `pipx`).

## Idioma y tono
- Responder siempre en español rioplatense, informal ("vos"). Nunca en inglés, aunque el código, logs o skills estén en inglés.
- La superficie pública del framework (rutas `docs/`, comandos, README) va en inglés; el contenido generado puede ir en español.

## Comandos del proyecto
- Instalar: `uv tool install .`
- Tests: `python -m pytest -q` (entorno: `.venv`)
- Lint/formato: `ruff check src tests`
- Tipado: `mypy src` (strict)

## Setup / gotchas
- Fuente de verdad absoluta: `logsayer_especificacion_maestra.md`. Reemplaza y consolida toda decisión previa (capas, roadmap, tema Dune, bot vs subagente, umbrales, estrategia multi-agente).
- `prompts_bootstrap_framework.md` es el flujo de prompts de bootstrap: define la constitución y las features del propio CLI.
- No inventar comandos, config ni estructura que no estén en la especificación maestra: verificar ahí antes de asumir.
- `__version__` vive en `src/logsayer/__init__.py` y debe seguir el `version` de `pyproject.toml`.

## Arquitectura del proyecto
- El CLI genera para proyectos usuarios: `docs/01_global/`, `docs/02_technical/`, `docs/03_process/`, `docs/04_user_stories/HU-XX/`, `docs/05_agile_methodology/`, `docs/06_audits/`; más `docs/project_state.md` (Capa 2) y `docs/logbooks/logbook_<fase>_NN.md` con `00_index.md` (Capa 3) — ver `src/logsayer/scaffold.py`.
- Motor único `logsayer/core/` + adaptadores por agente (`logsayer/adapters/<agente>/`) que solo traducen la convención de archivos nativa de cada herramienta e invocan comandos del CLI.
- Comandos con alias plano: `logsayer truthsayer audit run` ≡ `logsayer audit run`.

## Fuente de verdad
- `logsayer_especificacion_maestra.md` es la única fuente de verdad (nombre, 5 capas, estructura, umbrales, comandos, roadmap, stack, riesgos conocidos, disclaimer).
- Si el código real contradice la especificación, avisar antes de asumir.

## Reglas globales (no duplicar, ya cargadas vía config global)
- Git/git flow, anti-alucinación, APA y SOLID viven en `~/.config/opencode/rules/`. No copiarlas acá: si este repo necesita algo distinto, documentarlo JUSTIFICANDO la diferencia.

## Reglas del proyecto
- No duplicar lógica del framework dentro de los templates/adaptadores que genera el CLI: todo juicio vive en `logsayer/core/`, los archivos generados son wrappers finos (spec §6).

## Estado actual
- Fase 4 del roadmap (validación): `init`, `spec new`, `state show`, `log add` + `log index`, `audit run` + `audit status`, `agent add <opencode|claude>`, y `suk doctor`/`check` + `fremen verify`/`process check` implementados y verificados (tests + mypy + ruff).
- Pendientes del roadmap: fase 3 restante (copilot/cursor/gemini/hermes por demanda), fase 5 (README con disclaimer, PyPI, MIT, casos de ejemplo), fase 6 (comunidad).
- `main` tiene solo el bootstrap; feature branches convergen en `develop`; releases con tag semver (`v0.1.0`..`v0.4.0`).

## Memoria del proyecto (por definir)
- [ ] Dogfooding del propio repo: bootstrappear `docs/` de logsayer sobre sí mismo y mantener `docs/project_state.md` (Capa 2) + logbook (Capa 3).