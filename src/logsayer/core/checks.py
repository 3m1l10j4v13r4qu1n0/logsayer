"""Resultado de chequeos determinísticos (bots: Suk Doctor y Fremen).

Tres estados, no dos: `warn` existe para lo que es un pendiente y no un
paciente enfermo (spec §13.4.1). Una bandeja con documentos sin ubicación
reporta `warn` — el exit code sigue siendo 0, porque un `fail` por eso
enseña a la gente a ignorar el `check`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Status = Literal["ok", "warn", "fail"]

_MARKS: dict[Status, str] = {"ok": "✔", "warn": "!", "fail": "✘"}


@dataclass(frozen=True)
class CheckResult:
    """Resultado de un chequeo único con criterio objetivo (sin juicio)."""

    name: str
    status: Status
    detail: str

    @property
    def ok(self) -> bool:
        return self.status == "ok"

    @property
    def mark(self) -> str:
        return _MARKS[self.status]


def ok(name: str, detail: str = "OK") -> CheckResult:
    return CheckResult(name=name, status="ok", detail=detail)


def warn(name: str, detail: str) -> CheckResult:
    return CheckResult(name=name, status="warn", detail=detail)


def fail(name: str, detail: str) -> CheckResult:
    return CheckResult(name=name, status="fail", detail=detail)
