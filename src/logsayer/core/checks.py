"""Resultado de chequeos determinísticos (bots: Suk Doctor y Fremen)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CheckResult:
    """Resultado de un chequeo único con criterio objetivo (sin juicio)."""

    name: str
    ok: bool
    detail: str


def ok(name: str, detail: str = "OK") -> CheckResult:
    return CheckResult(name=name, ok=True, detail=detail)


def fail(name: str, detail: str) -> CheckResult:
    return CheckResult(name=name, ok=False, detail=detail)