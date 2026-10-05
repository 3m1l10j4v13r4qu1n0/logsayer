---
fase: fase7
---
# Estado del proyecto — logsayer

> Snapshot operativo para el agente al iniciar cada sesión (Capa 2 — Navegante). No es acumulativo: se sobrescribe al cerrar sesión con aprobación previa. Referencia: `logsayer_especificacion_maestra.md` y `docs/`.

## Fase actual del roadmap

**Fases 0 a 9 cerradas, y ahora las nueve tienen código.** La 7 fue la última que
tenía diseño escrito y superficie sin implementación: cerró con HU-18
(`init --preset`). Con ella no queda ninguna fase del roadmap a medio hacer — la
10 sigue desplazada a propósito (solo entra si duele) y lo que queda abierto son
deudas con fila propia, no fases.

La decisión de fondo la fijó el humano el 2026-09-30 y la implementación la
ejecutó sin discutirla: el preset es un **snapshot, no una herencia viva**, así que
`init` copia los valores al `logsayer.toml` y el preset deja de existir para ese
proyecto. No hay que resolver "qué pasa si el preset cambia en la próxima versión"
y el TOML se edita sin sorpresas. El precio —actualizar logsayer no actualiza los
umbrales de un proyecto ya scaffoldeado— se paga con dos checks, no con una
migración.

Lo que salió del contraste con el código y no estaba escrito:

- **`default` no declara la tabla `[logsayer]`.** Como la precedencia son dos
  escalones (el preset elige; cada clave que declara pisa el default del dataclass
  y las que omite caen al default), no declarar nada es literalmente "usar los
  defaults". Así `init` e `init --preset default` coinciden **por construcción** y
  no por valores repetidos: el test compara las dos salidas en vez de afirmar una
  lista.
- **`LogsayerConfig.from_mapping()`** saca la validación de `[logsayer]` de
  `load()`. Sin eso, el preset se validaría contra un segundo validador y un preset
  roto podría llegar al scaffold — que era justo el punto 1 de la fila D-08.
- **D41**: `adaptadores_declarados` mide el **conjunto** de archivos de un
  adaptador y no cada archivo. Quien escribió uno a mano ya ejecutó la parte, y un
  subagente borrado a conciencia no es un pendiente; medirlo archivo por archivo
  daría un aviso permanente en cada proyecto que depure, que es la clase de ruido
  que D19 y D35 ya descartaron.

Fases 0 a 9 **cerradas**. La fase 3 cerró con HU-17: el adaptador de GitHub
Copilot, el último de los tres, y el único que necesitó una decisión de diseño
(D26 lo decidió así: uno solo, no los cuatro que el registro enumeraba).

Copilot no tiene la convención de los otros dos. `agent add copilot` escribe
ocho archivos en vez de cuatro, porque su convención parte el rol en dos:
perfil en `.github/agents/<rol>.agent.md` (quién es el rol y qué herramientas
tiene) e instrucción en `.github/instructions/logsayer/<rol>.instructions.md`
(en qué rutas aplica). Si se escribiera uno solo, los cuatro prompts llegarían a
todos los contextos del repo.

Lo que se decidió leyendo la documentación oficial de GitHub, y que quedó
escrito como decisión (spec §6):

- **`applyTo` es filtro de contexto, no permiso.** Decide dónde se inyecta la
  instrucción y no qué puede escribir el rol, así que la escritura única por capa
  se escribe en la prosa de cada template, igual que en el adaptador de Claude
  Code (D38). Los ocho archivos llevan `excludeAgent: "code-review"`, porque los
  roles no existen en una sesión de code review (D39).
- **No se genera `.github/copilot-instructions.md`.** Copilot consume `AGENTS.md`
  de forma nativa y ese archivo ya es el prompt de proyecto que genera el CLI;
  el archivo extra sería una segunda fuente de verdad para lo mismo (D37).
- **Perfil con dos campos:** `description` y `tools`, con los alias canónicos de
  la herramienta. Se omiten `target` (existe, pero sin valor sirve para GitHub.com
  y para el IDE), `argument-hint` y `handoffs` (la doc los declara ignorados) e
  `infer` (retirada). La Decidora declara `edit` porque escribe la tabla de
  veredictos; la Reverenda Madre no, porque su única escritura es
  `logsayer log add` (D40).

Auditoría **2026-10-02** (scaffoldeada ese día, pasada ejecutada el 2026-10-05)
aprobada y contador reseteado a 0. Resultado: 13 HUs `cumple`, 1 `sin cambios`
por herencia (HU-09), 2 `parcial` y ninguna `no cumple`
(`docs/06_audits/audit_2026-10-02.md`). Las dos parciales —HU-05 y HU-08—
comparten una sola causa externa: `examples/hello-logsayer/README.md` promete
una salida real del CLI que dejó de serlo cuando las fases 8 y 9 movieron la
superficie (D-10, con D34 decidiendo el momento de regenerarlo). La síntesis no
encontró contradicciones entre veredictos.

La auditoría dejó dos deudas que siguen abiertas: **D-12** (el `truthsayer` de
Claude declara `tools:` sin `Write`/`Edit` y por lo tanto no puede llenar la tabla
que su propio prompt le asigna — la clase de defecto que D24 prohíbe al revés, y
que en Copilot se resolvió al revés declarando `edit`) y **D-13** (los README de
HU-13 y HU-16 citan rutas que no resuelven, lo que bloquea su herencia en cada
corrida).

> El campo `fase` del frontmatter de arriba es el identificador de la fase: es lo
> que `logsayer log add` convierte en el nombre del logbook. Solo se acepta un
> slug corto (letras, dígitos, `-`, `_`, `.`); la frase de la línea de arriba es
> contexto para humanos y no participa de esa decisión.

Pendientes, en orden: las dos deudas de la auditoría del 2026-10-02 — D-12 (el
`truthsayer` de Claude Code declara `tools:` sin `Write`/`Edit` y no puede llenar la
tabla que su propio prompt le asigna) y D-13 (los README de HU-13 y HU-16 citan
rutas que no resuelven); la regeneración de `examples/hello-logsayer/`, que era lo
que faltaba para que la superficie quedara quieta (D-10, con D34 decidiendo el
momento); y Trusted Publishing (OIDC) para borrar `PYPI_API_TOKEN` (D-11). La cola
vive en `inbox/feedback_deudas_auditoria.md`. La fase 10 (frontmatter extendido)
sigue desplazada: solo entra si duele.

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
- D11 — La publicación en PyPI es un hecho verificado, no una intención: 0.6.0, 0.7.0 y **0.8.0** (2026-10-01) comprobados en la JSON API y reinstalando el paquete en un venv limpio. El token de PyPI viaja por variable de entorno; el `3m1l10j4v13r4qu1n0` que los docs llamaban "token" es el usuario de GitHub, no una credencial.
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
- D22 — `--hu` repite una pasada y no escribe reporte: el alcance vive en la tabla, y un reporte con una sola fila sería el último y dejaría el resto sin cubierto.
- D23 — La síntesis lee solo la tabla de veredictos, y solo si algún veredicto cambió: abrir HUs para sintetizar sería una segunda pasada entera.
- D24 — La superficie de permisos se declara con la unidad que la herramienta soporta: opencode tiene bloque `permissions:` por acción/recurso/efecto, Claude Code solo el allowlist `tools` (granularidad por herramienta), Copilot solo `tools` con alias canónicos y el alcance por ruta como filtro de contexto. No se escribe un campo que la herramienta pueda ignorar en silencio, y `settings.json` no se genera porque es de sesión.
- D25 — Un aviso que solo vive en el documento generado no avisa a quien lo pidió: `doc new` muestra el aviso de conversión por stdout, además de dejarlo en el bloque `## Fuente`.
- D26 — La fase 3 se cierra con un solo adaptador, Copilot: es el de mayor uso y su convención (`AGENTS.md` más instrucciones por path con `applyTo`) es la más expresiva. No se implementan los cuatro que el registro enumera a la vez: `hermes` no tiene ni un referente verificable, y cuatro adaptadores a medio hacer son cuatro superficies de permisos que la herramienta puede ignorar en silencio (D24). **Ejecutada en HU-17.**
- D27 — El release de 0.8.0 mueve `main`: PR `develop` → `main` y el tag semver sobre ese merge. `main` quedó en 0.6.0 solo porque era ancestro estricto de `develop`; con las fases 8 y 9 ya integradas, el tag y el contenido de `main` volvieron a decir lo mismo.
- D28 — La publicación es manual hasta que exista CI: el repo no tenía `.github/workflows/`, así que `v0.7.0` salió de una shell con `UV_PUBLISH_TOKEN`. La deuda entró como fila propia de la cola y no solo en la bitácora, porque la bitácora no es la cola de trabajo entre sesiones y `bandeja_entrada` mide antigüedad, no existencia. **Cerrada:** la CI existe y el tag `v0.8.0` publicó por el job.
- D29 — El idioma del contenido no es eje del preset: detrás de una clave `lang` hay i18n de los templates —con los de adaptadores, que además difieren entre opencode, Claude Code y Copilot— y no hay ninguna bandera de idioma en el CLI. Queda fuera de la v1 y el idioma es decisión de proyecto.
- D30 — `init` declara y `agent add` ejecuta: el preset escribe `[adapters] enabled` y el único comando que genera archivos de adaptador sigue siendo `agent add`. La razón es dura: `generate_adapters()` pisa lo que encuentra sin preguntar, así que si `init` generara adaptadores, `init --here` rompería su promesa de no sobrescribir (D4) y podría pisar subagentes editados por el usuario. Lo reconcilia el check `adaptadores_declarados`, que avisa y no corrige.
- D31 — Los umbrales se quedan en `[logsayer]` y no se mueven: cambiar la tabla a `[thresholds]` haría que todo proyecto ya scaffoldeado dejara de encontrar sus umbrales y volviera a los defaults **en silencio**, porque `LogsayerConfig.load()` no distingue "falta la tabla" de "no hay configuración".
- D32 — La CI corre sobre la matriz que declara el paquete: 3.11, 3.12 y 3.13. `ruff format --check` queda **fuera** de la puerta: hoy quiere reformatear 34 archivos, y un gate que arranca rojo es deuda nueva.
- D33 — El tag no publica hasta que tag, `pyproject.toml` y `__version__` dicen lo mismo: D11 vuelto mecanismo. El token sigue siendo una credencial de larga vida — Trusted Publishing (OIDC) es el cierre pendiente y tiene fila propia, aparte del release.
- D34 — `examples/hello-logsayer/README.md` se regenera al final del ciclo, no ahora: promete ser salida real del CLI, así que cualquier cambio en la superficie lo vuelve falso, y las deudas que quedan (D-01, D-02, D-08, D-10) caen exactamente sobre sus líneas. Editarlo hoy a mano sería hacer trabajo que se tira.
- D35 — El contador de HUs del estado se verifica contra el disco, pero el umbral no se mueve: el check `contador_hus_al_dia` deriva el contador —directorios `HU-*` sin veredicto en el reporte que selló— y avisa en `warn` solo cuando lo declarado subestima. Declarar de más es el caso benigno; sin auditoría sellada no se mide, en vez de asumir que todo está pendiente. El check se validó contra este mismo repo y **avisó el primer día** (declaraba 1, derivadas 2), que es la prueba de que no es decorativo (D9).
- D36 — El adaptador de Copilot escribe **dos archivos por rol**: perfil en `.github/agents/<rol>.agent.md` e instrucción en `.github/instructions/logsayer/<rol>.instructions.md`. Con un archivo solo, los cuatro prompts llegarían a todos los contextos del repo y las reglas de la Decidora se aplicarían a los archivos de la Reverenda Madre.
- D37 — No se genera `.github/copilot-instructions.md`: Copilot consume `AGENTS.md` de forma nativa y ese archivo ya es el prompt de proyecto que genera el CLI, así que el extra sería una segunda fuente de verdad para lo mismo — y dos archivos que se contradicen no los separa ningún check.
- D38 — `applyTo` es **filtro de contexto, no permiso**: decide dónde se inyecta la instrucción y no qué puede escribir el rol. Por eso la escritura única por capa queda escrita en la prosa de cada template, como ya hacía el adaptador de Claude Code, y no en un campo. `target` existe y es válido, pero se omite: sin valor sirve para GitHub.com y para el IDE, y fijarlo reduciría el alcance. `argument-hint` y `handoffs` no se emiten porque la documentación los declara ignorados en GitHub.com, e `infer` porque está retirada.
- D39 — Los ocho archivos de Copilot llevan `excludeAgent: "code-review"`: los cuatro roles son de una sesión de trabajo con contexto propio y no existen en una sesión de code review, donde el contexto es el diff.
- D40 — En el adaptador de Copilot la Decidora declara `edit` y la Reverenda Madre no, porque su única escritura es `logsayer log add`. La falta equivalente del `truthsayer` de Claude Code (D-12) es una deuda aparte y no se corrigió en la misma HU: tocar dos adaptadores a la vez es cómo una HU deja de ser auditable.

- D41 — `adaptadores_declarados` mide el conjunto de archivos de un adaptador, no cada archivo: avisa cuando un nombre de `[adapters] enabled` está en `SUPPORTED` pero **ninguno** de los archivos de su `AdapterSpec` existe. Quien escribió uno a mano ya ejecutó la parte de `agent add`, y un subagente borrado a conciencia no es un pendiente; medirlo archivo por archivo convertiría cada proyecto que depure su `.claude/agents/` en un aviso permanente, que es el ruido que D19 descartó para `indice_al_dia` y D35 para el contador.

## HUs cerradas desde la última auditoría

2

Auditoría del **2026-10-02** aprobada y contador reseteado a 0 (venían 3 HUs
desde el 2026-09-29: HU-14, HU-15 y HU-16). Desde el reset cerraron **HU-17**, el
adaptador de Copilot (D-07), y **HU-18**, los presets de proyecto (D-08), que
cerró la fase 7.

El reporte del 2026-10-02 selló 16 HUs y su tabla está completa, así que
`auditoria_completa` y `contador_hus_al_dia` avisan por HU-17 y HU-18 hasta la
próxima corrida: es D20 funcionando — el alcance es la tabla sellada, no el
directorio — y no un hueco. Umbral 3: falta 1 HU para que la Decidora vuelva a
correr, y HU-19 sería la que la dispare.