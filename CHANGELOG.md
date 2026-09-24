# Changelog

Todos los cambios notables de logsayer quedan documentados acá, por versión, en orden cronológico inverso. Formato [Keep a Changelog](https://keepachangelog.com/es/1.1.0/), versionado [semver](https://semver.org/lang/es/).

## [Unreleased]

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