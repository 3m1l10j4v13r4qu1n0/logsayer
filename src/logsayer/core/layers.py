"""Taxonomía de capas de `docs/` (spec §2).

Existe para que no haya tres copias de la misma lista: el Suk chequea estructura
con ella, el índice de memoria le asigna nivel y `--capa` valida contra ella.
Cuando una capa se agrega en un lugar y se olvida en otro, `capas_mezcladas` y
`memory search` empiezan a discrepar sin que ningún test lo note — que es
justo lo que pasó con la sexta capa que la fase 8 descartó.

El *nivel* de cada capa no vive acá: es una lectura del índice de memoria
(distancia a la especificación, D15) y lo define `core.memory`.
"""

from __future__ import annotations

GLOBAL = "01_global"
TECHNICAL = "02_technical"
PROCESS = "03_process"
STORIES = "04_user_stories"
AGILE = "05_agile_methodology"
AUDITS = "06_audits"
LOGBOOKS = "logbooks"

# Orden de presentación: el mismo en el índice, en `check` y en la bitácora.
ALL: tuple[str, ...] = (GLOBAL, TECHNICAL, PROCESS, STORIES, AGILE, AUDITS, LOGBOOKS)
