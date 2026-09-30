# HU-15 — Contador de HUs verificable: el número que dispara la auditoría deja de ser una afirmación

> Cierre de D-01, la deuda transversal de la auditoría del 2026-09-29. No es una fase: es
> el agujero que dejó la fase 9 al convertir el alcance en tabla y dejar el contador, que
> era lo que la disparaba, en un número que nadie verificaba.

## Qué hay que construir

- `core/audit.py` (D1): `derived_closed_hus()` cuenta las HUs que el disco tiene y el
  reporte que selló tiene la fila vacía, y devuelve `None` cuando no hay ese reporte. El
  derivado no lee `docs/project_state.md`: cuenta directorios `HU-*` contra
  `parse_verdicts()`, así que el desfase entre lo declarado y lo real es medible sin que
  nadie lo afirme.
- `contador_hus_al_dia` como check de **Suk** (Capa 4), junto a `auditoria_completa` en
  `run_suk()`: `warn` cuando lo declarado queda por debajo de lo derivado, nunca `fail`.
  Los dos checks miden cosas distintas y no se reemplazan: `auditoria_completa` pregunta
  si el reporte más reciente tiene veredicto para cada HU; este pregunta si el
  que decide el umbral todavía cuenta lo que el disco tiene.
- `logsayer audit status` muestra el derivado y, si hay desvase, lo dice. El veredicto
  del umbral sigue siendo el del contador declarado: el derivado informa, no corrige.

### Decisiones tomadas en esta HU

1. **El derivado se apoya en `sealed_audit()`, no en `last_audit()`.** El contador
   significa "HUs cerradas desde la última auditoría", y lo que cuenta como auditoría es
   el reporte que opinó, no el andamiaje que `audit run` acaba de escribir. Consecuencia
   asumida: con la Decidora a medio llenar, el derivado sobrecuenta y el aviso nombra HUs
   que se están auditando en ese momento, un estado que `auditoria_completa` ya está
   avisando con nombre y apellido.
2. **Sin auditoría sellada no se mide; no es "cero".** `None` es la ausencia del
   denominador, no un número. Sin reporte con worklist no hay auditoría de la que "desde"
   medir, y los reportes anteriores a la fase 9 dicen cuáles HUs cubrieron en prosa, que
   es justo el parsing que la fase 9 elimina. La alternativa, contar todas las HUs del
   disco, daría un aviso permanente en todo proyecto con HUs que nunca se auditó; y un
   aviso permanente no avisa (el mismo criterio que D19 aplicó a `indice_al_dia`).
3. **La dirección del aviso es una sola.** Se avisa cuando lo declarado **subestima**,
   que es el fallo que retrasa la auditoría. Un contador que declara más de lo que hay en
   disco es el caso benigno, una HU borrada o un número redondeado hacia arriba, y avisos
   de eso enseñarían a ignorar el check entero.
4. **`warn`, no `fail`** (D7). Corregir el contador es escribir prosa en el snapshot;
   bloquear el flujo obligaría a hacerlo antes de poder trabajar.
5. **El umbral sigue siendo del declarado.** Mover el gate de `audit status` al derivado
   cerraría el hueco de punta a punta, pero cambia cuándo se propone auditar en un comando
   ya publicado, y esa es una decisión de umbral, no una corrección de un número. El check
   y la línea de desvase hacen visible el problema; mover el umbral es otro cambio, con
   su propio costo.

## Cómo se valida

- Un proyecto con reporte sellado, HUs cubiertas y contador declarado igual al derivado
  da **ok** en `contador_hus_al_dia`, con el par de números en el detalle.
- Con el contador declarado por debajo del derivado da **warn**, nombrando las HUs sin
  veredicto y el reporte del que se derivan, y el `check` igual sale con 0.
- Declarado por encima del derivado **no avisa**: es el caso benigno de la decisión 3.
- Sin ninguna auditoría sellada (nunca auditado, o con un reporte en prosa) el check da
  **ok** diciendo que no se mide, y no cuenta las HUs del disco como pendientes.
- Un andamiaje scaffoldeado con todas las filas vacías no rompe el sello: el derivado
  sigue apuntando al reporte anterior, aunque el andamiaje sea más reciente.
- `sin cambios` cuenta como veredicto: una HU heredada está cubierta.
- `logsayer audit status` imprime el derivado con el reporte del que sale, avisa el
  desvase, y su veredicto de umbral sigue siendo el del contador declarado.
- `contador_hus_al_dia` aparece en la lista de `run_suk()` / `logsayer check`.
- Batería completa en verde: `pytest`, `ruff check src tests`, `mypy src`.
