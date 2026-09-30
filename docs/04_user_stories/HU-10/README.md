# HU-10 — Índice de memoria: frontmatter `tags` y `docs/00_memory_index.md`

> Fase 8 (memoria seleccionable) — primera mitad. Diseño: `docs/02_technical/memory_architecture.md`.
> Cierra el índice generado; el retrieval (`memory search`) y el check `indice_al_dia` son HU-11.

## Qué hay que construir

- `core/memory.py` (D1): parseo del frontmatter con el **único** campo `tags` (D13),
  nivel derivado de la ruta y generación del artefacto `docs/00_memory_index.md`
  (una línea por documento de `docs/`, sin más y sin menos). El índice se
  regenera, no se edita a mano.
- `logsayer memory index` y `logsayer memory status`, con alias de rol
  (`logsayer navigator memory …`), como el resto de la superficie.
- Exención de `docs/00_memory_index.md` en el check `capas_mezcladas`: es un
  artefacto transversal (D12), no una sexta capa, y sin la exención dispara
  `fail`.
- Frontmatter `tags` en la plantilla `doc.md.j2`: el CLI lo scaffoldea, el
  Mentat lo refina (D8). Las tags del índice son las del frontmatter cuando
  existen y, si faltan, las derivadas mecánicamente del nombre `snake_case` y
  de la HU citada en `## Fuente`.

### Decisiones tomadas en esta HU

1. **Niveles.** El diseño define 0/1/2 para `project_state.md`+`01_global/`,
   `02_technical/` y `HU-XX/`, y no dice qué pasa con el resto de las capas.
   Acá `03_process/`, `05_agile_methodology/`, `06_audits/` y `logbooks/` son
   **nivel 3**: la numeración es "distancia a la especificación", y esas capas
   no compiten por ser fuente de verdad de una HU.
2. **`memory status` cae acá** y no en HU-11: es introspección del índice
   (qué indexa, cuántas líneas, con cuántas tags). Lo fresco —"cuándo quedó
   viejo"— es de `indice_al_dia`, en HU-11.
3. **El frontmatter obliga a tocar `header_capa1`.** Ese check exige `# Título`
   en la primera línea; con frontmatter arriba, todo documento scaffoldeado
   passaría a fallar. Se ajusta para saltear el bloque `---`, no para aflojar la
   regla: la siguen teniendo que cumplir título, `Fecha · Estado` y `## Resumen`.

### Lo que explícitamente NO se hace

- **No hay `search` ni `indice_al_dia`**: son HU-11. `status` no calcula
  frescura, dice qué hay.
- **No se reescriben los documentos existentes para agregarles tags.** El
  frontmatter es opcional y el índice es correcto igual: por eso la derivación
  desde el nombre es el piso, no el techo.
- **No se indexa nada fuera de `docs/`.** `inbox/` es staging (D6) y los `.md`
  de la raíz del repo no son de ninguna capa.
- **No se parsea el cuerpo del documento** más allá del header estándar
  (`Fecha · Estado`) y del bloque `## Fuente`: leer prosa para extraer metadata
  es juicio de LLM, y el índice es mecánico.

## Cómo se valida

- `logsayer memory index` sobre este repo produce un índice con una línea por
  documento de `docs/`, sin ninguno de más y sin ninguno de menos.
- El índice sobrevive a un `doc new`: el documento scaffoldeado entra al
  reindexar, con las tags que trae su frontmatter.
- Un documento con `tags:` en el frontmatter muestra esas tags; uno sin ellas
  muestra las derivadas del nombre. Un documento con frontmatter mal formado no
  rompe la indexación: se indexa igual, sin tags.
- `logsayer memory status` informa el artefacto (ruta, cantidad de documentos,
  de tags) y qué comando lo regenera; no inventa un veredicto de frescura.
- `logsayer check` y `logsayer process check` en verde con el índice presente:
  `capas_mezcladas` no lo señala y `header_capa1` tolera el frontmatter.
- `logsayer memory index` es idempotente: correrlo dos veces no cambia el
  archivo.
- Batería completa en verde: `pytest`, `ruff check src tests`, `mypy src`.
