# HU-18 — Presets de proyecto (`init --preset`, cierre de la fase 7)

> Cierra D-08: la fase 7 era la última con diseño escrito y cero código. El diseño
> está en `logsayer_especificacion_maestra.md` §4 y §5, y las decisiones que salieron
> del contraste con el código real son D29 (el idioma no es eje del preset), D30
> (`init` declara, `agent add` ejecuta) y D31 (los umbrales no se mueven de
> `[logsayer]`). Lo nuevo de esta HU es D41.

## Qué hay que construir

- `src/logsayer/presets/default.toml` y `minimal.toml`: los presets son **datos**,
  TOML dentro del paquete, leídos con `importlib.resources`. Agregar un preset es
  agregar un archivo y no toca lógica.
- `src/logsayer/core/presets.py`: `available()`, `load(nombre) -> Preset` y
  `PresetError`. El `Preset` lleva los umbrales ya validados y los adaptadores
  declarados.
- `LogsayerConfig.from_mapping()`: los umbrales de un preset se validan contra el
  **mismo** contrato que lee el `logsayer.toml` del proyecto. Sin esto, el preset
  tendría un segundo validador y un preset roto podría llegar al scaffold.
- `init --preset <nombre>`: materializa el preset **una vez** en `logsayer.toml`,
  escribiendo `[project] preset` y `[adapters] enabled`. Sin `--preset`, el TOML
  sale idéntico al de siempre.
- Dos checks nuevos en Suk: `preset_conocido` y `adaptadores_declarados`. Los dos
  hacen legales las dos claves nuevas (D13) y los dos avisan sin corregir.

## Lo que el diseño fija y el código tiene que respetar

- **El preset es un snapshot, no una herencia viva.** `init` copia los valores y el
  preset deja de existir para ese proyecto. El precio —actualizar logsayer no
  actualiza los umbrales de un proyecto ya scaffoldeado— se paga en §10 y con
  `preset_conocido`.
- **`default` no sobreescribe nada.** Su archivo no declara `[logsayer]`: la
  ausencia de la tabla es el contrato, así que `init` e `init --preset default`
  producen los mismos umbrales por construcción, no por coincidencia de valores.
- **La forma del TOML no se mueve.** Los cuatro umbrales siguen en `[logsayer]`
  (D31): renombrar la tabla haría que todo proyecto ya scaffoldeado volviera a los
  defaults **en silencio**, porque `LogsayerConfig.load()` no distingue "falta la
  tabla" de "no hay configuración".
- **`init` no genera adaptadores.** El `enabled` es una declaración y `agent add`
  es el único comando que escribe archivos de adaptador (D30).
- **En modo adopt, el preset no se aplica sobre un `logsayer.toml` existente** y
  `init` avisa: el TOML del proyecto manda y aplicarlo a medias sería peor que no
  aplicarlo (D4).
- **Un nombre de adaptador desconocido en un preset no es un error del preset.**
  El juicio es del check, que es donde vive; un preset no puede saber qué
  adaptadores tendrá la versión futura.

## D41 — Se mide el conjunto, no cada archivo

`adaptadores_declarados` avisa cuando un nombre de `enabled` está en `SUPPORTED`
pero **ninguno** de los archivos de su `AdapterSpec` existe en el proyecto. Se
descartó avisar por archivo faltante: quien escribió uno a mano ya ejecutó la
parte, y un archivo borrado a conciencia no es un pendiente. Con el criterio
archivo-por-archivo, borrar un subagente por desuso produciría un aviso permanente
—la clase de ruido que el check `indice_al_dia` ya evita por decisión de D19.

## Cómo se valida

- Los dos presets empaquetados validan contra `LogsayerConfig`, y un preset con
  umbral inválido, con TOML roto o con `enabled` mal formado se rechaza.
- Los nombres empaquetados son exactamente `{default, minimal}`: agregar un tercero
  sin decidirlo rompe el test.
- `init --preset minimal` escribe `[project] preset = "minimal"`,
  `[adapters] enabled = ["claude"]` y los umbrales laxos; el `AGENTS.md` generado
  hereda esos umbrales (`800 líneas`).
- `init` sin `--preset` no escribe `[project]` ni `[adapters]`.
- `init` no crea `.opencode/`, `.claude/` ni `.github/` aunque el preset declare un
  adaptador.
- `init --here --preset` sobre un `logsayer.toml` existente no lo toca y avisa;
  sobre uno ausente, lo aplica.
- `preset_conocido` avisa cuando el nombre declarado no existe en el paquete y
  nombra la versión; `adaptadores_declarados` avisa antes de `agent add` y queda en
  `ok` después.
- Un proyecto scaffoldeado sin preset deja los dos checks en `ok`: la batería no
  puede avisar por algo que nadie pidió.
- El wheel lleva `logsayer/presets/*.toml` (verificado instalando el wheel en un venv
  limpio y scaffoldeando con `--preset minimal`).
- Batería en verde: `python -m pytest -q`, `ruff check src tests`, `mypy src`.