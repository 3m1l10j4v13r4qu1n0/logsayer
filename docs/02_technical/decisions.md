# Decisiones técnicas — logsayer

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