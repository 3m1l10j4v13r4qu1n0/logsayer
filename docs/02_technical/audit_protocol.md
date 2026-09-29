---
# Protocolo de auditoría por pasada: alcance del disco, pasada acotada, síntesis al final.
tags:
  - audit
  - protocolo
  - worklist
  - coverage
---

# Protocolo de auditoría

> Documento de Capa 1 — Especificación. Diseña la fase 9: el mecanismo por el cual la
> Decidora de Verdad audita por pasada sin que ninguna HU se pierda por omisión.

Fecha: 2026-09-29 · Estado: vigente

## Fuente

- Feedback de sesión sobre la auditoría del 2026-09-27, que cubrió HU-06..HU-09
  sobre las 11 HUs que había en disco.

## Resumen

El alcance de la auditoría lo cuenta el CLI como una tabla de filas, una por HU del
disco, y la Decidora llena celdas en vez de decidir qué filas existen. Cada HU se
audita en una pasada acotada a su input, y una síntesis al final lee solo los
veredictos. Un `warn` mecánico avisa si alguna fila quedó vacía.

## El problema

La auditoría del 2026-09-27 cerró cuatro HUs de once. No por un error de criterio:
el subgrafo decidió qué era auditable, y lo que no clasificó en el ranking se quedó
sin cubrir sin que nada lo signalara. El reporte era un documento plausible, los
checks estaban en verde, y el alcance real era otro.

Eso es un modo de falla silencioso, y es peor que un check en rojo: un check rojo te
dice que algo está mal; un reporte incompleto te dice que todo está bien.

La causa no es que la Decidora fuera perezosa, es que el alcance estaba **en prosa**.
Un alcance escrito en prosa no se puede verificar sin volver a interpretarlo con el
mismo criterio que produjo el hueco. Si no hay un artefacto mecánico, no hay forma
de distinguir "esa HU no estaba" de "se me olvidó esa HU".

## Qué establece

### 1. El alcance lo cuenta el CLI (D20)

`hu_ids()` enumera `docs/04_user_stories/HU-*/` y el reporte se scaffoldea con una
fila por HU. `parse_verdicts()` es el inverso exacto de `HuItem.row()`: el CLI
escribe la tabla y la relee igual, así que la cobertura se verifica parseando, no
interpretando.

El alcance no lo deduce ningún agente, y `docs/00_memory_index.md` no participa: es
un índice generado que puede estar viejo, y el artefacto de verdad es el disco.
D14 ya decía que el retrieval ordena por dónde empezar, nunca qué es auditable; acá
eso se vuelve una tabla.

Una tabla de filas tiene una propiedad que una lista en prosa no tiene: **el hueco
se ve en el `git diff` del reporte**. Agregaste una HU y la fila no aparece; eso es
revisable por un humano sin correr nada.

### 2. La pasada se acota a su input (D20)

Cada pasada recibe:

- el README de la HU;
- la base fija: `docs/01_global/mission.md` y `docs/project_state.md`;
- las rutas que la HU nombra entre backticks, deduplicadas, resueltas contra un
  catálogo de roots y reportadas si no existen.

Las citas son **directas**: los `## Fuente` de los documentos citados no se siguen.
Si se siguieran, el contexto volvería a crecer con el grafo y la pasada perdería su
cota, que es el problema que D14 ya señaló con el subgrafo.

Solo se parsean rutas entre backticks con extensión. Una HU que dice "la spec de
memoria" no aporta una cita: eso es interpretación, y el alcance es mecánico.

La base fija va siempre y las citas son mejora. Sin base fija, una HU sin citas
arrancaría ciega; con ella, una HU mal escrita sigue siendo auditable.

### 3. "Sin cambios" es una herencia condicionada (D21)

Una HU puede heredar su veredicto si y solo si:

- ya tenía veredicto en el reporte que selló;
- su README es anterior a ese reporte;
- ninguna ruta que cita cambió desde entonces.

Es herencia, no atajo: si tocaste lo que la HU cita, vuelve a auditarse. La
herencia existe para no re-litigar lo que ya se falló, no para silenciar cambios.

`docs/project_state.md` **no** invalida la herencia. Se reescribe en cada cierre de
sesión y contarlo invalidaría para siempre el veredicto de toda HU que lo menciona.
Es el mismo error que D19 corrige para `indice_al_dia`: el ritual de coordinación no
es requisito, y un aviso que aparece siempre deja de avisar (D7).

### 4. El reporte que se mide y el reporte que sella son distintos (D20)

`last_audit()` devuelve el más reciente: es el que la auditoría mide.
`sealed_audit()` devuelve el más reciente **con veredictos**: es el que sella la
herencia.

No pueden ser el mismo, y confundirlos rompe la herencia de una forma difícil de
ver: `audit run` scaffoldea un reporte vacío, ese andamiaje pasa a ser "el
previo", y una sola corrida borra todo lo que el trabajo anterior había ganado. Un
andamiaje no dice nada sobre la cobertura, así que no sella.

Un reporte **sin worklist** —los anteriores a esta fase, que listan las HUs en
prosa— tampoco sella ni se mide. Consecuencia asumida: el primer `audit run` de un
proyecto con historia re-audita todas sus HUs. No es una regresión, es el primer
reporte con alcance verificable, y la alternativa —interpretar prosa— reintroduce
el problema que esto existe para cerrar.

### 5. Una cita muerta o ambigua no hereda

Si la HU nombra una ruta que no existe en disco, o una que resuelve a más de un
archivo, el brief la muestra como tal y la HU no hereda el veredicto. Una HU que
apunta a algo que ya no existe tiene algo que decir, y heredarle el veredicto lo
taparía.

La ambigüedad no se resuelve al azar. `mentat.md.j2` existe en
`adapters/opencode/` y en `adapters/claude/`, y elegir el primer hit puede mandar a la
Decidora a auditar el archivo equivocado con toda confianza. Se reporta como ambigua
—con la instrucción de alcanzar la que corresponda— y no se resuelve.

### 6. La síntesis es el único momento de lectura cruzada, y es condicional

Después de las pasadas, y solo si algún veredicto cambió, se escribe la sección
**Sintesis entre HUs** leyendo únicamente la tabla de veredictos.

Que el input sea la tabla y no las HUs es lo que mantiene el aislamiento: si la
síntesis pudiera abrir HUs, sería una segunda pasada entera. Ante una contradicción
sospechada que ninguna pasada registró, la instrucción es nombrarla y pedir una
repasada acotada de esas HUs, no resolverla ahí. La síntesis detecta
contradicciones evidentes entre veredictos; una contradicción que ninguna pasada
individual registró, no la va a ver, y eso es el límite honesto del diseño.

### 7. Tres niveles de verificación, y quién resuelve cada uno

| Nivel | Quién | Qué es |
| --- | --- | --- |
| Estructura | `logsayer check`, `logsayer process check` | capas mezcladas, headers, índice fresco, bandeja |
| Comportamiento del código | `pytest`, `ruff check src tests`, `mypy src` | criterios de aceptación verificables por comando |
| **Veredicto** | **la Decidora** | si la implementación cumple lo que la HU dice, y si spec y código divergen |

La batería corre **una vez**, no por HU: derivarla por HU es trabajo mecánico
repetido. Y el nivel de veredicto es prosa —no es determinable por comando— y por
eso el resultado de la auditoría lo produce la Decidora y no el CLI. El CLI
scaffoldea; no opina.

### 8. `auditoria_completa` avisa, no bloquea

El check compara el alcance del disco contra las filas con veredicto del último
reporte. Es `warn`, nunca `fail`: un reporte a medio llenar es un estado legítimo
mientras la Decidora trabaja, y bloquearlo haría odiar el check (D7). El corte real
es el `--reset-counter`, que es decisión del humano.

Sin reporte previo, o con un reporte que no trae worklist, el check es `ok`: no se
mide cobertura con una métrica que el artefacto no adoptó.

### 9. `--hu` repite una pasada sin tocar el alcance

`logsayer audit run --hu HU-XX` reemite el brief de una sola HU, para repetir la
que falló. **No escribe reporte.** El alcance vive en la tabla; un reporte con una
sola fila se volvería `last_audit()` y dejaría al resto del alcance sin cubrir,
que es justo el fallo que este diseño cierra. Un brief es un artefacto
desechable, no un estado.

## Cómo se valida

- `logsayer audit run` genera exactamente una fila por directorio `HU-*` del disco.
- `parse_verdicts()` y `HuItem.row()` son inversos exactos; `—` y celda vacía no
  cuentan como veredicto.
- Una HU sellada, sin tocar, sale `sin cambios` con la fecha del reporte; tocar su
  README o lo que cita la manda a re-auditar; tocar `docs/project_state.md`, no.
- Un `audit run` con el reporte ya sellado y nada tocado conserva la herencia.
- Un reporte en prosa no se mide ni sella.
- Una HU con cita muerta o ambigua sale con la ruta en el brief, marcada como tal, y no hereda.
- Una cita que resuelve a más de un archivo se reporta ambigua en vez de elegir un hit.
- `logsayer check` con una fila vacía da `warn` nombrando la HU y sale con 0.
- `logsayer audit run --hu HU-01` escribe solo el `.prompt.md`, no cambia el conteo
  de reportes, y el prompt trae un único `### HU-`. Con una HU fuera de alcance,
  sale con error.
- Un `HU-XX/` sin README aparece en la tabla y no lanza excepción.
- Batería completa en verde: `pytest`, `ruff check src tests`, `mypy src`.
