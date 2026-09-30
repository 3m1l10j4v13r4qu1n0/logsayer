# HU-11 — Retrieval de memoria: `memory search` y el check `indice_al_dia`

> Fase 8 (memoria seleccionable) — segunda mitad. Diseño: `docs/02_technical/memory_architecture.md`.
> HU-10 dejó el índice; acá se cierra el retrieval y la frescura que lo vigila.

## Qué hay que construir

- `logsayer memory search "<consulta>"` en `core/memory.py` (D1): tokeniza la
  consulta, la intersecta con las tags del índice, ordena y corta. Sin LLM y
  sin embeddings. Con `--capa` para acotar a una capa y `--limit` para el corte
  (`0` = todos).
- `indice_al_dia` como check de **Fremen** (Capa 5): el índice no puede quedar
  viejo sin aviso. Reusa el patrón de `estado_al_dia` —el máximo entre
  `git log -1` y el mtime, extraído a `core/freshness.py` para que los dos
  checks midan lo mismo.
- `core/layers.py`: la taxonomía de capas en un solo lugar, importada por el
  Suk, el índice y `--capa`.
- Los adaptadores de **Truthsayer** y **Mentat** usan `search` para ordenar su
  arranque, con la garantía de alcance escrita en el prompt (D14).

### Decisiones tomadas en esta HU

1. **El retriever lee el artefacto, no los documentos.** `memory search` parsea
   `docs/00_memory_index.md` en vez de volver al disco. La consecuencia es
   deliberada: si leyera los archivos, `indice_al_dia` no detectaría nada y el
   índice sería decorativo. El precio es que hay que reindexar para que un
   documento nuevo sea encontrable, y ese precio lo paga el check.
2. **El ranking son las tags, y el desempate es el orden del índice.** Puntaje
   por tags que matchean (exacto pesa más que prefijo), y a igualdad de puntaje
   el nivel más cercano a la especificación y después la ruta. Es el mismo orden
   con el que se lee el índice, para que los dos artefactos se lean como las
   mismas capas. La ruta **no** puntúa: matchear `readme` o `technical`
   devolvería casi todo y el ranking dejaría de filtrar.
3. **`indice_al_dia` mira solo Capa 1.** El diseño dice "el documento más
   reciente que indexa", pero `log add` anexa al logbook (Capa 3) y el cierre de
   sesión reescribe `project_state.md`: con el alcance completo, casi todo
   cierre dejaría el índice viejo y un aviso que aparece siempre deja de avisar
   (D7). Las capas que no compiten por ser fuente de verdad de una HU (D15) no
   cambian lo que el agente tiene que leer primero.
4. **Sin fase declarada, `warn` visible; no se adivina.** `indice_al_dia` es
   `warn` y no `fail`: se arregla con un comando, no es una estructura rota. Y
   el índice ausente es opcional, como la bandeja: un proyecto scaffoldeado
   antes de la fase 8 no tiene por qué romper `process check`.
5. **`search` cuelga del mismo grupo `memory` que `index` y `status`**, cuyo
   alias de rol es el Navegante. El diseño lo imaginaba colgado del Mentat y la
   Truthsayer, pero colgarles el grupo entero les daría `memory index` —una
   escritura fuera de su alcance declarado—. Con D2 ("el alias plano es la
   puerta de entrada") alcanza con que el comando exista en la raíz y lo
   consuman desde el prompt del rol.

### Lo que explícitamente NO se hace

- **No hay búsqueda semántica ni embeddings**: dependencia, costo y
  no-determinismo. El diseño ya los deja para una evolución posterior.
- **No se regenera el índice dentro de `search`.** Un retrieval que reindexa
  antes de responder no puede estar viejo, y entonces no hay nada que verificar.
- **No se matchea el cuerpo del documento.** Solo las tags del contrato. Leer
  prosa para extraer signals es juicio de LLM, y el índice es mecánico.
- **No se recortan las tags declaradas.** Una tag que no matchea nada es
  información —de que la clasificación está mal— y borrarla sería tapar el
  síntoma.

## Cómo se valida

- `logsayer memory search "motor de memoria"` rankea
  `02_technical/memory_architecture.md` por encima de documentos sin relación.
- `memory search --capa` nunca devuelve documentos de otra capa, y una capa
  desconocida sale con error nombrando las opciones.
- Un token que comparte prefijo con una tag (`memori` → `memoria`) entra, pero
  con menos puntaje que el acierto exacto. Las tildes y las mayúsculas no
  impiden el match: `Auditoría` encuentra `auditoria`.
- Los stopwords no puntúan: en "de la memoria", el `de` no compite con
  `memoria`. Los tokens repetidos tampoco.
- Las tags con guion se matchean enteras: `search "HU-04"` encuentra
  `04_user_stories/HU-04/`.
- `search` ve lo que el índice dice, no lo que hay en disco: un documento nuevo
  no aparece hasta que se reindexa, y `indice_al_dia` avisa.
- `indice_al_dia` pasa en verde con el índice regenerado; al tocar un documento
  de Capa 1 sin reindexar pasa a **warn** nombrando el documento más nuevo, y
  `process check` sigue saliendo con 0 (D7).
- Un cambio en el logbook o en `project_state.md` **no** pone el índice viejo.
- La fila del índice y su parser son inversos exactos: lo que `memory index`
  escribe, `search` lo lee igual.
- Batería completa en verde: `pytest`, `ruff check src tests`, `mypy src`.
