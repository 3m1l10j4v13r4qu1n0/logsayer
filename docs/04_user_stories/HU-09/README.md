# HU-09 — Checks de Capa 1: destino sugerido, header estándar y staleness

> Fase 6 del roadmap. Cierra F3, F7 y F8 del feedback de usabilidad.

## Qué hay que construir

- `capas_mezcladas` deja de ser un error mudo: cada hallazgo incluye la capa y
  el destino sugerido, no solo "documento markdown fuera de capa" (F3).
- Check de **header estándar** en los documentos de Capa 1 no-HU
  (`01_global/`, `02_technical/`): `# Título`, `Fecha` · `Estado`, `## Resumen`.
  Los `.md` de la raíz no se escanean (no son de ninguna capa).
- Check `estado_al_dia`: si algún documento de Capa 1 tiene fecha de última
  modificación más nueva que `project_state.md`, el snapshot está viejo
  (F7). Fecha por `git log -1` si el proyecto es un repo git, mtime si no.

## Lo que explícitamente NO se hace

- **No se detectan "docs huérfanos" por mención.** El estado es prosa libre:
  un check que busca "el nombre del doc aparece en el estado o en un logbook"
  falla para siempre en `01_global/` (visión, alcance — nunca se citan) y deja
  de ser determinista. La coherencia entre capas es de la Decidora (spec §10).
- **No se valida el bloque `## Fuente`.** El template lo prescribe, pero `check`
  no puede distinguir un doc derivado de uno escrito a mano.

## Cómo se valida

- Un `.md` suelto en `docs/` reporta la capa sugerida en el mensaje.
- Un doc de `02_technical/` sin header falla; con header, pasa.
- Un doc de Capa 1 más nuevo que el estado dispara el warning con el nombre de
  los archivos; Updating el estado lo deja en verde.
- Sin git (o sin repo), el staleness usa mtime y no rompe.
- `pytest`, `ruff`, `mypy`, `check` y `process check` en verde.
