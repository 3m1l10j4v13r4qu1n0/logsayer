# HU-13 — Pasada por HU y síntesis: `--hu`, briefs acotados y la Decidora en el prompt

> Fase 9 (auditoría por pasada) — segunda mitad. Diseño: `docs/02_technical/audit_protocol.md`.
> HU-12 dejó el alcance medible; acá se acotá cada pasada y se cierra la auditoría.

## Qué hay que construir

- `HuItem.brief()` (D1): el input de **una** pasada — el README de la HU, la
  base fija (`docs/01_global/mission.md` + `project_state.md`) y las rutas que cita, con las
  muertas a la vista. Es lo que hace que auditar sea re-ejecutable.
- `logsayer audit run --hu HU-XX`: reemite el brief de una sola pasada, para
  repetir la que falló. **No escribe reporte.**
- El prompt de auditoría con una sección por HU y un cierre de síntesis. Las
  filas con `sin cambios` ya vienen resueltas y el prompt dice que no se
  re-auditen.
- Los adaptadores de **Truthsayer** (opencode y claude) con el bucle de pasadas
  y el momento de síntesis escrito en su prompt.

### Decisiones tomadas en esta HU

1. **`--hu` no escribe reporte, y no es un detalle.** El alcance vive en la
   tabla. Un reporte con una sola fila se volvería `last_audit()` y dejaría al
   resto del alcance sin cubrir, que es el fallo que D14 existe para cerrar: la
   herencia del andamiaje se pierde y `auditoria_completa` mediría un alcance
   de 1. Un brief es un artefacto desechable, no un estado. Por eso el nombre
   lleva `.prompt.md`, que `_latest()` ya excluía del realm de reportes.
2. **La base fija va siempre, las citas son mejora.** Sin `docs/01_global/mission.md` y
   `project_state.md`, una HU sin citas arrancaría ciega; con ellas, la
   extracción de citas es una mejora y no un requisito. Una HU que no cita nada
   es normal y el brief lo dice, para que la Decidora no la salte.
3. **La síntesis es el único momento de lectura cruzada, y es condicional.** Se
   dispara solo si algún veredicto cambió en la corrida. El input es la tabla de
   veredictos y nada más: si la Decidora puede abrir HUs para sintetizar, la
   síntesis se convierte en una segunda pasada entera y el aislamiento se
   pierde. Ante una contradicción sospechada pero no registrada por ninguna
   pasada, la instrucción es nombrarla y pedir una repasada acotada — no
   resolverla ahí.
4. **El prompt nombra los tres niveles de verificación y quién resuelve cada
   uno.** Checks estructurales, batería de código (`pytest`/`ruff`/`mypy`) una
   sola vez, y veredicto semántico. Sin esa separación, la Decidora deriva por
   HU una batería que es mecánica, y el nivel de veredicto queda mezclado con lo
   que un comando ya responde. Ese nivel es prosa: no es determinable por
   comando, y por eso el resultado lo produce ella.
5. **Las filas heredadas no se re-auditan.** Decirlo en el prompt evita que la
   Decidora gaste el contexto en una HU que el CLI ya resolvió, que es el modo
   natural de re-litigar un veredicto sin motivo.
6. **El cierre exige `auditoria_completa` en verde antes del reset.** El
   `--reset-counter` es la decisión humana que la fase 9 no automatiza: el
   check avisa, el humano aprueba.

### Lo que explícitamente NO se hace

- **No hay subagente por HU.** La Decidora es un rol y las pasadas las ejecuta
  el agente orquestador: el aislamiento de contexto es de la pasada, no de un
  proceso aparte.
- **No se auditan HUs fuera de `docs/04_user_stories/HU-*/`.** El alcance es el
  disco; `memory search` ordena por dónde empezar, nunca qué es auditable.
- **No se automatiza el veredicto.** Ninguna heurística decide `cumple` /
  `parcial` / `no cumple`: la batería cubre lo verificable por comando y el
  resto es juicio de la Decidora.
- **No se escribe en el reporte desde el CLI después de scaffoldearlo.** La
  tabla la llena la Decidora; el CLI no opina encima.

## Cómo se valida

- El prompt de `audit run` trae una sección por HU, y cada una lista el README,
  la base fija y las rutas citadas de esa HU.
- Las filas con `sin cambios` salen con esa etiqueta y el prompt dice explícitamente
  que no se re-auditen.
- Una HU sin citas sale con la línea "Rutas citadas: ninguna" y la pasada se
  emite igual: la base fija la sostiene.
- Una HU que cita una ruta inexistente la nombra como tal en su brief, sin
  adivinar a qué archivo se refiere.
- `logsayer audit run --hu HU-01` escribe solo el `.prompt.md` con esa HU, deja
  el conteo de reportes igual, y el prompt de esa pasada trae un único `### HU-`.
- `logsayer audit run --hu HU-99` sale con error nombrando que no está en el
  alcance de `docs/04_user_stories/`.
- El prompt separa los tres niveles y le dice a la Decidora que corra la batería
  **una vez**, no por HU.
- El cierre de la síntesis nombra las HUs involucradas en una contradicción en
  vez de resolverla.
- Los prompts de Truthsayer (opencode y claude) describen el bucle de pasadas,
  el `--hu` de repetición y el momento de la síntesis.
- Batería completa en verde: `pytest`, `ruff check src tests`, `mypy src`.
