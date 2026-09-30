# HU-14 — Cierre de la deuda de HU-07: aviso de conversión, paridad de adaptadores y criterios viejos

> Cierra los tres puntos que dejaron HU-07 en `parcial` en la auditoría del
> 2026-09-29 (`docs/06_audits/audit_2026-09-29.md`, fila HU-07).

## Qué hay que construir

- **`doc new` avisa la conversión por stdout.** `inbox.stage()` ya devuelve el
  aviso (`core/inbox.py:86-91`) y `create_doc` lo escribe en el bloque
  `## Fuente` del documento creado, pero nunca sale por la terminal. La spec §3
  dice que el CLI "avisa que hay que hacerlo antes": el aviso va a stdout, donde
  el humano lo lee, y no solo dentro del archivo que la Decidora va a auditar
  después.
- **La superficie de permisos de cada adaptador, declarada y testeada.** El
  bloque `permissions:` de opencode evalúa reglas ordenadas por
  `action` + `resource` + `effect`; el frontmatter de Claude Code solo expone
  `tools` como allowlist de **nombres de herramienta**. Son dos granularidades
  distintas de la misma restricción, y solo una de las dos se puede declarar.
- **La excepción de Claude Code, escrita donde se la busca.** La spec §6 y el
  template `adapters/claude/mentat.md.j2` dicen cuál es la superficie real y por
  qué el scoping por recurso no es declarable por subagente, en vez de dejar la
  restricción en prosa como si fuera una declaración.

### Decisiones tomadas en esta HU

1. **No se escribe un campo de permiso sin verificar.** La documentación de
   Claude Code se contradice sobre si `Bash(<patrón>)` es válido en el
   `tools:` de un subagente: `tools-reference` lo lista entre los lugares que
   aceptan `ToolName(especificador)` y `subagents` documenta que la sintaxis con
   especificador se ignora dentro de un subagente. Hay un issue abierto de
   Anthropics (`#27099`) donde un campo de permisos mal nombrado en el frontmatter
   de un agente se ignora **en silencio** y el subagente hereda Bash sin
   restringir. Un campo en silencio ignorado es peor que prosa: la prosa admite
   que es una instrucción, el campo finge ser una garantía.
2. **`settings.json` no es la salida.** Sus reglas `permissions.allow/ask/deny`
   son de sesión, no de subagente: escribirlas para restringir al Mentat
   restringiría también a la sesión principal y a los otros tres roles, y
   seguiría sin restringir al subagente. El CLI no genera ese archivo.
3. **La excepción es de granularidad, no de cobertura.** Los dos adaptadores
   declaran la misma restricción con la unidad que su herramienta soporta. Lo que
   se registra en la spec es el costo —en Claude Code el alcance por ruta vive en
   el prompt y en las reglas de la sesión—, no una limitación que se puede
   resolver generando más archivos.
4. **`doc new` no cambia de veredicto: avisa.** El CLI no convierte PDF ni docx
   (spec §3) y `doc new` no va a empezar a hacerlo. Lo que cambia es que el
   humano que tipea el comando lo lee en la terminal, sin tener que abrir el
   documento generado para descubrir que su PDF quedó archivado sin convertir.

### Lo que explícitamente NO se hace

- **No se genera `.claude/settings.json`** ni ningún otro archivo de
  configuración de la sesión del usuario (decisión 2).
- **No se reescribe el bloque `permissions:` de opencode.** Ya declara lo que
  tiene que declarar; el problema era la mitad que faltaba, no la que sobraba.
- **No se audita el comportamiento de los otros tres roles.** La HU mira la
  superficie de permisos del Mentat, que es la que Hu-07 nombraba; los roles de
  Capa 2, 3 y 4 no invocan `doc route` ni `doc new`.
- **No se cambia `doc route` para que mande el PDF a `02_technical/`.** La
  señal de "no es markdown" resuelve a la bandeja a propósito (D6/D10): el CLI
  propone, el Mentat decide la capa. Lo que se corrige es el criterio de HU-07,
  que describía el comportamiento anterior a esa decisión.

## Cómo se valida

- `doc new technical acta_reunion --from acta.pdf` imprime por stdout el aviso de
  conversión (el mismo texto que hoy solo queda en el bloque `## Fuente`), y el
  documento creado lo conserva.
- `doc new` desde un `.md` no imprime ese aviso.
- El adaptador de opencode declara `logsayer spec new*`, `logsayer doc new*` y
  `logsayer doc route*` como reglas `shell`/`allow` antes de la regla `shell`
  `*`/`ask`, y `edit` denegado antes del `shell`.
- El adaptador de Claude Code declara su superficie en el frontmatter `tools:` y
  nombra en el cuerpo la excepción de granularidad, con la misma información que
  la spec §6.
- Un test compara los dos adaptadores sobre los comandos que HU-07 nombraba: si
  alguien saca `doc new` de la superficie declarada de cualquiera de los dos, el
  test falla.
- El reporte de auditoría del 2026-09-29 no se reescribe: es un artefacto
  sellado. HU-07 vuelve a `cumple` cuando se re-audite.
- Batería completa en verde: `pytest`, `ruff check src tests`, `mypy src`,
  `check` y `process check`.
