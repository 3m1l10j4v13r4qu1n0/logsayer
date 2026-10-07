# Changelog

Todos los cambios notables de logsayer quedan documentados acá, por versión, en orden cronológico inverso. Formato [Keep a Changelog](https://keepachangelog.com/es/1.1.0/), versionado [semver](https://semver.org/lang/es/).

## [0.9.0] — 2026-10-07

Fases 3 y 7 del roadmap + las deudas de las auditorías del 2026-09-29 y 2026-10-02 que quedaban. La fase 3 cerró con el adaptador de **Copilot** (D26: uno solo, el de mayor uso y cuyo convención —perfil más instrucción por path— es la más expresiva) y la fase 7 con **`init --preset`**, el snapshot de convenciones que entra una sola vez en el TOML del proyecto. Este release también es la puerta de la evidencia de D-11: la primera versión que publica el job con **Trusted Publishing (OIDC)**, sin credencial de larga vida en el repo.

### Added
- **`logsayer init --preset <nombre>`** (HU-18, D-08): fase 7. Un preset es un bundle de convenciones con dos ejes —qué adaptadores deja declarados y qué umbrales pone— y se materializa **una sola vez** en el `logsayer.toml` del proyecto. El preset es un **snapshot, no una herencia viva**: `init` copia los valores y el preset deja de existir para ese proyecto, así que no hay que resolver "qué pasa si el preset cambia en la próxima versión" y el TOML se edita sin sorpresas. Se distributionan dos, como TOML dentro del paquete y no como código: `default` (no sobreescribe nada) y `minimal` (un adaptador, umbrales más laxos). `strict` quedó fuera a propósito — un preset sin caso real es superficie para mantener.
- **`[project] preset` y `[adapters] enabled` en el `logsayer.toml`**: dos bloques nuevos que conviven con `[logsayer]`, cuya forma **no se mueve**: renombrar la tabla haría que todo proyecto ya scaffoldeado volviera a los defaults **en silencio** (D31). `init` declara los adaptadores y `agent add` los escribe — la frontera es dura, porque `generate_adapters()` pisa lo que encuentra sin preguntar y `init --here` no puede romper su promesa de no sobrescribir (D30). En modo adopt, si el `logsayer.toml` ya existe, `--preset` no se aplica y `init` avisa: el TOML del proyecto manda (D4).
- **Checks `preset_conocido` y `adaptadores_declarados`** (Suk): los dos hacen legales las dos claves nuevas, porque un valor entra solo si un comando lo consume mecánicamente (D13). El primero avisa cuando el preset declarado ya no existe en el paquete instalado —el fallo real de un snapshot— y nombra la versión. El segundo avisa cuando un nombre de `enabled` no tiene adaptador, o tiene uno pero sus archivos no están en el proyecto: se mide contra el conjunto entero y no archivo por archivo (D41), porque quien escribió uno a mano ya ejecutó la parte y un archivo borrado a conciencia no es un pendiente. Ninguno corrige.
- **Check `contador_hus_al_dia`** (HU-15, D-01): el contador de HUs cerradas del snapshot deja de ser una afirmación y se mide contra el disco — el derivado cuenta los directorios `HU-*` sin veredicto en el reporte que selló. Avisa en `warn` cuando lo declarado **subestima** lo que hay en disco, que es el único sentido que retrasa la auditoría (el caso benigno, declarar de más, no avisa). Sin auditoría sellada no se mide, en vez de asumir que todas las HUs están pendientes. Es la deuda transversal de la auditoría del 2026-09-29: el estado declaraba 2 HUs con 4 en disco y ningún check lo veía.
- **Comando `logsayer audit reset`** (HU-16, D-02): reinicia el contador de HUs. Rechaza con error nombrando las HUs pendientes si `pending_verdicts()` no está vacío; no crea ni modifica reportes de auditoría.
- **Adaptador de GitHub Copilot** (HU-17, D-07): fase 3, capa de coordinación. Motor único y adaptador delgado como en opencode y Claude Code, pero con la convención nativa de Copilot: **dos archivos por rol** — perfil en `.github/agents/<rol>.agent.md` e instrucción en `.github/instructions/logsayer/<rol>.instructions.md` (D36) — porque con un archivo solo los cuatro prompts llegarían a todos los contextos del repo. `applyTo` es filtro de contexto, no permiso: la escritura única por capa queda en la prosa de cada template y no en un campo (D38), los ocho archivos llevan `excludeAgent: "code-review"` (D39) y la Decidora declara `edit` mientras la Reverenda Madre no (D40). No se genera `.github/copilot-instructions.md`: Copilot consume `AGENTS.md` nativamente y un segundo archivo sería una segunda fuente de verdad para lo mismo (D37).

### Changed
- **`logsayer audit status` muestra el derivado** del disco junto al contador declarado, y avisa cuando el declarado queda por debajo. El veredicto de umbral sigue siendo el del contador declarado — el derivado informa, no mueve el gate.
- **Shim deprecado**: `logsayer audit run --reset-counter` ahora sale con código 1 y mensaje que apunta a `logsayer audit reset`, sin ejecutar auditoría ni reiniciar el contador.
- **`LogsayerConfig.from_mapping()`**: la validación de `[logsayer]` sale de `load()` para que un preset se valide contra el **mismo** contrato que lee el TOML del proyecto. Sin eso el preset tendría un segundo validador, y un preset roto podría llegar al scaffold. `LogsayerConfig.load()` no cambia de comportamiento.
- **La publicación pasa a Trusted Publishing** (D-11): el job pide `id-token: write` en el job `publicar` y `uv publish --trusted-publishing always` acuña el OIDC de GitHub y lo cambia por un token de corta vida contra PyPI. El `env: UV_PUBLISH_TOKEN` y el secreto `PYPI_API_TOKEN` desaparecen del workflow y del repo (D33 sigue igual: el tag, `pyproject.toml` y `__version__` tienen que decir lo mismo, y el publisher del lado de PyPI es el que autoriza el repo + workflow + environment).
- **Los candidatos de `doc route` no repiten el prefijo de capa** y el README queda coherente consigo mismo (feedback de 2026-10-05): roadmap reordenado 0–9 sin `hermes`, disclaimer Dune al final, quick start con un solo `check` y paso `--preset`, fila `audit run --hu`, paso concreto para actualizar umbrales de un proyecto viejo y nota de idioma (D29). El juicio del CLI presenta la lista sin capa; la tabla completa de `routing.py` la conserva porque ahí distingue de Capa 3 y 4.
- **`examples/hello-logsayer/` regenerado contra el CLI real** (D-10): el transcript —que era la causa del `parcial` de HU-05 y HU-08 en la auditoría del 2026-10-02— deja de ser una copia vieja de 0.6.0 y es la salida real, sesión corrida de nuevo con los 13 checks de Suk, los 5 de Fremen, el frontmatter `fase:`, el bloque `tags:` de `doc new`, Copilot con 8 archivos y las fases 8 y 9 enteras.

### Fixed
- **El `truthsayer` de Claude Code escribe la tabla de veredictos** (D-12): declaraba `tools: Read, Grep, Glob, Bash` sin `Write` ni `Edit` mientras su prompt le pedía llenar `docs/06_audits/` — el defecto que D24 prohíbe al revés. `tools:` pasó a incluir `Write, Edit` en el template, que es toda la superficie declarativa que esa herramienta tiene.
- **Citas muertas en HU-13, HU-16 y HU-18** (D-13): rutas que no resolvían y que bloqueaban la herencia en cada corrida (una cita muerta bloquea la herencia por la decisión 5 de HU-12). Corregidas las tres; 0 citas muertas en las 16 HUs.

## [0.8.0] — 2026-09-30

Fases 8 y 9 del roadmap: **memoria seleccionable** y **auditoría por pasada**. Las dos atacan el mismo defecto desde lados opuestos — el agente no sabía qué documento abrir primero, y la Decidora no sabía a qué HUs debía mirar. Ninguna de las dos se resolvió con prosa: la fase 8 produce un artefacto (`docs/00_memory_index.md`) y la fase 9 produce una tabla de alcance que el CLI escribe y relee, así que un hueco en cualquiera de las dos se ve en un `git diff`. La fase 8 entró a `develop` el 2026-09-28 (HU-10, HU-11) y la fase 9 el 2026-09-29 (HU-12, HU-13).

### Added
- **`docs/00_memory_index.md` y `logsayer memory index`**: un artefacto generado con una línea por documento de `docs/`, ordenado por (nivel, ruta), con fecha y estado del header estándar y las tags. El nivel se deriva de la ruta, nunca se escribe. Es navegación transversal, **no una sexta capa** (D12), y las capas que no compiten por ser la fuente de verdad de una HU van todas en el mismo nivel (D15).
- **Contrato de frontmatter reducido a `tags`**: es el único campo que entra, porque es el único que un comando consume mecánicamente (D13). Sin frontmatter, las tags se derivan del nombre, de la carpeta `HU-XX/` y de la HU citada en `## Fuente`, así que un documento queda clasificable sin escribir una línea de metadata. `doc new` scaffoldea el bloque desde el nombre; lo ajusta Mentat (D8).
- **`logsayer memory search "<consulta>"`** (HU-11): retrieval determinista — tokeniza la consulta, la intersecta con las tags del índice, ordena y corta, con `--capa` para acotar a una capa y `--limit` para el tope (`0` = todos). El acierto exacto pesa más que el prefijo compartido, y a igualdad de puntaje mandan el nivel más cercano a la especificación y la ruta: el mismo orden con el que se lee el índice, para que los dos artefactos se lean como las mismas capas. Sin LLM y sin embeddings.
- **`logsayer memory status`**: informa qué indexa y con cuántas tags.
- **Check `indice_al_dia`** (Fremen): avisa en `warn` cuando un documento de Capa 1 cambió después del índice. Reusa el patrón de `estado_al_dia` con la lógica extraída a `core/freshness.py`, para que los dos checks midan lo mismo. El alcance es Capa 1 y no todo `docs/`, porque `log add` y el cierre de sesión tocarían el índice en casi todos los cierres y un aviso permanente no avisa (D19).
- **El alcance de la auditoría pasa a ser una tabla que cuenta el CLI** (HU-12): `audit run` scaffoldea una fila por directorio `HU-*` del disco y `parse_verdicts()` es el inverso exacto de `HuItem.row()`, así que la cobertura se verifica parseando y no re-interpretando (D20). Un `HU-XX/` sin README entra en el alcance con su hueco adentro, y una ruta citada que no resuelve se distingue entre muerta y ambigua — `mentat.md.j2` existe en `adapters/opencode/` y en `adapters/claude/`, y elegir el primer hit manda a la Decidora al archivo equivocado con toda confianza.
- **Check `auditoria_completa`**: compara el alcance del disco contra las filas con veredicto del último reporte y avisa en `warn` nombrando las HUs pendientes. Es `warn` y no `fail` (D7): un reporte a medio llenar es un estado legítimo mientras la Decidora trabaja, y bloquearlo haría odiar el check. El corte real es del humano.
- **`logsayer audit run --hu HU-XX`** (HU-13): reemite el brief de una pasada aislada y **no escribe reporte** (D22). Que no escriba no es comodidad: el alcance vive en la tabla, y un reporte con una sola fila pasaría a ser el último y dejaría al resto sin cubrir — justo el modo de falla silencioso que la fase 9 cierra.
- **Síntesis condicional de la auditoría**: lee solo la tabla de veredictos y solo si alguno cambió (D23). Las filas heredadas salen con "sin cambios" y el prompt dice que no se re-auditen, para que la Decidora no gaste contexto re-litigando lo ya fallado.
- **Brief por HU** (`HuItem.brief()`): acota la pasada al input de esa HU — el README, la base fija (mission + project_state) y las rutas que cita, con las muertas y las ambiguas a la vista. La base fija va siempre y las citas son mejora: sin ella, una HU sin citas arrancaría ciega.
- **CI** (D28, D33): `.github/workflows/ci.yml` corre la batería en cada PR a `develop` y en cada push a `develop` sobre 3.11, 3.12 y 3.13 — las tres que declara `requires-python` (D32). `.github/workflows/publish.yml` publica en PyPI cuando se pushea un tag semver, previa batería y previa verificación de que el tag declara la versión de `pyproject.toml` **y** la de `__version__`. Desde este release, la publicación la hace el job y no una shell.

### Changed
- **El prompt de auditoría separa los tres niveles de verificación** y quién resuelve cada uno: checks estructurales, batería de código una sola vez, y veredicto semántico. Sin esa separación, la Decidora deriva por HU una batería que es mecánica.
- **`last_audit()` y `sealed_audit()` son consultas distintas**: la primera devuelve el reporte más reciente (el que se mide) y la segunda el más reciente con veredictos (el que sella la herencia). Confundirlas rompe la herencia de una HU de forma difícil de ver: `audit run` scaffoldea un reporte vacío, ese andamiaje pasa a ser "el previo" y una sola corrida borra todo lo que el trabajo anterior había ganado.
- **`docs/project_state.md` no invalida la herencia de una HU** (D21): se reescribe en cada cierre de sesión, y contarlo invalidaría para siempre el veredicto de toda HU que lo menciona.
- **El retriever lee el artefacto, no los documentos** (D18): si regenerara o leyera los archivos, `indice_al_dia` no tendría nada que verificar y el índice sería decorativo. El precio —un documento nuevo no es encontrable hasta que se reindexa— lo paga el check.
- **`core/layers.py` centraliza la taxonomía de capas** que el Suk, el índice y `--capa` compartían por copia: agregar una capa en un lugar y olvidarla en el otro es como apareció la sexta capa que la fase 8 descartó.
- **`capas_mezcladas` exime el índice**: sin la excepción, el check leería su propia navegación transversal como una sexta capa.
- **`header_capa1` busca el header en el cuerpo, después del frontmatter** (D16): exigir que el título sea la primera línea haría fallar a todo documento que genera la propia CLI. El header se sigue exigiendo igual, y un `---` sin pareja se indexa sin tags pero el Suk lo señala como header faltante — perdonar metadata nunca vale esconderla.
- **El token de PyPI viaja por variable de entorno** (`UV_PUBLISH_TOKEN` con el secreto `PYPI_API_TOKEN` del repo). Trusted Publishing (OIDC) queda pendiente y **fuera** de este release: no se mezcla con el corte.

### Fixed
- **`audit run --hu` ya no apunta a `docs/06_audits/None`**: `run_audit()` pasa `report_name` en esa rama.

### Diseño documentado, todavía sin código
- **Fase 7 (`init --preset <nombre>`)**: diseño escrito en la spec §4 y §5, sin implementación. El preset es un **snapshot, no una herencia viva** — `init` copia los valores a `logsayer.toml` y el preset deja de existir para ese proyecto. `init` declara los adaptadores en `[adapters] enabled` y los escribe `agent add` (D30: `generate_adapters()` pisa sin preguntar, así que `init` pisaría lo que ya está). Los umbrales se quedan en `[logsayer]` y no se mueven (D31: cambiar la tabla haría que todo proyecto ya scaffoldeado volviera a los defaults **en silencio**). El idioma del contenido no es eje del preset (D29).
- **Fase 3**: la decisión de fondo quedó tomada (D26) — un solo adaptador, Copilot — y la implementación sigue pendiente.

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

[0.9.0]: https://github.com/3m1l10j4v13r4qu1n0/logsayer/compare/v0.8.0...v0.9.0
[0.8.0]: https://github.com/3m1l10j4v13r4qu1n0/logsayer/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/3m1l10j4v13r4qu1n0/logsayer/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/3m1l10j4v13r4qu1n0/logsayer/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/3m1l10j4v13r4qu1n0/logsayer/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/3m1l10j4v13r4qu1n0/logsayer/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/3m1l10j4v13r4qu1n0/logsayer/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/3m1l10j4v13r4qu1n0/logsayer/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/3m1l10j4v13r4qu1n0/logsayer/releases/tag/v0.1.0