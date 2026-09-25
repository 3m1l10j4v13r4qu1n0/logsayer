# HU-07 — Ruteo y derivación de documentos de Capa 1 (`doc route`, `doc new`)

> Fase 6 del roadmap. Cierra F1, F2 y F3 del feedback de usabilidad: el marco
> sabe qué capas existen, pero no dice qué hacer con un documento suelto.

## Qué hay que construir

- `core/routing.py`: la tabla de decisión **explícita** (entrada → capa →
  destino → ¿se versiona?), como dato del core, no heurística. El ruteo por
  nombre o extensión es juicio, y el juicio lo tiene el subagente, no el bot
  (spec §2, §10).
- `logsayer doc route [<archivo>]`: imprime la tabla; con argumento, la fila que
  aplica a ese archivo (capa, destino, si se versiona, y el comando a correr).
  No escribe nada.
- `logsayer doc new <global|technical> <nombre> [--from <archivo>]`: scaffoldea
  el documento con header estándar (`# Título`, `Fecha` · `Estado`, `## Resumen`)
  y bloque `## Fuente` cuando viene de un archivo. Con `--from`, mueve el
  original a `inbox/_done/`. Las HU siguen usando `spec new` (spec §5).
- Alias de rol `logsayer mentat doc route` / `logsayer mentat doc new` (spec §13).
- Permisos `doc route*` y `doc new*` en los dos `mentat.md.j2`, y la instrucción
  de derivar en `mentat.md.j2` (opencode y Claude Code).
- `doc.md.j2`: template mínimo, sin Hundreds de líneas (spec §10).

## Cómo se valida

- `doc route` sin argumento imprime las 6 filas de la tabla, cada una con su
  comando; la fila de HU dice `logsayer spec new`.
- `doc route inbox/contrato.pdf` resuelve a `docs/02_technical/...` y avisa que la
  fuente externa no se versiona.
- `doc new technical contrato_api` crea el archivo con header y `## Fuente`;
  con `--from`, el original termina en `inbox/_done/` y el doc referencia origen
  y fecha. Reintentar sobre un doc existente falla.
- `doc new hu ...` no existe (una sola forma de crear una HU) y el error lo dice.
- `doc new` con un `.pdf` avisa que hay que convertirlo antes; no convierte.
- Tests con `cwd_project`; `ruff`, `mypy`, `check` y `process check` en verde.
