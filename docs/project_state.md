# Estado del proyecto — logsayer

> Snapshot operativo para el agente al iniciar cada sesión (Capa 2 — Navegante). No es acumulativo: se sobrescribe al cerrar sesión con aprobación previa. Referencia: `logsayer_especificacion_maestra.md` y `docs/`.

## Fase actual del roadmap

Fase 6 — Ingreso de documentos (0.7.0)

Fases 0 a 5 cerradas; la 6 acaba de cerrarse con `inbox/`, `inbox add`, `doc route` y `doc new`. Pendientes: publicar en PyPI (token), fase 3 restante (adaptadores copilot/cursor/gemini/hermes por demanda), fase 7 (comunidad: presets, más agentes).

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

## HUs cerradas desde la última auditoría

4

HU-06 (bandeja + warn), HU-07 (ruteo y doc new), HU-08 (onboarding público), HU-09 (checks de Capa 1). Umbral 3 superado: la próxima sesión arranca proponiendo auditoría de la Decidora.
