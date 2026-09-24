# Estado del proyecto — logsayer

> Snapshot operativo para el agente al iniciar cada sesión (Capa 2 — Navegante). No es acumulativo: se sobrescribe al cerrar sesión con aprobación previa. Referencia: `logsayer_especificacion_maestra.md` y `docs/`.

## Fase actual del roadmap

Dogfooding

El framework aplicándose sobre su propio desarrollo (marco de sesiones). Roadmap (spec §9): fases 0 a 5 cerradas; pendientes: fase 3 restante (adaptadores copilot/cursor/gemini/hermes por demanda), publicar en PyPI (token), fase 6 (comunidad).

## Decisiones activas

- D1 — Motor único + adaptadores finos (spec §6): la lógica vive en `core/`, los generados son wrappers al CLI.
- D2 — Alias plano como puerta de entrada (spec §13): `logsayer audit run` ≡ `logsayer truthsayer audit run`.
- D3 — Template mínimo por HU (spec §10): un README con "qué construir" + "cómo se valida".
- D4 — `init --here` en modo adopt (spec §5): scaffoldea sobre proyecto existente sin sobrescribir.
- D5 — Audit semántico honesto (spec §10): el CLI genera estructura + prompt; el veredicto lo produce la Decidora.

## HUs cerradas desde la última auditoría

0