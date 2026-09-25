# Decisiones técnicas — logsayer

Fecha: 2026-09-25 · Estado: vigente

## Resumen

Registro vivo de las decisiones de arquitectura activas. Cada una tiene su porqué en la
bitácora; acá queda solo la referencia y su estado.

Registro de las decisiones de arquitectura activas. Cada una tiene su porqué (entrada de logbook en su momento); acá solo la referencia viva.

## D1. Un motor único + adaptadores finos (spec §6)

Toda la lógica vive en `logsayer/core/` y `cli.py`. Los archivos generados por `agent add` son wrappers finos que llaman al CLI — agregar un agente nuevo no duplica lógica. *Referencia: bitácora fase 3.*

## D2. Alias plano como puerta de entrada (spec §13)

`logsayer audit run` ≡ `logsayer truthsayer audit run`. El lore Dune da identidad pero nunca debe ser la única puerta de entrada a la funcionalidad.

## D3. Template mínimo por HU (spec §10)

Un solo `README.md` por HU con "Qué hay que construir" + "Cómo se valida". Nada de documentos de cientos de líneas por defecto (anti "sea of markdown").

## D4. `init --here` en modo adopt (spec §5)

`logsayer init --here` scaffoldea sobre un proyecto existente: crea lo que falta y **no sobrescribe** archivos ya presentes (AGENTS.md, logsayer.toml, estado, índice). Cerrado en el dogfooding del propio repo (fase del marco de sesiones).

## D5. Audit semántico honesto (spec §10)

El CLI genera estructura + prompt; el resultado lo produce un subagente. No se promete determinismo: se documenta. La responsabilidad es generar la estructura del reporte y el prompt, no el veredicto.

## D6. `inbox/` es staging, no una capa (spec §3)

La bandeja vive fuera de `docs/` y a propósito: no es Capa 1 ni ninguna otra. Razones: (a) sus archivos son *fuentes* sin jerarquía editorial, no documentos del proyecto; (b) el contenido se ignora en Git para no versionar material de terceros; (c) mezclarla con `docs/` haría que un `.pdf` sin procesar contamine el árbol documental. El derivado sí es Capa 1 y es lo único que se versiona. `logsayer check` escanea `docs/` únicamente.

## D7. Aviso ≠ fallo: el nivel `warn` (spec §4)

`CheckResult.status` pasó a ser `ok | warn | fail`. Un documento sin ubicar o un estado desactualizado no son errores de estructura: son pendientes que el humano debe ver pero que no deben cortar el flujo (`logsayer check` sale con 0). Solo `fail` bloquea. El motivo es operativo: si el pendiente bloqueara, la gente startaría a odiar el check y perderíamos la señal.

## D8. El CLI mueve y nombra; el agente deriva (spec §6)

El motor no redacta contenido ni convierte formatos. `doc new` scaffoldea el documento con su bloque `## Fuente` y archiva el original en `inbox/_done/`; el subagente Mentat es quien decide la capa y escribe el cuerpo. La responsabilidad del CLI es mecánica y verificable; la del agente requiere juicio.

## D9. Checks de Capa 1 como detectores de deuda (spec §4)

`header_capa1` y `estado_al_dia` se implementaron contra este mismo repo como prueba: fallaron el primer día contra documentos reales. Un check que nunca falla en el proyecto que lo dogfoodea es decorativo.

## D10. El CLI propone la capa, el subagente la decide (spec §3)

`doc route <archivo>` devuelve filas candidatas y decide solo con señal inequívoca: extensión no markdown, o una HU declarada en el nombre. La primera implementación clasificaba por palabras del nombre y, ante lo desconocido, devolvía `docs/02_technical/` por defecto. Se descartó: un `.md` de visión de producto terminado en la carpeta técnica sin que nadie lo notara es exactamente el tipo de error que el marco de 5 capas existe para evitar (spec §2). Además ahora detecta el reenvío de un documento que ya existe y avisa que no se duplique. *Discusión cerrada con el humano el 2026-09-25.*
