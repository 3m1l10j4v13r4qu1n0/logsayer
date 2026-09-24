# Definition of Ready — logsayer

Criterios objetivo para considerar una HU lista para trabajar y para cerrar (Capa 5 — Fremen). Reglas del equipo; el framework solo verifica su cumplimiento estructural.

## Para arrancar una HU

- La HU vive en `docs/04_user_stories/HU-XX/` con su README (qué construir + cómo se valida).
- La fase del roadmap está reflejada en `docs/project_state.md` (Capa 2).
- El contador de auditoría está por debajo del umbral (`audit status`); si no, se audita antes.

## Para cerrar una HU

- `pytest` pasa completo.
- `ruff check src tests` pasa.
- `mypy src` (strict) pasa.
- `logsayer check` reporta estado sano (estructura y capas).
- Si el cambio toca el CLI o la estructura: `logsayer fremen verify` sano.
- Se incrementa el contador de HUs en `project_state.md` y se registra la entrada de logbook.