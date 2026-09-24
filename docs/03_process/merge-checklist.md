# Checklist de merge — logsayer

Protocolo de integración (Capa 5 — Fremen). Convención del repo: feature branches convergen en `develop`; los releases llevan tag semver.

## Antes de mergear a `develop`

- [ ] Rama originada desde `develop` actualizado.
- [ ] `pytest` en verde.
- [ ] `ruff check src tests` en verde.
- [ ] `mypy src` (strict) en verde.
- [ ] `logsayer check` sano sobre el repo (dogfooding).
- [ ] Si corresponde, bump de versión sincronizado entre `pyproject.toml` y `src/logsayer/__init__.py`.
- [ ] Commit(es) con mensaje conventional (`feat`, `fix`, `docs`, `chore`, `test`, `merge`).
- [ ] Merge `--no-ff` con mensaje `merge(<fase>): <resumen>`.

## Publicación (PyPI)

- [ ] `python -m build` genera wheel + sdist sin errores.
- [ ] Instalación en venv limpio: `init` + `check` OK.
- [ ] Tag semver (`vX.Y.Z`) y push a `origin`.
- [ ] `uv publish` / `twine upload` con token de `3m1l10j4v13r4qu1n0` (manual).