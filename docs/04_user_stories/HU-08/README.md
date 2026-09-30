# HU-08 — Onboarding de documentos entrantes (README y ejemplo real)

> Fase 6 del roadmap. Cierra F5 y responde la pregunta que nadie tiene
> resuelta: "tengo un `.md` nuevo en la raíz, ¿qué hace logsayer con él?".

## Qué hay que construir

- Sección **Incoming documents** en el `README.md` (en inglés, como el resto de
  la superficie pública), con la respuesta literal: hoy un archivo en la raíz no
  lo ve nadie; la zona declarada es `inbox/`.
- La tabla "¿dónde va mi documento?" en el README, coherente con
  `core/routing.py` (mismas filas y mismo comando por fila).
- Transcript real en `examples/hello-logsayer/README.md` con la salida verdadera
  de `inbox add` → `check` → `doc route` → `doc new`, en el mismo estilo del
  ejemplo existente.
- Mención de `inbox_max_age_days` en la sección de configuración del README.
- Corrección de `README.md:119`, que declara la fase 5 como actual mientras el
  repo ya cerró 0-5 (drift entre capa y realidad, el mismo F7 que reporta el
  feedback).

## Cómo se valida

- Las filas de la tabla del README coinciden con las de `core/routing.py`: un
  test compara ambas (el README no puede drift-ear del core).
- El ejemplo del transcript se genera corriendo los comandos, no a mano.
- Los comandos citados en el README existen (`--help` los lista).
