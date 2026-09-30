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

## Flujo de git (checklist exacto)
Lo que sigue es lo único que se agrega a la regla global de git: el ciclo y los comandos de este repo. Las ramas, los conventional commits en español y la prohibición de commitear directo en `main`/`develop` se rigen por `~/.config/opencode/rules/git.md`, no se repiten acá.

### Ciclo obligatorio (PR por feature)
1. `git checkout develop && git pull`
2. `git checkout -b feature/<tema>` (o `fix/<tema>`; una rama = una HU/tarea)
3. Trabajar y commitear (tema por commit). Antes de abrir el PR, integrar develop: `git fetch && git merge origin/develop` **dentro de la rama** y resolver los conflictos ahí.
4. `git push -u origin <rama>`
5. `gh pr create --base develop --head <rama> --title "..." --body "..."`
6. Merge a `develop` solo con `gh pr merge --merge <n>` (nunca squash) y **solo con aprobación explícita del usuario**. Lo mismo para push, PR y tag: sin aprobación, no se ejecuta.
7. Release: PR `develop` → `main` + tag semver en el commit de release.

### Checklist pre-merge (los tres, en verde)
- `python -m pytest -q`
- `ruff check src tests`
- `mypy src`

Divergencia justificada respecto del checklist genérico global: el proyecto no usa `black` (el formateo es `ruff`, y `black` no está en las dev dependencies de `pyproject.toml`). En consecuencia, `ruff format` es la única verificación de formato.

### Limpieza
- `git branch -d <rama>` para las locales ya mergeadas; remotas con `git branch -r --merged develop` y después `git push origin --delete <rama>`.
- Nunca borrar `main` ni `develop`.

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
2. Correr `logsayer check` (mecánico, read-only) y atender los avisos antes de tomar tarea.
3. Si el contador de HUs cerradas desde la última auditoría es >= 3 HUs, proponer auditoría (Decidora de Verdad) antes de tomar tarea nueva.
4. NO leer `docs/logbooks/` completa — solo `docs/logbooks/00_index.md` bajo demanda.

### Documentos entrantes
- Si el humano te entrega o menciona un documento externo (`.md`, `.pdf`, `.docx`, `.txt`) que no pertenece a este repo: recordarle `logsayer inbox add <archivo>` y delegar la ubicación al subagente **Mentat**. No moverlo, leerlo ni deducir su capa vos.
- La decisión de capa la toma Mentat; vos invocás `logsayer doc route` / `logsayer doc new`.
- Los `.md` en la raíz NO se escanean: son invisibles para `logsayer check` a propósito. No los crees en este repo.

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
- Dogfooding del marco activo: logsayer se gobierna a sí mismo (docs/ bootstrappeado con `init --here` en modo adopt, HUs reales HU-01..14 en `docs/04_user_stories/`, logbooks por fase, auditorías 2026-09-24, 2026-09-27 y 2026-09-29 aprobadas, contador reseteado a 0).
- Versión actual: `0.7.0` (sync entre `pyproject.toml` y `src/logsayer/__init__.py`), **publicada en PyPI el 2026-09-30** con el tag `v0.7.0`. El modo adopt de `init --here` (spec §5) cerró la deuda de repositorios existentes, verificado con tests + check + fremen.
- Fases 0-6, 8 y 9 del roadmap cerradas. La fase 6 (ingreso de documentos — `inbox/`, `inbox add`, `doc route`, `doc new`) se integró en `develop` el 2026-09-25 (`db35a63`). Publicaciones: `logsayer` 0.6.0 el 2026-09-25 y **0.7.0 el 2026-09-30** (el token va por variable de entorno, nunca en el repo).
- Fase 8 (memoria seleccionable) cerrada: diseño en `docs/02_technical/memory_architecture.md`, implementación en HU-10 (índice generado + frontmatter `tags`) y HU-11 (retrieval + check de frescura `indice_al_dia`). El grafo es capa transversal de navegación, no una sexta capa (D12).
- Fase 9 (auditoría por pasada) cerrada: el alcance dejó de ser una promesa en el prompt y pasó a ser una tabla que cuenta el CLI (D20), con el check `auditoria_completa` y `audit run --hu`. Diseño en `docs/02_technical/audit_protocol.md`, desglose en HU-12 y HU-13. La deuda de HU-07 la cerró HU-14 (PR #11, `a4e89d2`).
- Release 0.7.0 cortado: **0.7.0 = fase 6**, **0.8.0 = fases 8 y 9**. El tag `v0.7.0` está en `087a482` (merge de la auditoría del 2026-09-27, el 2026-09-28), el último commit antes de que el diseño de la fase 8 entre a `develop`. Verificado en ese árbol: declara 0.7.0, no trae `memory` ni `audit_protocol`, y el paquete instalado desde PyPI expone `inbox` y `doc` pero no `memory`. `main` sigue en 0.6.0 a propósito: no hay forma de que contenga solo la fase 6, porque es ancestro estricto de `develop`.
- Pendientes: redactar `[0.8.0]` del CHANGELOG con las fases 8 y 9 y bumpear a `0.8.0`; fase 3 restante (copilot/cursor/gemini/hermes por demanda); fase 7 (comunidad: presets, más agentes); y las dos deudas de código que dejó la auditoría del 2026-09-29 — el contador de HUs sin ningún check que lo verifique, y `audit run --reset-counter` scaffoldeando un reporte con el alcance vacío. La cola vive en `inbox/feedback_deudas_auditoria.md`.
- `main` tiene el bootstrap y el changelog; `develop` concentra el trabajo; releases con tag semver (`v0.1.0`..`v0.7.0`). Desde 2026-09-27 todo feature entra a `develop` por PR (flujo de la regla global, ver §Flujo de git).

## Memoria del proyecto
- [x] Dogfooding del propio repo: `docs/` bootstrappeado sobre sí mismo; `docs/project_state.md` (Capa 2), logbooks por fase (Capa 3) y auditoría (Capa 4) mantenidos en el marco de sesiones.
- [x] Checkdogfooding: el propio `logsayer check` corre contra este repo; los checks de Capa 1 (`header_capa1` exige el header estándar, `estado_al_dia` avisa cuando un documento de Capa 1 tiene fecha más nueva que el snapshot) se validaron contra este mismo repo y fallaron el primer día (D9).