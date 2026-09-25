# Changelog

Todos los cambios notables de logsayer quedan documentados acá, por versión, en orden cronológico inverso. Formato [Keep a Changelog](https://keepachangelog.com/es/1.1.0/), versionado [semver](https://semver.org/lang/es/).

## [Unreleased]

## [0.7.0] — 2026-09-25

Fase 6 del roadmap: **ingreso de documentos**. El feedback de usabilidad del 2026-09-25 señaló un problema de diseño, no de fricción: un documento que entra al proyecto no tenía puerta de entrada, y `logsayer check` no iba a señalarlo. Ahora hay bandeja, ruteo explícito y un ejemplo público.

### Added
- **`logsayer inbox add <archivo>`**: mueve un documento externo a `inbox/` (staging, hermano de `docs/`, no es una capa) e informa el siguiente paso. Archiva en `inbox/_done/`, nunca borra.
- **`logsayer doc route [archivo]`**: tabla explícita "dónde va mi documento" (`core/routing.py`). Con argumento, devuelve los **candidatos** y decide solo con señal inequívoca (extensión no markdown, o HU en el nombre); sin argumento, muestra la tabla completa.
- **`logsayer inbox`** sin subcomando lista los documentos esperando ubicación.
- `doc route` detecta el reenvío de un documento que ya existe en Capa 1 y avisa que no se duplique.
- **`logsayer doc new <capa> <nombre> [--from <origen>]`**: scaffoldea documentos de Capa 1 (`global` / `technical`) desde el template `doc.md.j2`, registra la procedencia en `## Fuente` y archiva el original.
- **Alias `logsayer mentat`**: subagente que decide la capa del documento entrante (adaptadores opencode y Claude, con permisos actualizados).
- **Check `bandeja_entrada`**: documentos sin ubicar o con antigüedad mayor a `inbox_max_age_days` (default 14).
- **Check `header_capa1`**: exige `# Título`, `Fecha: YYYY-MM-DD · Estado: …` y `## Resumen` en `01_global/` y `02_technical/`.
- **Check `estado_al_dia`**: avisa cuando un documento de Capa 1 tiene fecha de versión más nueva que `project_state.md`.
- **Nivel `warn` en `CheckResult`**: los avisos se muestran pero no rompen el flujo (`logsayer check` sale con 0).
- **Sección "Incoming documents" en el README** y transcript real en `examples/hello-logsayer/README.md` (`inbox add` → `check` → `doc route` → `doc new`).

### Changed
- `CheckResult.ok` pasa a ser propiedad de `status: Literal["ok", "warn", "fail"]`; solo `fail` produce exit code 1.
- `capas_mezcladas` ahora sugiere destino (`sugerido: …`) además de señalar el archivo.
- **El CLI propone la capa, no la decide.** Se eliminó el default a `docs/02_technical/`: un `.md` entrante que en realidad es visión de producto ya no termina en la carpeta técnica por accidente. El subagente Mentat elige entre los candidatos.
- `scaffold()` crea `inbox/` con su propio `.gitignore`.
- `logsayer.toml` acepta `inbox_max_age_days`.
- Los documentos de Capa 1 del propio repo (`mission.md`, `decisions.md`, `tech-stack.md`) se normalizaron con el header estándar.

### Fixed
- El `.gitignore` de `inbox/` ya no se ignora a sí mismo (`*` + `!.gitignore`).

## [0.6.0] — 2026-09-24

### Added
- **Modo adopt en `logsayer init --here`** (spec §5): scaffoldea sobre un repositorio existente — crea lo que falta (capa de `docs/`, `logsayer.toml`) y **no sobrescribe** archivos ya presentes (`AGENTS.md`, estado, índice). Cierra la deuda entre la especificación y el código.
- **Dogfooding activo**: el propio repo ahora se gobierna con logsayer (Capa 1-5 en `docs/`), con HUs reales HU-01..05, logbooks por fase y auditoría 2026-09-24 aprobada.

### Changed
- `scaffold()` acepta `adopt` y devuelve los paths escritos; el CLI reporta qué se preservó y qué se generó.

## [0.5.0] — 2026-09-24

### Added
- `README.md` público (inglés) con el disclaimer Dune obligatorio (spec §12).
- `LICENSE` MIT.
- `examples/hello-logsayer/` — sesión real documentada con salidas del CLI.
- Empaquetado listo para PyPI: `readme`, `authors`, `keywords`, clasificadores y URLs en `pyproject.toml`.

## [0.4.0] — 2026-09-24

### Added
- **Suk Doctor** (`logsayer suk doctor` / alias `logsayer check`): verificación mecánica determinística — marcadores de raíz, estructura de capas, estado, índice de bitácora, ubicación de HUs y detección de capas mezcladas. Exit code 1 ante fallas.
- **Fremen** (`logsayer fremen verify` / alias `logsayer process check`): estado documentado, proceso desplegado, acuerdo de coordinación y Definition of Ready.

## [0.3.0] — 2026-09-24

### Added
- **`logsayer agent add <opencode|claude>`**: genera subagentes por rol (mentat, navigator, reverend-mother, truthsayer) como wrappers finos que invocan al CLI (motor único, spec §6).

## [0.2.0] — 2026-09-24

### Added
- **Comandos core** con alias plano (spec §13): `spec new` (template mínimo de HU), `state show`, `log add` con partición automática, `log index`, `audit run` y `audit status`.

### Changed
- Registro de comandos bajo grupo de rol **y** con alias plano en la raíz.

## [0.1.0] — 2026-09-24

### Added
- **`logsayer init <project-name>`** y `--here`: scaffoldea `docs/` con las 7 carpetas de capas, `AGENTS.md`, `project_state.md` e índice de bitácora.
- **`logsayer.toml`** con los umbrales (spec §4): `session_close_context_threshold = 0.70`, `bitacora_max_lines = 400`, `audit_threshold_hus = 3`.
- Valida slug y destino vacío; empaquetado hatchling (`pyproject.toml`).

[Unreleased]: https://github.com/3m1l10j4v13r4qu1n0/logsayer/compare/v0.6.0...HEAD
[0.6.0]: https://github.com/3m1l10j4v13r4qu1n0/logsayer/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/3m1l10j4v13r4qu1n0/logsayer/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/3m1l10j4v13r4qu1n0/logsayer/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/3m1l10j4v13r4qu1n0/logsayer/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/3m1l10j4v13r4qu1n0/logsayer/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/3m1l10j4v13r4qu1n0/logsayer/releases/tag/v0.1.0