# Prompts de bootstrap — logsayer (framework de 5 capas, edición Dune)

Adaptación del flujo de prompts original de Spec Kit, extendido para cubrir las 5 capas (el original solo cubre Especificación). Pensado para pegar directo en Claude Code, en orden, sesión por sesión. Usa el mismo patrón: `AskUserQuestion` agrupado, antes de escribir a disco.

Fuente de verdad: `logsayer_especificacion_maestra.md` — nombre, capas, estructura de `docs/`, umbrales, comandos y roadmap. El apéndice de rol Dune es la sección 13 de ese documento.

---

## 1. Creating the constitution (Capa 1 — Especificación / Mentat)

```
Estamos construyendo logsayer, un CLI open source en Python que scaffoldea
y coordina un sistema de 5 capas documentales para proyectos con agentes
IA: Especificación, Estado, Bitácora, Verificación (mecánica + semántica)
y Proceso. El tema narrativo usa personajes de Dune como metáfora de rol
(Mentat, Navegante, Reverenda Madre, Suk Doctor/Decidora de Verdad,
Fremen) — ver la sección 13 (apéndice lore) de
logsayer_especificacion_maestra.md para el mapeo completo.

Let's create a "constitution" in a specs directory:
- mission.md — qué resuelve el framework, por qué existe (diferencial vs
  GitHub Spec Kit: cierre del verification loop + continuidad de contexto
  entre sesiones), a quién apunta.
- tech-stack.md — Python 3.11+, Typer como CLI framework, Jinja2 para
  templates, TOML para config, empaquetado con pyproject.toml + hatchling,
  distribución vía PyPI (uv tool install / pipx).
- roadmap.md — fases de implementación en pasos chicos: Fase 0
  (definición — nombre logsayer ✅, manifiesto, schema de logsayer.toml);
  Fase 1 (MVP: comando init que scaffoldea docs/ + AGENTS.md, sin
  multi-agente); Fase 2 (comandos core: spec new, log add + partición
  automática, log index, audit run, audit status); Fase 3 (adaptadores
  multi-agente); Fase 4 (validación: doctor/check, detección de capas
  mezcladas); Fase 5 (documentación y publicación); Fase 6 (comunidad:
  presets, más agentes).

Important: You *must* use your AskUserQuestion tool, grouped on these 3,
before writing to disk.
```

---

## 2. Implementing features (Capa 1 — Especificación / Mentat)

Patrón para cada feature del propio CLI. La estructura de HUs está definida en la sección 3 de la especificación maestra (nombres de carpetas en inglés, contenido en español):

```
Find the next phase on the roadmap (sección 9 de
logsayer_especificacion_maestra.md) and make a branch, ask me about the
feature spec.

Create:
- A new directory docs/04_user_stories/HU-XX/ for this user story
- In there:
  - requirements.md for the scope, decisions, context
  - validation.md for how to know the implementation succeeded and can
    be merged

Refer to docs/01_global/ (visión, negocio) y docs/02_technical/
(decisiones técnicas) una vez scaffoldeados; mientras tanto, a
logsayer_especificacion_maestra.md.

Important: You must use your AskUserQuestion tool, grouped on these,
before writing to disk.
```

---

## 3. Cuándo cerrar sesión (Capa 2 — Estado / Navegante) — trigger por contexto

**No existe en el flujo original.** Se dispara solo, por señal de contexto — no hace falta que te acuerdes de pedirlo:

```
Si el uso de contexto de esta sesión (según /context o el indicador de la
statusline) supera el 70%, avisame antes de seguir con más tareas nuevas
y proponeme cerrar sesión (prompt 4 de este set) para no perder precisión
por degradación de contexto largo.
```

`logsayer.toml`: `session_close_context_threshold = 0.70`

---

## 4. Closing a session (Capa 2 — Estado / Navegante + Capa 3 — Bitácora / Reverenda Madre)

**Esto no existe en el flujo original — es la extensión que cierra el hueco.** Se corre al final de cada sesión de trabajo, después de que una feature (o parte de ella) quedó implementada, o cuando se dispara el trigger del prompt 3.

```
Cerrando la sesión. Actualizá el snapshot de estado y la bitácora:

1. Leé docs/project_state.md (si no existe, creálo con la estructura: fase
   actual del roadmap, últimas 3-5 decisiones activas, contador de HUs
   cerradas desde la última auditoría).
2. Actualizalo reflejando SOLO lo que cambió esta sesión — no dupliques
   contenido de specs/, no repitas el roadmap completo, es un snapshot, no
   un archivo. Mantenelo bajo ~2000 tokens.
3. Si hubo una decisión de diseño relevante (no un detalle de
   implementación menor), agregá una entrada en
   docs/logbooks/logbook_<fase>_NN.md (el archivo activo más reciente). Si
   ese archivo supera 400 líneas (~2.500-3.000 tokens), creá el siguiente
   NN y actualizá docs/logbooks/00_index.md.
4. Si esta sesión cerró una HU/feature completa, incrementá el contador
   de HUs cerradas desde la última auditoría en el estado.

Mostrame el diff de project_state.md y la entrada de bitácora ANTES de
escribir. Esperá mi aprobación explícita antes de guardar.
```

`logsayer.toml`:
```toml
bitacora_max_lines = 400
```

---

## 5. Auditoría periódica (Capa 4 — Verificación / Decidora de Verdad)

**Tampoco existe en el original.** Se dispara por **progreso del proyecto**, no por contexto de sesión — una sesión larga de debugging no amerita auditoría si no cerró ninguna HU. El agente lo propone apenas se cumple, no espera a que se lo pidan.

```
El contador de HUs cerradas desde la última auditoría es [N], y el umbral
configurado es 3. Toca auditoría.

Compará cada feature marcada como completa en docs/04_user_stories/HU-XX/
validation.md contra el código real en el repo. Para cada una:
- ¿El código cumple lo que validation.md dice que debe cumplir?
- ¿Hay código que dice implementar algo que en realidad no hace, o lo
  hace parcialmente?

No repares nada. Reportá solo discrepancias, con referencia al archivo de
spec y a la línea de código en cuestión.

Escribí el resultado en docs/06_audits/audit_<fecha>.md y reseteá el
contador en project_state.md — con mi aprobación antes de escribir.
```

`logsayer.toml`:
```toml
audit_threshold_hus = 3
```

---

## 6. Chequeo mecánico (Capa 4 — Verificación / Suk Doctor)

**Este no necesita prompt de razonamiento — es literalmente un bot.** Va como script en CI o pre-commit, no como prompt a un agente:

```bash
# .github/workflows/check.yml o pre-commit hook
pytest
ruff check .
logsayer suk doctor  # valida estructura de docs/ (alias: logsayer check)
```

---

## `logsayer.toml` consolidado (los 3 valores resueltos)

```toml
[logsayer]
session_close_context_threshold = 0.70   # % de contexto usado para proponer cierre de sesión
bitacora_max_lines = 400                 # líneas por archivo atómico de bitácora antes de particionar
audit_threshold_hus = 3                  # HUs cerradas desde la última auditoría para disparar audit
```

---

## Nota sobre por qué esta extensión importa

El flujo original (prompts 1 y 2) es exactamente el patrón de Spec Kit — spec-first, sólido para la primera generación de código. Pero sin los prompts 3 y 4, el bootstrap del framework tendría el mismo defecto que veníamos señalando en Spec Kit: nadie fuerza que el `project_state.md` se actualice, y nadie audita si el código de `logsayer init` sigue haciendo lo que `validation.md` de esa feature decía. Al usar los 4 prompts en conjunto, el propio bootstrap del CLI ya "come su propia comida" desde el commit número uno.