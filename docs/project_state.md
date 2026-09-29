---
fase: fase9
---
# Estado del proyecto — logsayer

> Snapshot operativo para el agente al iniciar cada sesión (Capa 2 — Navegante). No es acumulativo: se sobrescribe al cerrar sesión con aprobación previa. Referencia: `logsayer_especificacion_maestra.md` y `docs/`.

## Fase actual del roadmap

Fases 0 a 6, 8 y 9 cerradas

La fase 9 (auditoría por pasada) cerró con la auditoría del 2026-09-29: es la
primera corrida con alcance verificable — el CLI scaffoldeó una fila por HU del
disco y `auditoria_completa` mide la cobertura parseando la tabla, no
interpretando prosa. Veredicto: 11 de 13 HUs cumplen, HU-07 y HU-13 quedaron
parciales (`docs/06_audits/audit_2026-09-29.md`).

> El campo `fase` del frontmatter de arriba es el identificador de la fase: es lo
> que `logsayer log add` convierte en el nombre del logbook. Solo se acepta un
> slug corto (letras, dígitos, `-`, `_`, `.`); la frase de la línea de arriba es
> contexto para humanos y no participa de esa decisión.

Pendientes, en orden: publicar 0.7.0 con su tag `v0.7.0`; cerrar la deuda que
dejó la auditoría (permisos del adaptador de Claude Code de HU-07, más los dos
criterios de aceptación desactualizados de esa HU); fase 3 restante (adaptadores
copilot/cursor/gemini/hermes por demanda); fase 7 (comunidad: presets, más
agentes). La fase 10 (frontmatter extendido) sigue desplazada: solo entra si
duele.

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
- D11 — La publicación en PyPI es un hecho verificado, no una intención: 0.6.0 en vivo desde el 2026-09-25. El token de PyPI viaja por variable de entorno; el `3m1l10j4v13r4qu1n0` que los docs llamaban "token" es el usuario de GitHub, no una credencial.
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

## HUs cerradas desde la última auditoría

0

Auditoría del 2026-09-29 aprobada y contador reseteado a 0 (venían 4 HUs desde
el 2026-09-27: HU-10, HU-11, HU-12 y HU-13; el contador del estado decía 2 y el
disco decía 4 — el número que dispara la auditoría es el único valor del marco
que ningún check verifica). Umbral 3: a la tercera HU cerrada, la Decidora
vuelve a correr y ahora el alcance lo verifica `auditoria_completa`.
