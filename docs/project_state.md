---
fase: fase3
---
# Estado del proyecto — logsayer

> Snapshot operativo para el agente al iniciar cada sesión (Capa 2 — Navegante). No es acumulativo: se sobrescribe al cerrar sesión con aprobación previa. Referencia: `logsayer_especificacion_maestra.md` y `docs/`.

## Fase actual del roadmap

Fases 0 a 6, 8 y 9 cerradas. En curso: **fase 3**, que se cierra con un solo
adaptador, Copilot (D26).

Auditoría **2026-10-02** (scaffoldeada ese día, pasada ejecutada el 2026-10-05)
aprobada y contador reseteado a 0. Resultado: 13 HUs `cumple`, 1 `sin cambios`
por herencia (HU-09), 2 `parcial` y ninguna `no cumple`
(`docs/06_audits/audit_2026-10-02.md`). Las dos parciales —HU-05 y HU-08—
comparten una sola causa externa: `examples/hello-logsayer/README.md` promete
una salida real del CLI que dejó de serlo cuando las fases 8 y 9 movieron la
superficie (D-10, con D34 decidiendo el momento de regenerarlo). La síntesis no
encontró contradicciones entre veredictos.

La corrida de hoy confirma dos cosas del mecanismo: `auditoria_completa` pasó a
`OK` con la tabla de 15 veredictos llena **antes** del reset, que es la
precondición que D-02 pedía; y `contador_hus_al_dia` derivó 0 contra el 3
declarado sin avisar, porque declarar de más es el caso benigno (D35). Y
`audit run --reset-counter` sobre el reporte sellado salió con código 1 sin
scaffoldear ningún archivo nuevo: el defecto que D-02 reportaba no se reproduce.

La auditoría dejó además dos deudas nuevas, en
`inbox/feedback_deudas_auditoria.md`: **D-12** (el `truthsayer` de Claude
declara `tools:` sin `Write`/`Edit` y por lo tanto no puede llenar la tabla que
su propio prompt le asigna — la clase de defecto que D24 prohíbe al revés) y
**D-13** (los README de HU-13 y HU-16 citan rutas que no resuelven, lo que
bloquea su herencia en cada corrida).

> El campo `fase` del frontmatter de arriba es el identificador de la fase: es lo
> que `logsayer log add` convierte en el nombre del logbook. Solo se acepta un
> slug corto (letras, dígitos, `-`, `_`, `.`); la frase de la línea de arriba es
> contexto para humanos y no participa de esa decisión.

CI desde el PR #16 (merge `fb7e604`): `.github/workflows/ci.yml` corre la
batería en cada PR a `develop` y en cada push a `develop` sobre 3.11, 3.12 y
3.13 — verificado en verde sobre las tres (run `36743442993`), y
`.github/workflows/publish.yml` publica en PyPI cuando se pushea un tag semver,
previa batería y previa verificación de que el tag declara la versión de
`pyproject.toml` y la de `__version__`. **D-09 está cerrada**: el tag `v0.8.0`
publicó por el job, no a mano (run `36750950132`). El token sigue siendo una
credencial de larga vida y Trusted Publishing (OIDC) tiene fila propia en la
cola, aparte del código.

Pendientes, en orden: el adaptador Copilot de la fase 3 (D26, deuda D-07), que ya
tiene decisiones de diseño tomadas y registradas; la implementación de la fase 7
(`init --preset`), cuyo diseño quedó escrito en la spec §4 y todavía no toca
código (D-08, con D29, D30 y D31); la regeneración de
`examples/hello-logsayer/`, deliberadamente al final porque las dos deudas
anteriores tocan exactamente su superficie (D-10); las dos deudas que dejó esta
auditoría (D-12 y D-13); y Trusted Publishing (OIDC) para borrar
`PYPI_API_TOKEN` (D-11). La cola vive en `inbox/feedback_deudas_auditoria.md`.
La fase 10 (frontmatter extendido) sigue desplazada: solo entra si duele.

## Decisiones activas

- D1 — Motor único + adaptadores finos (spec §6): la lógica vive en `core/`, los generados son wrappers al CLI.
- D2 — Alias plano como puerta de entrada (spec §13): `logsayer audit run` ≡ `logsayer truthsayer audit run`.
- D3 — Template mínimo por HU (spec §10): un README con "qué construir" + "cómo se valida".
- D4 — `init --here` en modo adopt (spec §5): scaffoldea sobre proyecto existente sin sobrescribir.
- D5 — Audit semántico honesto (spec §10): el CLI genera estructura + prompt; el veredicto lo produce la Decidora.
- D6 — `inbox/` es staging, no una capa: vive fuera de `docs/` y no se versiona.
- D7 — Aviso ≠ fallo: `CheckResult.status` es `ok | warn | fail` y solo `fail` corta el flujo.
- D8 — El CLI mueve y nombra; el contenido lo deriva el subagente Mentat.
- D9 — Los checks de Capa 1 (`header_capa1`, `estado_al_dia`) se validaron contra este mismo repo: fallaron el primer día.
- D10 — El CLI propone la capa, no la decide: sin default a `02_technical/`; elige Mentat.
- D11 — La publicación en PyPI es un hecho verificado, no una intención: 0.6.0 en vivo desde el 2026-09-25, 0.7.0 desde el 2026-09-30 y **0.8.0 desde el 2026-10-01**, comprobado en la JSON API y reinstalando el paquete desde PyPI en un venv limpio (0.7.0 expone `inbox` y `doc` y no expone `memory`; 0.8.0 expone `memory index/status/search` y `audit run --hu`, y los dos funcionan sobre un proyecto nuevo). El token de PyPI viaja por variable de entorno; el `3m1l10j4v13r4qu1n0` que los docs llamaban "token" es el usuario de GitHub, no una credencial.
- D12 — El grafo de memoria es capa transversal de navegación, no una sexta capa: indexa las cinco, no compite con ellas.
- D13 — Un campo de frontmatter entra solo si un comando lo consume mecánicamente: el contrato queda en `tags`.
- D14 — El retrieval ordena la lectura, nunca recorta el alcance: la auditoría sigue siendo sobre `04_user_stories/` completo.
- D15 — El nivel es distancia a la especificación, no un grado de importancia: las capas que no compiten por ser la fuente de verdad de una HU (`03_process/`, `05_agile_methodology/`, `06_audits/`, `logbooks/`) son todas nivel 3, y el nivel se deriva de la ruta, nunca se escribe en el documento.
- D16 — El frontmatter es preámbulo, no contenido: el header estándar se valida igual, después del bloque. Un `---` sin pareja no rompe la indexación (el documento entra sin tags) pero el Suk sí lo señala como header faltante: perdonar metadata nunca vale esconderla.
- D17 — La fase se declara en el campo `fase` del frontmatter del estado y se valida como identificador, en vez de slugificarse de la prosa. El valor se convierte en nombre de archivo, así que una frase es una declaración inválida; sin fase declarada, `log add` avisa en vez de particionar en silencio.
- D18 — El retriever lee el artefacto, no los documentos: si regenerara, `indice_al_dia` no tendría nada que verificar. El precio (un documento nuevo no es encontrable hasta que se reindexa) lo paga el check.
- D19 — `indice_al_dia` mira solo Capa 1: `log add` y el cierre de sesión tocarían el índice en casi todos los cierres, y un aviso permanente no avisa.
- D20 — El alcance de la auditoría es una tabla que cuenta el CLI: una fila por directorio `HU-*`, escrita por el CLI y releída por `parse_verdicts()`. El hueco se ve en el `git diff` del reporte.
- D21 — `docs/project_state.md` no invalida la herencia de una HU: se reescribe en cada cierre de sesión, y contarlo invalidaría para siempre el veredicto de toda HU que lo menciona.
- D22 — `--hu` repite una pasada y no escribe reporte: el alcance vive en la tabla, y un reporte con una sola fila sería el último y dejaría el resto sin cubrir.
- D23 — La síntesis lee solo la tabla de veredictos, y solo si algún veredicto cambió: abrir HUs para sintetizar sería una segunda pasada entera.
- D24 — La superficie de permisos se declara con la unidad que la herramienta soporta: opencode tiene bloque `permissions:` por acción/recurso/efecto, Claude Code solo el allowlist `tools` (granularidad por herramienta). No se escribe un campo que la herramienta pueda ignorar en silencio, y `settings.json` no se genera porque es de sesión.
- D25 — Un aviso que solo vive en el documento generado no avisa a quien lo pidió: `doc new` muestra el aviso de conversión por stdout, además de dejarlo en el bloque `## Fuente`.
- D26 — La fase 3 se cierra con un solo adaptador, Copilot: es el de mayor uso y su convención (`AGENTS.md` más instrucciones por path con `applyTo`) es la más expresiva. No se implementan los cuatro que el registro enumera a la vez: `hermes` no tiene ni un referente verificable, y cuatro adaptadores a medio hacer son cuatro superficies de permisos que la herramienta puede ignorar en silencio (D24).
- D27 — El release de 0.8.0 mueve `main`: PR `develop` → `main` y el tag semver sobre ese merge. `main` quedó en 0.6.0 solo porque era ancestro estricto de `develop` y no había forma de que contuviera únicamente la fase 6; con las fases 8 y 9 ya integradas, el tag y el contenido de `main` vuelven a decir lo mismo y el desfase termina acá.
- D28 — La publicación es manual hasta que exista CI: el repo no tiene `.github/workflows/`, así que `v0.7.0` salió de una shell con `UV_PUBLISH_TOKEN` y no hay ruta automatizada. La deuda entra como fila propia de la cola y no solo en la bitácora, porque la bitácora no es la cola de trabajo entre sesiones y `bandeja_entrada` mide antigüedad, no existencia: sin fila, ningún check la va a avisar.
- D29 — El idioma del contenido no es eje del preset: detrás de una clave `lang` hay i18n de los 17 templates —con los 8 de adaptadores, que además difieren entre opencode y Claude Code— y no hay ninguna bandera de idioma en el CLI. Queda fuera de la v1 y el idioma es decisión de proyecto, que es lo que el propio `AGENTS.md` generado ya dice: superficie pública en inglés, contenido generado en el idioma del proyecto. Si entra alguna vez, entra como fase propia.
- D30 — `init` declara y `agent add` ejecuta: el preset escribe `[adapters] enabled` y el único comando que genera archivos de adaptador sigue siendo `agent add`. La razón es dura y no es de gusto: `generate_adapters()` pisa lo que encuentra sin preguntar, así que si `init` generara adaptadores, `init --here` rompería su propia promesa de no sobrescribir (D4) y podría pisar subagentes editados por el usuario. La distancia entre declarar y ejecutar la reconcilia el check `adaptadores_declarados`, que avisa y no corrige.
- D31 — Los umbrales se quedan en `[logsayer]` y no se mueven: cambiar la tabla a `[thresholds]` haría que todo proyecto ya scaffoldeado dejara de encontrar sus umbrales y volviera a los defaults **en silencio**, porque `LogsayerConfig.load()` no distingue "falta la tabla" de "no hay configuración". `[project]` y `[adapters]` son bloques nuevos que conviven con el viejo, así que el cambio no rompe nada y no obliga a migrar archivos versionados de los usuarios.
- D32 — La CI corre sobre la matriz que declara el paquete: 3.11, 3.12 y 3.13 son las que dicen `requires-python` y los classifiers, así que la batería corre en todas ellas o la CI estaría declarando menos que el paquete. Y `ruff format --check` queda **fuera** de la puerta: hoy quiere reformatear 34 archivos, y un gate que arranca rojo es deuda nueva.
- D33 — El tag no publica hasta que tag, `pyproject.toml` y `__version__` dicen lo mismo: D11 ("la publicación es un hecho verificado, no una intención") vuelto mecanismo, y convierte el fallo de "un paquete publicado que miente" en "un corte con mensaje". El token sigue siendo una credencial de larga vida en el repo — Trusted Publishing (OIDC) es el cierre pendiente y tiene fila propia, aparte del release.
- D34 — `examples/hello-logsayer/README.md` se regenera al final del ciclo, no ahora: promete ser salida real del CLI, así que cualquier cambio en la superficie lo vuelve falso, y las cuatro deudas que quedan (D-01, D-02, D-07, D-08) caen exactamente sobre sus líneas. Editarlo hoy a mano sería hacer trabajo que se tira.
- D35 — El contador de HUs del estado se verifica contra el disco, pero el umbral no se mueve: el check `contador_hus_al_dia` (HU-15) deriva el contador —directorios `HU-*` sin veredicto en el reporte que selló— y avisa en `warn` solo cuando lo declarado subestima, que es el único sentido que retrasa la auditoría. Declarar de más es el caso benigno y no avisa (decidir 3); sin auditoría sellada no se mide, en vez de asumir que todo está pendiente, porque un aviso permanente no avisa (como D19 con `indice_al_dia`). Y `logsayer audit status` muestra el derivado pero el veredicto de umbral sigue siendo el del declarado: el derivado informa, no mueve el gate, porque cambiar cuándo se propone auditar en un comando publicado es una decisión de umbral, no una corrección de número. El check se validó contra este mismo repo y **avisó el primer día** (declaraba 1, derivadas 2), que es la prueba de que no es decorativo (D9).

## HUs cerradas desde la última auditoría

0

Auditoría del **2026-10-02** aprobada y contador reseteado a 0 (venían 3 HUs
desde el 2026-09-29: HU-14, HU-15 y HU-16; el número que dispara la auditoría lo
confirma hoy `contador_hus_al_dia`, que antes ningún check verificaba — D35).
Umbral 3: a la tercera HU cerrada la Decidora vuelve a correr, y ahora el
alcance lo verifica `auditoria_completa` y el contador lo deriva el disco.

Desde el reset no cierra ninguna HU todavía: la siguiente es **HU-17, el
adaptador de Copilot** (D-07), que va ya con sus decisiones de diseño tomadas.
El reporte del 2026-10-02 selló 16 HUs y su tabla está completa, así que
`auditoria_completa` avisará por HU-17 hasta la próxima corrida: es D20
funcionando, no un hueco.
