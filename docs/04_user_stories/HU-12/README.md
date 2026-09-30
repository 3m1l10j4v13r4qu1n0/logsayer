# HU-12 — Alcance mecánico de auditoría: tabla de ítems y check de cobertura

> Fase 9 (auditoría por pasada) — primera mitad. Diseño: `docs/02_technical/audit_protocol.md`.
> HU-12 deja el alcance medible; HU-13 agrega la pasada por HU y la síntesis.

## Qué hay que construir

- `core/audit.py` (D1): `hu_ids()` enumera `docs/04_user_stories/HU-*/` y
  `hu_worklist()` arma un `HuItem` por HU. El reporte se scaffoldea con una
  fila por HU, y `parse_verdicts()` es el **inverso exacto** de `HuItem.row()`:
  el CLI escribe la tabla y la relee igual, así que el check mide cobertura real
  y no formato Kerberos.
- `cited_paths()`: extrae del README las rutas entre backticks, deduplica,
  resuelve contra un catálogo de roots (`src/logsayer/`, `docs/`, …) porque una
  HU escribe `core/audit.py`, no la ruta completa, y devuelve las que no
  existen para reportarlas en vez de adivinarlas.
- `auditoria_completa` como check de **Suk** (Capa 4): la auditoría cubrió cada
  HU que el disco tiene. `warn`, nunca `fail`.
- Herencia condicionada: `sealed_audit()` + `_Seal` conceden `sin cambios` solo
  si la HU ya tenía veredicto, su README es anterior al reporte que selló, y
  ninguna ruta que cita cambió desde entonces.

### Decisiones tomadas en esta HU

1. **El alcance lo cuenta el CLI, no lo elige la Decidora.** Una tabla de filas
   es diffeable sin LLM: el hueco se ve en el `git diff` del reporte. Si las
   filas las escribiera el agente, "se olvidó de una HU" sería indistinguible de
   "no había esa HU", que es exactamente el modo de falla silencioso que D14
   cierra.
2. **`sealed_audit()` y `last_audit()` son preguntas distintas.** El reporte que
   se **mide** es el más reciente; el reporte que **sella** es el más reciente
   con veredictos. No pueden ser el mismo: `audit run` scaffoldea un reporte
   vacío, y si ese andamiaje fuera "el previo", una sola corrida borraría toda
   la herencia que el trabajo anterior había ganado. Un andamiaje no dice nada
   sobre la cobertura, así que no sella.
3. **Un reporte sin worklist no se mide y no sella.** Los anteriores a la fase 9
   listan las HUs en prosa; leer prosa para decidir qué está cubierto es
   justamente el parsing que la fase 9 elimina. Sin herencia y a re-auditar: la
   respuesta conservadora ante un artefacto de formato desconocido. Por eso el
   primer `audit run` de este repo re-audita las 13 HUs, aunque la del 2026-09-27
   haya cubierto cuatro. No es una regresión: es el primer reporte con alcance
   verificable.
4. **`docs/project_state.md` no invalida la herencia** (`NON_SPEC_CITATIONS`,
   D21). Se reescribe en cada cierre de sesión; contarlo invalidaría para
   siempre el veredicto de toda HU que lo menciona. Es el mismo error que D19
   corrige para `indice_al_dia`: el ritual de coordinación no es requisito.
5. **Una cita muerta o ambigua bloquea la herencia.** El CLI la reporta en el
   brief y `sin cambios` no se concede: una HU que apunta a un archivo que ya no
   existe tiene algo que decir, y heredarle el veredicto lo taparía. La ambigua
   tampoco se resuelve al azar — `mentat.md.j2` está en `adapters/opencode/` y en
   `adapters/claude/`, y elegir el primer hit puede mandar a la Decidora al
   archivo equivocado con toda confianza.
6. **`auditoria_completa` es `warn`.** Un reporte a medio llenar es un estado
   legítimo mientras la Decidora trabaja; bloquearlo haría odiar el check (D7).
   El corte real es el reset del contador, que es decisión del humano.
7. **Las rutas del brief son relativas a la raíz.** Una ruta absoluta ata el
   prompt a la máquina donde se generó, y la Decidora no necesita saber dónde
   está el repo para leer un archivo.
8. **Un directorio `HU-XX/` sin README no rompe nada.** El directorio existe y
   por eso está en el alcance, con su hueco adentro: `cited_paths()` tolera el
   archivo ausente y el brief avisa que no hay spec que auditar.

### Lo que explícitamente NO se hace

- **No se sigue el grafo de citas.** Los `## Fuente` de los documentos citados
  no se abren: si se sigieran, el contexto volvería a crecer con el grafo y la
  pasada perdería su cota.
- **No se matchea prosa.** Solo rutas entre backticks con extensión. "la spec de
  memoria" es interpretación, y el índice es mecánico.
- **No se parsean los reportes en prosa** para extraer cobertura. Ver decisión 3.
- **No se regenera ni se reescribe un reporte previo.** La auditoría es un
  artefacto sellado; el CLI solo scaffoldea.
- **No hay pasada por HU ni síntesis todavía**: son HU-13. Acá el alcance es
  una lista de filas.

## Cómo se valida

- `logsayer audit run` sobre un proyecto con HUs genera un reporte con
  exactamente una fila por directorio `HU-*` del disco, aunque
  `docs/00_memory_index.md` mencione HUs que no existen.
- `parse_verdicts` y `HuItem.row()` son inversos: lo que el CLI escribe, el
  check lo relee. Un placeholder `—` o una celda vacía no cuentan como
  veredicto.
- Una HU con veredicto en el reporte que selló, README y citas sin tocar, sale
  con `sin cambios` y la fecha del reporte. Tocar el README la manda a
  re-auditar; tocar lo que cita, también; tocar `docs/project_state.md`, no.
- Un `audit run` con el reporte ya sellado y nada tocado **conserva** la
  herencia en vez de perderla.
- Un reporte en prosa no se mide ni sella: `auditoria_completa` dice que es
  anterior al worklist y la HU queda en `re-auditar`.
- Una HU que cita una ruta inexistente sale con esa ruta en el brief y no
  hereda.
- `logsayer check` con una fila vacía da **warn** nombrando la HU, y el check
  igual sale con 0.
- Un `HU-XX/` sin README aparece en la tabla, con la ausencia de spec en el
  brief, y no lanza excepción.
- Batería completa en verde: `pytest`, `ruff check src tests`, `mypy src`.
