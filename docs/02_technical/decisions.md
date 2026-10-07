# Decisiones técnicas — logsayer

Fecha: 2026-10-02 · Estado: vigente

## Resumen

Registro vivo de las decisiones de arquitectura activas. Cada una tiene su porqué en la
bitácora; acá queda solo la referencia y su estado.

## D1. Un motor único + adaptadores finos (spec §6)

Toda la lógica vive en `logsayer/core/` y `cli.py`. Los archivos generados por `agent add` son wrappers finos que llaman al CLI — agregar un agente nuevo no duplica lógica. *Referencia: bitácora fase 3.*

## D2. Alias plano como puerta de entrada (spec §13)

`logsayer audit run` ≡ `logsayer truthsayer audit run`. El lore Dune da identidad pero nunca debe ser la única puerta de entrada a la funcionalidad.

## D3. Template mínimo por HU (spec §10)

Un solo `README.md` por HU con "Qué hay que construir" + "Cómo se valida". Nada de documentos de cientos de líneas por defecto (anti "sea of markdown").

## D4. `init --here` en modo adopt (spec §5)

`logsayer init --here` scaffoldea sobre un proyecto existente: crea lo que falta y **no sobrescribe** archivos ya presentes (AGENTS.md, logsayer.toml, estado, índice). Cerrado en el dogfooding del propio repo (fase del marco de sesiones).

## D5. Audit semántico honesto (spec §10)

El CLI genera estructura + prompt; el resultado lo produce un subagente. No se promete determinismo: se documenta. La responsabilidad es generar la estructura del reporte y el prompt, no el veredicto.

## D6. `inbox/` es staging, no una capa (spec §3)

La bandeja vive fuera de `docs/` y a propósito: no es Capa 1 ni ninguna otra. Razones: (a) sus archivos son *fuentes* sin jerarquía editorial, no documentos del proyecto; (b) el contenido se ignora en Git para no versionar material de terceros; (c) mezclarla con `docs/` haría que un `.pdf` sin procesar contamine el árbol documental. El derivado sí es Capa 1 y es lo único que se versiona. `logsayer check` escanea `docs/` únicamente.

## D7. Aviso ≠ fallo: el nivel `warn` (spec §4)

`CheckResult.status` pasó a ser `ok | warn | fail`. Un documento sin ubicar o un estado desactualizado no son errores de estructura: son pendientes que el humano debe ver pero que no deben cortar el flujo (`logsayer check` sale con 0). Solo `fail` bloquea. El motivo es operativo: si el pendiente bloqueara, la gente startaría a odiar el check y perderíamos la señal.

## D8. El CLI mueve y nombra; el agente deriva (spec §6)

El motor no redacta contenido ni convierte formatos. `doc new` scaffoldea el documento con su bloque `## Fuente` y archiva el original en `inbox/_done/`; el subagente Mentat es quien decide la capa y escribe el cuerpo. La responsabilidad del CLI es mecánica y verificable; la del agente requiere juicio.

## D9. Checks de Capa 1 como detectores de deuda (spec §4)

`header_capa1` y `estado_al_dia` se implementaron contra este mismo repo como prueba: fallaron el primer día contra documentos reales. Un check que nunca falla en el proyecto que lo dogfoodea es decorativo.

## D10. El CLI propone la capa, el subagente la decide (spec §3)

`doc route <archivo>` devuelve filas candidatas y decide solo con señal inequívoca: extensión no markdown, o una HU declarada en el nombre. La primera implementación clasificaba por palabras del nombre y, ante lo desconocido, devolvía `docs/02_technical/` por defecto. Se descartó: un `.md` de visión de producto terminado en la carpeta técnica sin que nadie lo notara es exactamente el tipo de error que el marco de 5 capas existe para evitar (spec §2). Además ahora detecta el reenvío de un documento que ya existe y avisa que no se duplique. *Discusión cerrada con el humano el 2026-09-25.*

## D11. La publicación en PyPI es un hecho verificado, no una intención

La publicación en PyPI es un hecho verificado, no una intención: 0.6.0 en vivo desde el 2026-09-25, 0.7.0 desde el 2026-09-30 y **0.8.0 desde el 2026-10-01**, comprobado en la JSON API y reinstalando el paquete desde PyPI en un venv limpio (0.7.0 expone `inbox` y `doc` y no expone `memory`; 0.8.0 expone `memory index/status/search` y `audit run --hu`, y los dos funcionan sobre un proyecto nuevo). El token de PyPI viaja por variable de entorno; el `3m1l10j4v13r4qu1n0` que los docs llamaban "token" es el usuario de GitHub, no una credencial.

*Referencia: bitácora fase 7/8/9 y snapshot del 2026-10-02.*

## D12. El grafo es capa transversal, no una sexta capa

La memoria seleccionable (fase 8) no agrega una capa: agrega un índice que navega las que ya existen. El diseño viene de un feedback externo que proponía indexar las capas con un grafo de `nivel`/`peso`/`relaciones` y 13 fases de roadmap. Se conserva la idea de la separación entre memoria estructural (dónde buscar) y memoria documental (qué dice), y se descarta la sextificación. Motivo: una sexta capa sería un segundo sistema de documentación compitiendo con las otras cinco, y `capas_mezcladas` —la regla de oro de la spec §2— existe justamente para que cada documento tenga un dueño. El grafo entonces es un artefacto derivado, generado por el CLI, que no se edita a mano. *Referencia: `docs/02_technical/memory_architecture.md`.*

## D13. Un campo de frontmatter entra solo si un comando lo consume mecánicamente

El frontmatter se limita a `tags`, que consume `memory search`. Descartados: `id`, `capa`, `nivel` y `estado`, porque la ruta y el header estándar ya los dicen y duplicarlos crea dos verdades que divergen el primer día que no coincidan; y `peso` y `relaciones`, porque los escribiría un LLM o un humano a mano y se pudren. El criterio general es el de D9 aplicado al metadato: *lo que nadie lee mecánicamente es decoración*. Consecuencia asumida: el índice se construye con lo determinable (ruta, `## Fuente`, `git log -1`) y las tags iniciales se derivan del nombre del archivo, sin exigir trabajo humano. *Referencia: `docs/02_technical/memory_architecture.md`.*

## D14. El retrieval elige qué leer primero, nunca qué es auditable

La Decidora usa `memory search` para ordenar su arranque, pero el alcance de una auditoría sigue siendo `docs/04_user_stories/` completo. Motivo: si el subgrafo deja afuera un documento relevante, la auditoría pasa por omisión y el marco miente — un fallo silencioso peor que un check en rojo. El índice es un atajo de lectura, no un recorte de alcance. Es la traducción del D5 (el veredicto es del agente, no del CLI) al terreno de la recuperación: el motor acota el **contexto**, nunca el **alcance**. *Referencia: `docs/02_technical/memory_architecture.md`.*

## D15. El nivel es distancia a la especificación, no un grado de importancia

`01_global/` y `docs/project_state.md` son nivel 0, `02_technical/` nivel 1, `HU-XX/` nivel 2, y `03_process/`, `05_agile_methodology/`, `06_audits/` y `logbooks/` son **todas nivel 3**. La numeración mide qué tan lejos está un documento de la especificación de lo que hay que construir, y esas cuatro capas no compiten por ser la fuente de verdad de una HU: compiten por ser el registro de por lo que se construyó: la forma que tomó el trabajo y la evidencia de que pasó. El nivel se deriva de la ruta y nunca se escribe en el documento, por D13 —un campo que nadie lee mecánicamente se pudre, y este además no podría dejar de desincronizarse de la ruta que lo origina. *Referencia: `docs/02_technical/memory_architecture.md`, HU-10.*

## D16. El frontmatter es preámbulo, no contenido

El bloque `---` inicial es metadata: el header estándar se valida igual, en el cuerpo, después del bloque. Por eso `header_capa1` busca el título en el cuerpo y no en la primera línea — si no, todo documento scaffoldeado por la propia CLI passaría a fallar, que es un check que se vuelve decorativo por construcción. Un `---` sin pareja no rompe la indexación (el documento entra sin tags) pero el Suk sí lo señala como header faltante: perdonar metadata faltante nunca vale esconderlo. *Referencia: HU-10.*

## D17. La fase se declara; no se deduce de la prosa

La fase de la bitácora es el campo `fase` del frontmatter de `docs/project_state.md`, y se valida como identificador (letras, dígitos, `-`, `_`, `.`) en vez de normalizarse. Antes `current_phase()` slugificaba la primera línea de la sección "Fase actual del roadmap", que es texto libre para humanos: "Fase 6 — ingreso de documentos, cerrada y mergeada…" terminó siendo el nombre permanente de un logbook que hubo que borrar a mano. El motivo es que **el valor se convierte en un nombre de archivo**: una frase no es un slug que se limpia, es una declaración inválida. Y si no hay fase declarada, `log add` lo dice en su salida en vez de particionar en silencio: la fase ausente es un pendiente visible, no un default. Es D13 aplicado al estado — un campo entra solo si un comando lo consume mecánicamente, y el que lo consume es la Reverenda Madre. *Referencia: `fix/phase-fase-explicita`, incidente del 2026-09-28 en `logbook_fase8_01.md`.*

## D18. El retriever lee el artefacto, no los documentos

`memory search` parsea `docs/00_memory_index.md` en vez de volver al disco. La razón es garantizar que `indice_al_dia` tenga algo que verificar: un retrieval que regenera antes de responder, o que lee los archivos directo, nunca puede estar viejo, y entonces el check es decorativo y el índice es un artefacto que nadie necesita mirar. El precio —un documento nuevo no es encontrable hasta que se reindexa— es explícito y lo paga el check, que avisa en `warn` nombrando el documento más nuevo. El ranking son las tags del contrato, y la ruta no puntúa: matchear `readme` o `technical` devolvería casi todo y dejaría de filtrar. *Referencia: HU-11.*

## D19. El aviso de frescura del índice mira Capa 1

`indice_al_dia` compara el índice contra los documentos de `01_global/`, `02_technical/` y `04_user_stories/`, no contra todo `docs/`. Con el alcance completo, `log add` —que anexa al logbook— y el cierre de sesión —que reescribe `project_state.md`— pondrían el índice viejo en casi todos los cierres, y un aviso que aparece siempre deja de avisar (D7). Las capas que no compiten por ser fuente de verdad de una HU (D15) no cambian lo que el agente tiene que leer primero. *Referencia: HU-11.*

## D20. El alcance de la auditoría es una tabla que cuenta el CLI

`logsayer audit run` scaffoldea una fila por directorio `docs/04_user_stories/HU-*/`, y la Decidora llena celdas en vez de decidir qué filas existen. `parse_verdicts()` es el inverso exacto de `HuItem.row()`: el CLI escribe la tabla y la relee igual, así que la cobertura se verifica parseando y no interpretando. El motivo es que un alcance escrito en prosa no se puede verificar sin volver a interpretarlo con el mismo criterio que produjo el hueco: es imposible distinguir "esa HU no estaba" de "se me olvidó esa HU". Un alcance mecánico tiene además una propiedad que la prosa no tiene — el hueco se ve en el `git diff` del reporte, revisable por un humano sin correr nada. D14 ("el retrieval elige por dónde empezar, nunca qué es auditable") pasa así de una promesa en el prompt a un artefacto. De ahí salen las dos consecuencias menos obvias: `last_audit()` (el reporte que se mide) y `sealed_audit()` (el que sella la herencia) son consultas distintas, porque `audit run` scaffoldea un reporte vacío y si ese andamiaje fuera "el previo" una sola corrida borraría toda la herencia anterior; y un reporte sin worklist —los anteriores a la fase 9, que listan las HUs en prosa— ni sella ni se mide, con lo cual el primer `audit run` de un proyecto con historia re-audita todas sus HUs. *Referencia: HU-12, `docs/02_technical/audit_protocol.md`.*

## D21. `project_state.md` no invalida la herencia de una HU

La herencia de "sin cambios" compara el README de la HU y las rutas que cita contra el reporte que selló, pero excluye `docs/project_state.md`. El snapshot se reescribe en cada cierre de sesión: contarlo invalidaría para siempre el veredicto de toda HU que lo menciona, y una herencia que nunca llega a concederse es una herencia que no existe. Es el mismo error que D19 corrige para `indice_al_dia` —el ritual de coordinación no es requisito— y la misma regla de D7 detrás: un aviso que aparece siempre deja de avisar. Lo que sí invalida es tocar el README de la HU o algo que la HU cita, y una cita que ya no existe en disco. *Referencia: HU-12.*

## D22. `--hu` repite una pasada y no escribe reporte

`logsayer audit run --hu HU-XX` emite solo el brief de una HU. Que no escriba reporte no es una comodidad de la interfaz: el alcance vive en la tabla, y un reporte con una sola fila pasaría a ser el último y dejaría al resto del alcance sin cubrir, que es exactamente el modo de falla silencioso que D20 existe para cerrar. Un brief es un artefacto desechable, no un estado, y por eso lleva `.prompt.md` —extensión que `last_audit()` excluye. *Referencia: HU-13.*

## D23. La síntesis lee la tabla de veredictos, y solo si algo cambió

La sección "Sintesis entre HUs" se escribe al final, únicamente si algún veredicto cambió en la corrida, y su input es **la tabla de veredictos y nada más**. Si la síntesis pudiera abrir HUs para cruzar, sería una segunda pasada entera y el aislamiento de contexto se perdería; y si se disparara siempre, con veredictos heredados, revisaría auditoría sobre auditoría. Ante una contradicción sospechada que ninguna pasada registró, la instrucción es nombrarla nombrando las HUs involucradas y pedir una repasada acotada —no resolverla ahí. El límite es honesto y declarado: la síntesis detecta contradicciones evidentes entre veredictos; una contradicción que ninguna pasada individual registró, no la va a ver. *Referencia: HU-13.*

## D24. La superficie de permisos se declara con la unidad que la herramienta soporta, y la excepción se escribe

Un adaptador declara la restricción de single-writer con la unidad más fina que su herramienta acepta, y cuando esa unidad es más gruesa que la pretendida, la excepción queda escrita en el template y en la spec §6 en vez de completarse con un campo que la herramienta pueda ignorar. El caso es Claude Code: el frontmatter de subagente solo expone `tools` como allowlist de **nombres de herramienta**, y las reglas por recurso (`Bash(<comando>)`, `Edit(<ruta>)`) viven en `settings.json`, que son de sesión —alcanzarían a la sesión principal y a los otros roles por igual—, así que el CLI no las genera. El motivo de no escribirlo igual es que un campo de permiso ignorado en silencio se lee como una garantía y opera como una ausencia: hay un issue abierto de Anthropics (`#27099`) donde exactamente eso pasó con el nombre de campo equivocado, y la documentación oficial sobre si `Bash(<patrón>)` vale en el `tools:` de un subagente se contradice entre `tools-reference` y `subagents`. La prosa admite que es una instrucción; un campo en silencio no admite nada. En opencode el bloque `permissions:` sí evalúa `action` + `resource` + `effect` en orden, y ahí el alcance por ruta es una declaración de verdad. La diferencia entre los dos adaptadores es una limitación de la herramienta, no del framework, y por eso se documenta en vez de esconderse. *Referencia: HU-14, auditoría 2026-09-29 (fila HU-07).*

## D25. Un aviso que solo vive en el documento generado no avisa a quien lo pidió

`inbox.stage()` ya producía el aviso de conversión de un original no markdown y `create_doc` lo escribía en el bloque `## Fuente` del documento creado; la spec §3 dice que el CLI "avisa que hay que hacerlo antes", y el aviso no salía por stdout. La spec no dice dónde: el documento generado lo lee la Decidora, después, y el humano que tipeó `doc new` no lo va a abrir para descubrir que su PDF quedó archivado sin convertir. `create_doc()` devuelve ahora el aviso como dato y la terminal lo muestra, sin cambiar el veredicto: el CLI no convierte PDF ni docx y no va a empezar a hacerlo. *Referencia: HU-14.*

## D26. La fase 3 se cierra con un solo adaptador: Copilot

La fase 3 se cierra con un solo adaptador, Copilot: es el de mayor uso y su convención (`AGENTS.md` más instrucciones por path con `applyTo`) es la más expresiva. No se implementan los cuatro que el registro enumera a la vez: `hermes` no tiene ni un referente verificable, y cuatro adaptadores a medio hacer son cuatro superficies de permisos que la herramienta puede ignorar en silencio (D24).

*Referencia: bitácora fase 7/8/9 y snapshot del 2026-10-02.*

## D27. El release de 0.8.0 mueve `main`

El release de 0.8.0 mueve `main`: PR `develop` → `main` y el tag semver sobre ese merge. `main` quedó en 0.6.0 solo porque era ancestro estricto de `develop` y no había forma de que contuviera únicamente la fase 6; con las fases 8 y 9 ya integradas, el tag y el contenido de `main` vuelven a decir lo mismo y el desfase termina acá.

*Referencia: bitácora fase 7/8/9 y snapshot del 2026-10-02.*

## D28. La publicación es manual hasta que exista CI

La publicación es manual hasta que exista CI: el repo no tiene `.github/workflows/`, así que `v0.7.0` salió de una shell con `UV_PUBLISH_TOKEN` y no hay ruta automatizada. La deuda entra como fila propia de la cola y no solo en la bitácora, porque la bitácora no es la cola de trabajo entre sesiones y `bandeja_entrada` mide antigüedad, no existencia: sin fila, ningún check la va a avisar.

*Referencia: bitácora fase 7/8/9 y snapshot del 2026-10-02.*

## D29. El idioma del contenido no es eje del preset

El idioma del contenido no es eje del preset: detrás de una clave `lang` hay i18n de los 17 templates —con los 8 de adaptadores, que además difieren entre opencode y Claude Code— y no hay ninguna bandera de idioma en el CLI. Queda fuera de la v1 y el idioma es decisión de proyecto, que es lo que el propio `AGENTS.md` generado ya dice: superficie pública en inglés, contenido generado en el idioma del proyecto. Si entra alguna vez, entra como fase propia.

*Referencia: bitácora fase 7/8/9 y snapshot del 2026-10-02.*

## D30. `init` declara y `agent add` ejecuta

`init` declara y `agent add` ejecuta: el preset escribe `[adapters] enabled` y el único comando que genera archivos de adaptador sigue siendo `agent add`. La razón es dura y no es de gusto: `generate_adapters()` pisa lo que encuentra sin preguntar, así que si `init` generara adaptadores, `init --here` rompería su propia promesa de no sobrescribir (D4) y podría pisar subagentes editados por el usuario. La distancia entre declarar y ejecutar la reconcilia el check `adaptadores_declarados`, que avisa y no corrige.

*Referencia: bitácora fase 7/8/9 y snapshot del 2026-10-02.*

## D31. Los umbrales se quedan en `[logsayer]` y no se mueven

Los umbrales se quedan en `[logsayer]` y no se mueven: cambiar la tabla a `[thresholds]` haría que todo proyecto ya scaffoldeado dejara de encontrar sus umbrales y volviera a los defaults **en silencio**, porque `LogsayerConfig.load()` no distingue "falta la tabla" de "no hay configuración". `[project]` y `[adapters]` son bloques nuevos que conviven con el viejo, así que el cambio no rompe nada y no obliga a migrar archivos versionados de los usuarios.

*Referencia: bitácora fase 7/8/9 y snapshot del 2026-10-02.*

## D32. La CI corre sobre la matriz que declara el paquete

La CI corre sobre la matriz que declara el paquete: 3.11, 3.12 y 3.13 son las que dicen `requires-python` y los classifiers, así que la batería corre en todas ellas o la CI estaría declarando menos que el paquete. Y `ruff format --check` queda **fuera** de la puerta: hoy quiere reformatear 34 archivos, y un gate que arranca rojo es deuda nueva.

*Referencia: bitácora fase 7/8/9 y snapshot del 2026-10-02.*

## D33. El tag no publica hasta que tag, `pyproject.toml` y `__version__` dicen lo mismo

El tag no publica hasta que tag, `pyproject.toml` y `__version__` dicen lo mismo: D11 ("la publicación es un hecho verificado, no una intención") vuelto mecanismo, y convierte el fallo de "un paquete publicado que miente" en "un corte con mensaje". El token sigue siendo una credencial de larga vida en el repo — Trusted Publishing (OIDC) es el cierre pendiente y tiene fila propia, aparte del release.

*Referencia: bitácora fase 7/8/9 y snapshot del 2026-10-02.*

## D34. `examples/hello-logsayer/README.md` se regenera al final del ciclo, no ahora

`examples/hello-logsayer/README.md` se regenera al final del ciclo, no ahora: promete ser salida real del CLI, así que cualquier cambio en la superficie lo vuelve falso, y las cuatro deudas que quedan (D-01, D-02, D-07, D-08) caen exactamente sobre sus líneas. Editarlo hoy a mano sería hacer trabajo que se tira.

*Referencia: bitácora fase 7/8/9 y snapshot del 2026-10-02.*

## D35. El contador de HUs del estado se verifica contra el disco, pero el umbral no se mueve

El contador de HUs del estado se verifica contra el disco, pero el umbral no se mueve: el check `contador_hus_al_dia` (HU-15) deriva el contador —directorios `HU-*` sin veredicto en el reporte que selló— y avisa en `warn` solo cuando lo declarado subestima, que es el único sentido que retrasa la auditoría. Declarar de más es el caso benigno y no avisa (decidir 3); sin auditoría sellada no se mide, en vez de asumir que todo está pendiente, porque un aviso permanente no avisa (como D19 con `indice_al_dia`). Y `logsayer audit status` muestra el derivado pero el veredicto de umbral sigue siendo el del declarado: el derivado informa, no mueve el gate, porque cambiar cuándo se propone auditar en un comando publicado es una decisión de umbral, no una corrección de número. El check se validó contra este mismo repo y **avisó el primer día** (declaraba 1, derivadas 2), que es la prueba de que no es decorativo (D9).

*Referencia: bitácora fase 7/8/9 y snapshot del 2026-10-02.*

## D36. Copilot se integra con perfiles por rol más instrucciones por path, no con un prompt único

D26 individuality adaptador y este es su diseño. `agent add copilot` genera ocho archivos: cuatro perfiles en `.github/agents/<rol>.agent.md` y cuatro instrucciones en `.github/instructions/logsayer/<rol>.instructions.md`. El motivo de que sean dos capas y no una es que `applyTo` es el mecanismo nativo de alcance por ruta, y sin él un solo prompt tendría que hacer el trabajo de cuatro: las reglas de la Decidora (escribe la tabla de veredictos en `docs/06_audits/`), las de la Reverenda Madre (bitácora append-only, escribe solo vía `logsayer log add`) y las del Navegante (solo lee `project_state.md`) no se pueden separar si todas llegan siempre. Ninguna de las dos capas duplica el otro: el perfil declara **quién es** y **qué superficie de herramientas** tiene, y la instrucción declara **en qué rutas y con qué reglas** trabaja. Los thresholds siguen en `logsayer.toml` y no se escriben en ningún prompt.

## D37. No se genera `.github/copilot-instructions.md`

Copilot consume `AGENTS.md` de forma nativa, así que ese archivo ya es el prompt de proyecto del CLI y no hace falta un instructions file global encima. Generar los dos sería una segunda fuente de verdad para lo mismo, y de las que peor se detectan: dos archivos que se contradicen no los separa ningún check. El frontmatter es `description` y el resto de la superficie va en la instrucción; el nombre del archivo no lleva `name:` porque es opcional y duplicaría el nombre del archivo.

## D38. `applyTo` es contexto por path, no permiso — y la superficie de herramientas va en `tools:`

Copilot no declara permisos por ruta: `applyTo` filtra **dónde se inyecta** la instrucción, no quién puede escribir, así que el patrón de escritura única por rol que sostienen el resto de los adaptadores no se puede declarar como campo. Por D24 se escribe lo que la herramienta declara y nada más: `tools:` en el perfil con los alias canónicos (`read`, `search`, `edit`, `execute`, `agent`, `web`, `todo`), y se omiten `target`, `argument-hint`, `handoffs` y `infer` — esta última está retirada. Los aliases desconocidos se ignoran en silencio, así que el test verifica contra la lista canónica y no contra lo que «funciona en mi máquina». La restricción de escritura única queda escrita en la prosa del template, como la excepción de Claude Code (D24).

## D39. El code review de Copilot queda excluido de las instrucciones de los roles

Los cuatro `.instructions.md` llevan `excludeAgent: "code-review"`. Los roles de logsayer no existen en una sesión de code review y el `applyTo` de las rutas de `docs/` no la alcanzaría igual, así que sin esto el prompt de cada rol aparece en un contexto donde el rol no puede actuar. El campo es una exclusión real —la doc oficial lo documenta como tal— y no un permiso: deja de inyectarse la instrucción, nada más.

## D40. El `truthsayer` de Copilot declara `edit`, y la falta de `Write`/`Edit` en el de Claude se reporta aparte

La Decidora tiene que escribir la tabla de veredictos, así que el perfil de Copilot declara `edit` sobre su archivo. Declarar menos de lo que el prompt exige es la clase de defecto que D24 prohíbe, y es **exactamente** lo que encontró la auditoría del 2026-10-02 en `templates/adapters/claude/truthsayer.md.j2`, cuyo `tools:` no incluye `Write` ni `Edit` mientras su línea 24 dice que escribe la tabla. Eso no se arregla de paso acá: es otro adaptador, otra herramienta y otra HU, y quedó con fila propia (D-12) en la cola. Mezclarlo en el PR del adaptador nuevo habría hecho la revisión de D-07 más difícil de leer y la deuda más difícil de fechar.

*Referencias: bitácora fase 3 del 2026-10-02, spec §6 (documentación oficial de GitHub Copilot: `custom-agents-configuration`, `create-custom-agents`, `custom-instructions-support`) y fila D-07 de `inbox/feedback_deudas_auditoria.md`.*

## D41. `adaptadores_declarados` mide el conjunto de archivos del adaptador, no cada archivo

El check avisa cuando un nombre de `[adapters] enabled` está en `SUPPORTED` pero **ninguno** de los archivos de su `AdapterSpec` existe en el proyecto. Se descartó la lectura archivo por archivo (avisar si falta alguno): quien escribió uno a mano ya ejecutó la parte de `agent add`, y un subagente borrado a conciencia no es un pendiente. Medirlo archivo por archivo convertiría cada proyecto que depure su `.claude/agents/` en un aviso permanente, que es la clase de ruido que D19 ya descartó para `indice_al_dia` y que D35 descartó para el contador de HUs: **un aviso que aparece siempre no avisa nada**. Lo que el check mide es la distancia estructural entre declarar y ejecutar (D30), y esa distancia se cierra ejecutando `agent add`, no completando el conjunto a mano.

Lo que sí se avisa, en orden: un nombre fuera de `SUPPORTED` no tiene nada que ejecutar y por eso corta antes de mirar archivos; después, los nombres declarados sin ningún archivo. Ninguna de las dos ramas corrige, como todo lo demás en Suk.

*Referencias: HU-18, spec §4, y la fila D-08 de `inbox/feedback_deudas_auditoria.md`.*
