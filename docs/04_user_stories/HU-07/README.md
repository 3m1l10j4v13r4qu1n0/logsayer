# HU-07 — Ruteo y derivación de documentos de Capa 1 (`doc route`, `doc new`)

> Fase 6 del roadmap. Cierra F1, F2 y F3 del feedback de usabilidad: el marco
> sabe qué capas existen, pero no dice qué hacer con un documento suelto.
>
> **Actualizado 2026-09-29 (HU-14).** La auditoría de esa fecha dejó esta HU en
> `parcial` por tres puntos: dos criterios de aceptación que describían el
> comportamiento anterior a D6/D10, y el requisito de permisos que solo el
> adaptador de opencode podía cumplir. Los dos criterios se corrigen acá y la
> superficie de permisos se reencuadra; el resto de la HU no se toca. Ver
> `docs/04_user_stories/HU-14/README.md` y las decisiones D24/D25.

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
  de derivar en `mentat.md.j2` (opencode y Claude Code). **Reencuadrado por
  HU-14:** cada adaptador declara la restricción con la unidad que su herramienta
  soporta. En opencode es el bloque `permissions:` con reglas `shell`/`allow`.
  En Claude Code el frontmatter de subagente solo da `tools` como allowlist de
  nombres de herramienta, y las reglas por recurso son de sesión, no de
  subagente: el CLI no las genera, y el template declara la excepción en vez de
  fingir un alcance que no puede expresar (D24).
- `doc.md.j2`: template mínimo, sin Hundreds de líneas (spec §10).

## Cómo se valida

- `doc route` sin argumento imprime las 6 filas de la tabla, cada una con su
  comando; la fila de HU dice `logsayer spec new`.
- `doc route inbox/contrato.pdf` no resuelve a una capa de Capa 1: la extensión
  no markdown manda el documento a la bandeja (`→ capa: fuera de docs/`) y
  avisa que hay que convertirlo antes. La capa la decide el Mentat; el CLI no
  clasifica un PDF como técnico (D6, D10). **Corregido por HU-14**: el criterio
  original pedía `docs/02_technical/...`, que es el comportamiento anterior a
  que la señal inequívoca dejara de tener un default a `02_technical/`.
- `doc new technical contrato_api` crea el archivo con header y `## Fuente`;
  con `--from`, el original termina en `inbox/_done/` y el doc referencia origen
  y fecha. Reintentar sobre un doc existente falla.
- `doc new hu ...` no existe (una sola forma de crear una HU) y el error lo dice.
- `doc new` con un `.pdf` avisa por stdout que hay que convertirlo antes; no
  convierte. El mismo aviso queda en el bloque `## Fuente` del documento creado
  (D25).
- Tests con `cwd_project`; `ruff`, `mypy`, `check` y `process check` en verde.
