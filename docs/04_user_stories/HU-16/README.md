# HU-16 — `audit reset` y shim deprecado para `--reset-counter`

> Cierre de D-02: evitar que `audit run --reset-counter` corra la auditoría antes de resetear
> (lo que scaffoldeaba un reporte vacío con el alcance entero). Se introduce `audit reset`
> que solo resetea y falla nombrando las HUs si hay veredictos pendientes.

## Qué hay que construir

- `src/logsayer/cli.py`: agregar comando `audit reset` (hereda alias `truthsayer audit reset`).
  - Si `audit.pending_verdicts()` no está vacío → `typer.BadParameter` nombrando las HUs.
  - Si vacío → `project.set_closed_hus(root, 0)` + echo de confirmación.
  - En `audit run`, el flag `--reset-counter` pasa a ser **shim deprecado**: corta con código 1 y mensaje
    `--reset-counter ya no resetea: usá logsayer audit reset` **antes** de llamar a `audit.run_audit()`.
- Templates de adaptadores: `src/logsayer/templates/adapters/opencode/truthsayer.md.j2` y
  `claude/truthsayer.md.j2` actualizan la instrucción a `logsayer audit reset`.
- Tests: ajustar el test del flag y agregar regresiones para `audit reset`.

## Cómo se valida

- `audit reset` con veredictos pendientes rechaza con código ≠ 0 y nombra las HUs pendientes.
- `audit reset` con reporte sellado completo resetea el contador a 0 y **no crea ningún archivo**
  en `docs/06_audits/`.
- `audit run --reset-counter` sale con código 1, no corre auditoría, no scaffoldea reporte nuevo
  y no reinicia el contador.
- El mensaje incluye `logsayer audit reset`.
