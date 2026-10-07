---
fase: fase7
---
# Estado del proyecto — logsayer

> Snapshot operativo para el agente al iniciar cada sesión (Capa 2 — Navegante). No es acumulativo: se sobrescribe al cerrar sesión con aprobación previa. Referencia: `logsayer_especificacion_maestra.md` y `docs/`.

## Fase actual del roadmap

**Fases 0 a 9 cerradas con código, sin fases a medio hacer.** La 7 (`init --preset`,
HU-18) fue la última con diseño escrito y superficie sin implementar; cerró el
ciclo. La 10 (frontmatter extendido) sigue desplazada a propósito: solo entra si
duele.

- **Versión:** 0.8.0 publicada en PyPI el 2026-10-01 por el job de CI (tag `v0.8.0`).
- **Auditoría:** 2026-10-02 aprobada (pasada el 2026-10-05), contador reseteado.
  13 `cumple`, 1 `sin cambios` (HU-09), 2 `parcial` (HU-05 y HU-08), 0 `no cumple`.
- **Deudas de esa auditoría cerradas:** D-12 (truthsayer de Claude con `Write`/`Edit`,
  PR #25) y D-13 (citas muertas en HU-13/HU-16/HU-18, PR #26). El detalle vive en
  `inbox/feedback_deudas_auditoria.md`.
- **Feedback de README** (`inbox/feedback_README.md`, 2026-10-05) aplicado en
  PR #27: roadmap reordenado, disclaimer al final, quick start limpio, fila
  `audit run --hu`, candidatos de `doc route` sin el prefijo de capa repetido.
  Quedan pendientes de esta fila solo los puntos de `project_state.md` (esta
  reescritura) y la regeneración del ejemplo (D-10).

Pendientes, en orden:

1. **D-10** — regenerar `examples/hello-logsayer/` contra la superficie actual
   (D34: al final del ciclo; el README ya lleva la nota provisoria). Es lo que
   falta para cerrar HU-05 y HU-08 del todo.
2. **D-11** — Trusted Publishing (OIDC) para borrar `PYPI_API_TOKEN`.
3. **D-07** — fila sin cerrar de HU-17 en el reporte del 2026-10-02
   (`auditoria_completa` avisa); resolver con `audit run --hu` o completando la fila.
4. Fase 10 (frontmatter extendido) — desplazada, solo si duele.

La cola vive en `inbox/feedback_deudas_auditoria.md` y `inbox/feedback_README.md`.

> El campo `fase` del frontmatter de arriba es el identificador de la fase: es lo
> que `logsayer log add` convierte en el nombre del logbook. Solo se acepta un
> slug corto (letras, dígitos, `-`, `_`, `.`); la frase de la línea de arriba es
> contexto para humanos y no participa de esa decisión.

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
- D40 — En el adaptador de Copilot la Decidora declara `edit` y la Reverenda Madre no, porque su única escritura es `logsayer log add`. La falta equivalente del `truthsayer` de Claude Code (D-12) se cerró en su propia fila (PR #25).
- D41 — `adaptadores_declarados` mide el conjunto de archivos de un adaptador, no cada archivo: avisa cuando un nombre de `[adapters] enabled` está en `SUPPORTED` pero **ninguno** de los archivos de su `AdapterSpec` existe. Quien escribió uno a mano ya ejecutó la parte de `agent add`, y un subagente borrado a conciencia no es un pendiente; medirlo archivo por archivo convertiría cada proyecto que depure su `.claude/agents/` en un aviso permanente, que es el ruido que D19 descartó para `indice_al_dia` y D35 para el contador.

## HUs cerradas desde la última auditoría

2

Auditoría del **2026-10-02** aprobada y contador reseteado a 0 (venían 3 HUs
desde el 2026-09-29: HU-14, HU-15 y HU-16). Desde el reset cerraron **HU-17**, el
adaptador de Copilot (D-07), y **HU-18**, los presets de proyecto (D-08), que
cerró la fase 7.

El reporte del 2026-10-02 selló 16 HUs y su tabla está completa, así que
`auditoria_completa` avisa por HU-17 y HU-18 hasta la próxima corrida: es D20
funcionando — el alcance es la tabla sellada, no el directorio — y no un hueco.
Umbral 3: falta 1 HU para que la Decidora vuelva a correr, y HU-19 sería la que
la dispare.
