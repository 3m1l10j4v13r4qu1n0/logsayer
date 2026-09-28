---
tags:
  - memoria
  - retrieval
---
# Arquitectura de memoria

> Documento de Capa 1 — Especificación. Completa solo lo indispensable (spec §10).

Fecha: 2026-09-28 · Estado: vigente

## Resumen

Define cómo el agente navega la memoria del proyecto sin leerla entera: un índice
generado mecánicamente (`docs/00_memory_index.md`) más un motor de retrieval
determinista en Python. El grafo es una **capa transversal de navegación** (D12), no
una sexta capa: no reemplaza las 5 capas, las indexa.

## Fuente

- Origen: `inbox/_done/feelback_agente_grafo_memoria_motor_memoria_2026_09_28.md` (recibido el 2026-09-28)
- Adaptação: el documento de origen propone 13 fases de roadmap y un índice en la raíz
  de `docs/`. Se corrigieron tres premisas suyas; ver "Lo que no se toma".

## Qué establece

### Tesis

> Los metadatos sirven para navegar la memoria; el contenido sirve para razonar
> sobre la memoria.

El beneficio no es "los metadatos son baratos" en abstracto, sino que habilitan una
**preselección mecánica antes de cargar contenido al modelo**. Sin esa preselección,
el frontmatter es decoración.

### Componentes

```
DOCUMENTOS  ──parse──▶  METADATOS  ──▶  ÍNDICE  ──▶  RETRIEVER  ──▶  CONTEXTO
 (Capa 1)              (frontmatter)   (generado)   (determinista)
```

1. **Metadatos** — frontmatter por documento. Contrato mínimo, ver abajo.
2. **Índice** — `docs/00_memory_index.md`, generado por `logsayer memory index`.
   Un `.md` por documento, una línea por documento. Es un artefacto: se regenera, no
   se edita.
3. **Retriever** — `logsayer memory search "<consulta>"`. Tokeniza la consulta,
   intersecta con las tags, ordena y corta. Sin LLM y sin embeddings.
4. **Contexto** — lo que el agente lee primero. El contenido completo se recupera
   después, solo de los documentos seleccionados.
5. **Frescura** — check `indice_al_dia` (Capa 5 — Fremen): el índice no puede ser más
   viejo que el documento más reciente que indexa. Reusa el patrón de
   `estado_al_dia` (HU-09), que compara el máximo entre `git log -1` y mtime.

### Contrato de frontmatter

```yaml
---
tags:
  - memoria
  - retrieval
---
```

**Un solo campo: `tags`.** Es el único que consume un comando (`memory search`).
La regla que decide cualquier campo futuro (D13):

> Un campo entra al frontmatter solo si algún comando lo lee mecánicamente.

Por eso no entra:

| Campo propuesto | Por qué no |
|---|---|
| `id` | ya está en la ruta (`HU-XX/`, nombre del archivo) |
| `capa` | implícita en el directorio (`01_global/`, `02_technical/`, …) |
| `nivel` | implícito en la ruta: `01_global` nivel 0, `02_technical` nivel 1, `HU-XX` nivel 2 |
| `estado` | ya está en el header estándar, y `header_capa1` lo valida |
| `peso` | lo escribiría un LLM y se pudre; el ranking se deriva, no se declara |
| `relaciones` | maintenance manual garantizada; solo se conservan las que el CLI puede verificar (`## Fuente`) |

Duplicar en el frontmatter lo que la ruta ya dice crea dos verdades que divergen. El
primer día que `nivel` y la ruta no coincidan, nadie sabe cuál manda.

### Origen de las tags

Derivadas mecánicamente en la primera indexación, sin intervención de LLM: tokens del
nombre `snake_case` del archivo + identificador de la HU referenciada en `## Fuente`.
El **Mentat** puede refinararlas al editar el documento, pero no tiene la obligación de
mantenerlas: si faltan, el índice sigue siendo correcto.

### Formato del índice

```markdown
# Índice de memoria

<!-- Generado por 'logsayer memory index'. No editar a mano. -->

01_global/mission.md                              · nivel 0 · vigente · 2026-09-24
02_technical/memory_architecture.md               · nivel 1 · vigente · 2026-09-28 · memoria, retrieval
04_user_stories/HU-09/README.md                   · nivel 2 · vigente · 2026-09-27 · checks, capa-1
```

La implementación (HU-10) cierra tres detalles que el ejemplo deja abiertos:

- **Orden:** por `(nivel, ruta)`. Es lo que hace que las líneas se lean como capas
  y no como un `ls`.
- **Metadata ausente:** `—`. Las capas de proceso, metodología, auditoría y
  bitácora no llevan el header estándar, y el índice no inventa un estado para
  ellas.
- **Nivel de las capas no enumeradas:** `03_process/`, `05_agile_methodology/`,
  `06_audits/` y `logbooks/` son **nivel 3**. La numeración es "distancia a la
  especificación", y esas capas no compiten por ser la fuente de verdad de una
  HU. El nivel nunca se escribe en el documento: se deriva de la ruta.

Este documento declara su propio frontmatter porque la CLI lo scaffoldea y el
Mentat lo ajusta (D8): es el ejemplo ejecutable del contrato, no una excepción
a él.

### Comandos

```bash
logsayer memory index                              # regenera el índice      (HU-10)
logsayer memory status                             # qué indexa, con cuántas tags (HU-10)
logsayer memory search "checks de capa 1"          # candidatos ordenados     (HU-11)
logsayer memory search "inbox" --capa technical    # con filtro de capa       (HU-11)
```

Ambos con su alias de rol: `logsayer memory ...` ≡ el subagente que los consume
(`index` y `status` cuelgan del Navegante; `search`, en HU-11, lo consumen
Mentat y Truthsayer). `status` no dictamina frescura —eso es `indice_al_dia` en
HU-11—: informa qué hay.

### Reparto por capa y subagente

| Pieza | Dueño | Naturaleza |
|---|---|---|
| `core/memory.py` + `memory index` / `search` | CLI | Mecánico, testeado, en `core/` (D1) |
| Frontmatter en las plantillas | CLI scaffoldea, Mentat completa | Híbrido (D8) |
| `docs/00_memory_index.md` | CLI genera | Artefacto; nadie lo edita a mano |
| Indexar y linkear documentos de Capa 1 | **Mentat** | Consume `search` para ubicar |
| Nodo raíz del grafo | **Navegante** | `docs/project_state.md` es nivel 0 |
| Registrar la decisión de adoptar el grafo | **Reverenda Madre** | `logsayer log add`; no crea documentos de Capa 1 |
| Contexto barato de auditoría | **Truthsayer** | Usa `search` para arrancar |
| `indice_al_dia` | **Fremen** | Verificación mecánica |

La **Reverenda Madre** no crea los documentos con el frontmatter: es Capa 3 y su
alcance es la bitácora append-only (`templates/adapters/opencode/reverend-mother.md.j2`).
El scaffoldeo lo hace el CLI y el cuerpo lo escribe el **Mentat** (D8). Lo que sí le
corresponde es registrar la decisión.

### Garantía de alcance (D14)

> El retrieval elige **qué leer primero**, nunca **qué es auditable**.

Si el subgrafo deja afuera un documento relevante, la auditoría pasa por omisión y el
marco miente. Por eso la Truthsayer usa `search` para **ordenar su arranque**, pero el
alcance de la auditoría sigue siendo `docs/04_user_stories/` completo. El índice es un
atajo de lectura, no un recorte de alcance.

### Lo que no se toma

1. **Búsqueda semántica y embeddings.** Agrega dependencia, costo y no-determinismo.
   El origen lo propone como evolución posterior; queda fuera.
2. **`MemoryNode` / `MemoryEdge` / `MemoryGraph` como clases.** Sobreingeniería
   prematura: arranca con funciones puras sobre el índice.
3. **Índice en la raíz de `docs/` sin exención.** El origen propone
   `docs/00_memory_index.md` sin advertir que dispara **fail** en `capas_mezcladas`:
   el check recorre `docs/**/*.md` y solo exime las capas más el estado
   (`check_mixed_layers`, en `src/logsayer/core/suk.py`). Se agrega la exención,
   con el mismo patrón que ya exime `project_state.md`.
4. **13 fases de roadmap.** El origen numera las fases contra un README viejo (su fase 6
   es "presets y nuevos agentes", cuando la 6 real es ingreso de documentos). Acá es
   **una** fase — la 8, después de la 7 (comunidad) — desglosada en dos HUs.
5. **Pesos y niveles declarados a mano.** Ver "Contrato de frontmatter".

## Cómo se valida

- `logsayer memory index` sobre este repo produce un índice con una línea por documento
  de `docs/`, sin ninguno de más y sin ninguno de menos.
- `logsayer memory search "motor de memoria"` rankea `02_technical/memory_architecture.md`
  por encima de documentos sin relación, y `memory search` con `--capa` nunca devuelve
  documentos de otra capa.
- `indice_al_dia` pasa en verde con el índice regenerado; al tocar un documento de Capa 1
  sin reindexar, el check pasa a **warn** nombrando el documento más nuevo (no bloquea,
  D7).
- El índice sobrevive a un `doc new`: el documento scaffoldeado entra al reindexar sin
  metadata escrita a mano.
- `logsayer check` y `logsayer process check` siguen en verde con el índice presente.
- Batería completa en verde: `pytest`, `ruff check src tests`, `mypy src`.

## HUs

| HU | Alcance |
|---|---|
| HU-10 | Frontmatter `tags` en `doc.md.j2` + `docs/00_memory_index.md` + `memory index` / `memory status` + exención en `capas_mezcladas` + `header_capa1` tolerante del frontmatter |
| HU-11 | `memory search` + `indice_al_dia` + la Decidora lo consume |
