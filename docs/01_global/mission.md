# Misión y alcance — logsayer

**Mensaje de una línea:** *Spec Kit te dice qué construir. logsayer te dice dónde estás parado, cómo llegaste, y si lo que construiste sigue siendo lo que dijiste que ibas a construir.*

## Problema

Spec Kit y el patrón spec-driven gobiernan la primera generación de código; después, su autoridad sobre el código es por convención, no por verificación. Además, los agentes de IA no tienen memoria persistente entre sesiones: cada sesión arranca sin saber dónde está parado el proyecto ni por qué se tomaron decisiones pasadas.

## Qué resuelve logsayer

1. **Continuidad de estado entre sesiones** — snapshot ancla (`project_state.md`) que el agente lee al arrancar y que se sobrescribe al cerrar, con aprobación previa.
2. **Bitácora histórica particionable** — el "por qué" de las decisiones, en append-only, con índice y partición automática por tamaño.
3. **Verificación continua** — mecánica (estructura, no mezcla de capas) y semántica (lo construido sigue siendo lo especificado).
4. **Coordinación multi-agente** — un motor único + adaptadores finos por herramienta, con `AGENTS.md` como punto de coordinación universal.

## Alcance (qué no es)

- No es un ORM de documentación ni genera documentos de cientos de líneas por defecto: produce el mínimo indispensable (spec §10).
- El resultado del audit semántico no es determinístico: lo produce un subagente a partir de la estructura y el prompt que genera el CLI (spec §10).