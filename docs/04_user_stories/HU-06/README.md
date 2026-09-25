# HU-06 — Bandeja de entrada (`inbox/`) y su aviso en `check`

> Fase 6 del roadmap (ingreso de documentos). Origen: feedback de usabilidad
> `feelback_usabilidad_2026-09-25.md` (F1, F4, F6) — un documento externo que
> llega al proyecto no tiene lugar ni comando.

## Qué hay que construir

- `inbox/` en la raíz del proyecto, **fuera de `docs/`** (spec §3), con su propio
  `.gitignore` (`*`) para que lo que entra no se versione sin tocar el
  `.gitignore` del usuario. `init` la crea; `init --here` también (modo adopt).
- `core/inbox.py`: `add` (mueve el archivo que el humano le señaló, validando que
  exista y que no venga de adentro), `pending` (lista lo que no fue ubicado,
  excluyendo `_done/`), `mark_done` (mueve a `inbox/_done/`), `age_days`.
- Check `bandeja_entrada` en Suk Doctor: lista pendientes y, si alguno supera
  `inbox_max_age_days` de `logsayer.toml`, avisa que la bandeja envejece.
- **Nivel `warn` en `CheckResult`**: una bandeja con pendientes es un proyecto
  sano con un pendiente, no un fallo. Exit code 1 solo con `fail`.

## Cómo se valida

- `init` genera `inbox/.gitignore`; `git status` no muestra lo que se deja ahí.
- `check` en un proyecto recién scaffoldeado: `✔ bandeja_entrada: sin bandeja
  (opcional)` — sin ruido.
- Con un archivo en `inbox/`: `! bandeja_entrada: 1 sin ubicar` y exit code 0.
- Con el archivo viejo (mtime manipulado): el mismo `warn` con la antigüedad.
- `inbox add` con un archivo de `~/Downloads` lo deja en `inbox/`; con un path
  inexistente o dentro de `inbox/` falla con mensaje claro.
- `pytest`, `ruff check src tests`, `mypy src`, `logsayer check` y
  `logsayer process check` en verde.
