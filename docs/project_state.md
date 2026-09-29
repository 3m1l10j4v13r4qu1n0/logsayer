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

La deuda de HU-07 se cierra con HU-14, en la rama
`feature/hu-14-cierre-deuda-hu-07`: el aviso de conversión de `doc new` sale por
stdout (D25), la superficie de permisos de cada adaptador queda declarada con la
unidad que su herramienta soporta y la excepción de Claude Code escrita en la
spec §6 y en el template (D24). HU-13 ya había quedado resuelta por el PR #9
(`audit run --hu` apuntaba a `docs/06_audits/None`).

> El campo `fase` del frontmatter de arriba es el identificador de la fase: es lo
> que `logsayer log add` convierte en el nombre del logbook. Solo se acepta un
> slug corto (letras, dígitos, `-`, `_`, `.`); la frase de la línea de arriba es
> contexto para humanos y no participa de esa decisión.

Pendientes, en orden: mergear el PR de HU-14; publicar 0.7.0 con su tag
`v0.7.0` (el `[Unreleased]` del CHANGELOG está vacío con las fases 8 y 9 sin
documentar, así que la versión a cortar hay que decidirla); refrescar `AGENTS.md`
y el roadmap del README, que siguen diciendo "fase 8 (current)"; fase 3 restante
(adaptadores copilot/cursor/gemini/hermes por demanda); fase 7 (comunidad:
presets, más agentes). Dos hallazgos de la auditoría siguen abiertos: el
contador de HUs del estado no lo verifica ningún check, y
`audit run --reset-counter` scaffoldea un reporte nuevo con el alcance entero
vacío antes de resetear. La fase 10 (frontmatter extendido) sigue desplazada:
solo entra si duele.

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
- D24 — La superficie de permisos se declara con la unidad que la herramienta soporta: opencode tiene bloque `permissions:` por acción/recurso/efecto, Claude Code solo el allowlist `tools` (granularidad por herramienta). No se escribe un campo que la herramienta pueda ignorar en silencio, y `settings.json` no se genera porque es de sesión.
- D25 — Un aviso que solo vive en el documento generado no avisa a quien lo pidió: `doc new` muestra el aviso de conversión por stdout, además de dejarlo en el bloque `## Fuente`.

## HUs cerradas desde la última auditoría

1

Auditoría del 2026-09-29 aprobada y contador reseteado a 0 (venían 4 HUs desde
el 2026-09-27: HU-10, HU-11, HU-12 y HU-13; el contador del estado decía 2 y el
disco decía 4 — el número que dispara la auditoría es el único valor del marco
que ningún check verifica). Umbral 3: a la tercera HU cerrada, la Decidora
vuelve a correr y ahora el alcance lo verifica `auditoria_completa`.

Desde el reset cierra HU-14 (deuda de HU-07). `auditoria_completa` va a
avisar hasta la próxima corrida —HU-14 no estaba en el alcance del reporte
sellado—: es el comportamiento diseñado, no un hueco.
