# Estado del proyecto — logsayer

> Snapshot operativo para el agente al iniciar cada sesión (Capa 2 — Navegante). No es acumulativo: se sobrescribe al cerrar sesión con aprobación previa. Referencia: `logsayer_especificacion_maestra.md` y `docs/`.

## Fase actual del roadmap

Fase 6 — Ingreso de documentos (cerrada y mergeada en `develop`; 0.7.0 aún sin publicar)

Fases 0 a 6 cerradas. El proyecto ya está publicado en PyPI: `logsayer` 0.6.0 subido el 2026-09-25 (verificado en vivo vía la API de PyPI). Pendientes: publicar 0.7.0 (tag `v0.7.0`), fase 3 restante (adaptadores copilot/cursor/gemini/hermes por demanda), fase 7 (comunidad: presets, más agentes) y la deuda que dejó la auditoría del 2026-09-27 en HU-07 (permisos del adaptador de Claude Code + dos criterios de aceptación desactualizados).

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

## HUs cerradas desde la última auditoría

0

Auditoría del 2026-09-27 aprobada y contador reseteado (HU-06..HU-09: 3 de 4 cumplen, HU-07 parcial con 3 acciones pendientes). El umbral vuelve a ser 3 HUs.
