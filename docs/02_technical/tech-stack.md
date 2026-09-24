# Stack técnico — logsayer (fuente: spec §11 y `pyproject.toml`)

| Componente | Elección | Por qué |
|---|---|---|
| Lenguaje | Python 3.11+ (`requires-python >=3.11`) | Tipado moderno, ecosistema CLI, targets compatibles |
| CLI framework | Typer `>=0.12` | Comandos anidados + alias con poco boilerplate |
| Templates | Jinja2 `>=3.1` | Render de `AGENTS.md`, estado, índice, HUs y adaptadores |
| Config | TOML (`logsayer.toml`) | Spec §4: umbrales en un solo archivo, parsing nativo (`tomllib`) |
| Empaquetado | `pyproject.toml` + hatchling | `packages = ["src/logsayer"]`, publicación vía PyPI |
| Distribución | `uv tool install` / `pipx` | Instalación global de CLIs sin contaminar entornos |
| Verificación | pytest, ruff, mypy (`--strict`) | Tests + lint + tipado estricto (`pyproject.toml`) |

## Layout

```
src/logsayer/
├── cli.py         # comandos Typer + alias planos
├── config.py      # LogsayerConfig (umbrales)
├── scaffold.py    # init / modo adopt
├── core/          # motor único: specs, logbook, audit, suk, fremen, checks, project
└── adapters/      # por agente: opencode, claude — wrappers finos al CLI
```