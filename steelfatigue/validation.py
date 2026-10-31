"""Validadores de parámetros de ingeniería, sin dependencias.

Copia local (vendorizada) de los validadores compartidos del ecosistema
Structural JM, para que ``steelfatigue`` funcione como paquete independiente.

El estilo de mensaje y el tipo de excepción imitan deliberadamente lo que los
módulos ya levantan (``ValueError("<name> must be positive")``, en inglés),
para que el código que captura errores existente siga funcionando.

Cada validador devuelve el valor validado, así puede usarse inline:
    >>> fy = require_positive(fy, "fy")
"""
from __future__ import annotations

from typing import Iterable, TypeVar

Number = TypeVar("Number", int, float)
T = TypeVar("T")


def require_positive(value: Number, name: str = "value") -> Number:
    """Exige ``value > 0``. Imita ``ValueError("<name> must be positive")``."""
    if not value > 0:
        raise ValueError(f"{name} must be positive")
    return value


def require_non_negative(value: Number, name: str = "value") -> Number:
    """Exige ``value >= 0``. Imita ``ValueError("<name> must be >= 0")``."""
    if not value >= 0:
        raise ValueError(f"{name} must be >= 0")
    return value


def require_range(
    value: Number, low: float, high: float, name: str = "value"
) -> Number:
    """Exige ``low <= value <= high``."""
    if not (low <= value <= high):
        raise ValueError(f"{name} must be in [{low}, {high}]")
    return value


def require_in(value: T, choices: Iterable[T], name: str = "value") -> T:
    """Exige que ``value`` esté en ``choices``."""
    choices = list(choices)
    if value not in choices:
        opts = ", ".join(str(c) for c in choices)
        raise ValueError(f"{name} must be one of: {opts}")
    return value
