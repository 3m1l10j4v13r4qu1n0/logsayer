# HU-17 — Adaptador de GitHub Copilot (cierre de la fase 3)

> Cierra D-07: el último adaptador de la fase 3. D26 decidió que sea **uno solo**
> (Copilot) y no los cuatro que el registro enumeraba. La convención nativa se
> verificó contra la documentación oficial de GitHub antes de escribir una línea:
> perfil en `.github/agents/<rol>.agent.md` con `description` + `tools`, e
> instrucción en `.github/instructions/**/<rol>.instructions.md` con `applyTo` +
> `excludeAgent`.

## Qué hay que construir

- `src/logsayer/adapters/copilot.py`: `copilot_spec` con **ocho** archivos, dos por
  rol. El perfil declara quién es el rol y qué herramientas tiene; la instrucción
  declara en qué rutas aplica. Con un archivo solo, los cuatro prompts llegarían a
  todos los contextos del repo.
- Registro: `copilot` entra a `REGISTRY` y sale de `NOT_YET_IMPLEMENTED` (que queda
  con `cursor`, `gemini`, `hermes`).
- Ocho templates: `templates/adapters/copilot/<rol>.agent.md.j2` y
  `templates/adapters/copilot/instructions/<rol>.instructions.md.j2`, con los mismos
  roles y la misma prosa operativa de los otros adaptadores.
- **No** se genera `.github/copilot-instructions.md`: Copilot consume `AGENTS.md`
  nativamente y el archivo sería una segunda fuente de verdad (D37).
- Help de `logsayer agent add`: `(opencode | claude | copilot)`.

## Superficie declarada (D24, verificado contra la doc oficial)

- `description` es el único campo requerido. `tools:` usa los alias canónicos
  (`read`, `search`, `edit`, `execute`), porque un alias desconocido se ignora en
  silencio.
- Se omiten `argument-hint` y `handoffs` (la doc los declara ignorados en
  GitHub.com), `infer` (retirada) y `target` (existe, pero sin valor se aplica a
  ambos entornos: fijarlo reduciría el alcance). `name` se omite porque duplica el
  nombre del archivo.
- **Copilot no declara permisos por ruta.** `applyTo` filtra dónde se inyecta la
  instrucción, no qué puede escribir el rol, así que la escritura única por capa
  queda escrita en la prosa de cada template en vez de en un campo (D38).
- Los cuatro `.instructions.md` llevan `excludeAgent: "code-review"`: los roles no
  existen en una sesión de code review (D39).

## Cómo se valida

- `logsayer agent add copilot` genera los 8 archivos en las rutas exactas y es
  idempotente.
- Ningún perfil declara un campo que Copilot ignore (test sobre el frontmatter de
  los cuatro).
- Los alias de `tools:` de cada perfil están en el conjunto canónico de la doc, y
  el conjunto declarado es el que el rol necesita: la Decidora declara `edit`
  (escribe la tabla de veredictos) y la Reverenda Madre no (escribe solo por CLI).
- Los cuatro `applyTo` cubren la capa del rol y ninguna otra: el del Navegante no
  incluye rutas de Capa 1, y el del Mentat no incluye `docs/project_state.md`,
  `docs/logbooks/` ni `docs/06_audits/`.
- `agent add copilot` no crea `.github/copilot-instructions.md`.
- Los tres adaptadores invocan los mismos comandos de Mentat
  (`spec new`, `doc new`, `doc route`).
- Los umbrales del `logsayer.toml` llegan a los templates (`>= 3`, `400 líneas`).
- Prueba manual: `agent add copilot` en un proyecto scaffoldeado, y `logsayer check`
  sigue en verde (los archivos van en `.github/`, no en `docs/`, así que no pueden
  disparar `capas_mezcladas`).
- Batería en verde: `python -m pytest -q`, `ruff check src tests`, `mypy src`.