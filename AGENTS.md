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

## Coordinación con docs/ (dogfooding)
Este repo usa logsayer sobre sí mismo (marco de sesiones, spec §7). Los umbrales viven en `logsayer.toml`; esto tiene que reflejarlos (lo verifica `logsayer fremen verify`).

### Al iniciar sesión
1. Leer `docs/project_state.md` (Capa 2, obligatorio, siempre).
2. Si el contador de HUs cerradas desde la última auditoría es >= 3 HUs, proponer auditoría (Decidora de Verdad) antes de tomar tarea nueva.
3. NO leer `docs/logbooks/` completa — solo `docs/logbooks/00_index.md` bajo demanda.

### Durante la sesión
- Si el uso de contexto supera el 70%, proponer cierre de sesión antes de tomar más tareas.
- Trabajar cada HU leyendo solo su carpeta en `docs/04_user_stories/`.
- Decisión de arquitectura nueva → candidata a entrada de logbook y a `docs/02_technical/decisions.md`; nunca se escribe directo en el estado.

### Al cerrar sesión o commit (requiere aprobación previa)
- Sobrescribir `docs/project_state.md` (snapshot, no acumulativo).
- Append en el logbook activo `docs/logbooks/logbook_dogfooding_NN.md`.
- Si el logbook activo supera las 400 líneas, crear `NN+1` y actualizar `00_index.md`.
- Si se cerró una HU, incrementar el contador de auditoría.

### Auditoría (Decidora de Verdad)
- Disparador: contador >= 3 HUs. Ejecutar `logsayer audit run`.
- Compara `docs/04_user_stories/` contra el código real; resultado en `docs/06_audits/audit_<fecha>.md`.
- Resetear el contador tras la aprobación.

## Estado actual
- Dogfooding del marco activo: logsayer se gobierna a sí mismo (docs/ bootstrappeado con `init --here` en modo adopt, HUs reales HU-01..05 en `docs/04_user_stories/`, logbooks por fase, auditoría 2026-09-24 aprobada y contador reseteado).
- Versión actual: `0.6.0` (sync entre `pyproject.toml` y `src/logsayer/__init__.py`). El modo adopt de `init --here` (spec §5) cerró la deuda de repositorios existentes, verificado con tests + check + fremen.
- Fases 0-5 del roadmap cerradas. Pendientes: publicar en PyPI (token de `3m1l10j4v13r4qu1n0`), fase 3 restante (copilot/cursor/gemini/hermes por demanda), fase 6 (comunidad: presets, más agentes).
- `main` tiene solo el bootstrap; feature branches convergen en `develop`; releases con tag semver (`v0.1.0`..`v0.6.0`).

## Memoria del proyecto
- [x] Dogfooding del propio repo: `docs/` bootstrappeado sobre sí mismo; `docs/project_state.md` (Capa 2), logbooks por fase (Capa 3) y auditoría (Capa 4) mantenidos en el marco de sesiones.