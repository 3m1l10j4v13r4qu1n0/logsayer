# Metodología de trabajo con IA — logsayer

Cómo se trabaja en este repo con agentes de IA coordinados por logsayer (Capa 5).

## Marco de sesiones (spec §7)

1. **Apertura** — el agente lee solo `docs/project_state.md` (Capa 2). No relee los logbooks completos ni el roadmap.
2. **Chequeo de auditoría** — si el contador supera el umbral (`audit_threshold_hus = 3`), se propone auditoría antes de tomar tarea nueva.
3. **Trabajo** — se trabaja la HU leyendo solo su carpeta en `docs/04_user_stories/`; la bitácora solo bajo demanda (vía `00_index.md`).
4. **Cierre / commit** — con aprobación previa del usuario: snapshot de estado (sobrescribe) + entrada de logbook (append).
5. **Auditoría** — `logsayer audit run` genera estructura + prompt; la Decidora compara `04_user_stories` contra el código; resultado en `06_audits/`.

## Triggers

| Evento | Acción | Aprobación |
|---|---|---|
| Inicio de sesión | Leer `project_state.md` | No |
| Contador ≥ umbral | Proponer auditoría | Sí |
| Cierre / commit | Actualizar estado + bitácora | Sí |
| Decisión de arquitectura nueva | Entrada de logbook + `02_technical/decisions.md` | Sí |
| Logbook activo lleno (400 líneas) | Particionar y actualizar índice | No (mecánico) |

## Git flow

- `main` solo bootstrap; desarrollo en `develop`; features en `feature/<descripcion>`.
- Releases con tag semver (`v0.1.0`...).
- Reglas globales de git/git flow viven en `~/.config/opencode/rules/` (fuente: config global).