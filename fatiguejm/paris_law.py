"""
Paris-Erdogan crack propagation (1963).

    da/dN = C·(ΔK)^m

donde ΔK = Y·Δσ·√(π·a), Y factor de forma (~1.12 borde libre, ~1.0 interior).

Integra desde tamaño inicial a_i hasta tamaño crítico a_c para obtener
los ciclos N de vida residual.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import pi, sqrt
from typing import Any

import numpy as np


@dataclass(frozen=True)
class ParisInput:
    a_initial_mm: float       # tamaño inicial fisura
    a_critical_mm: float
    delta_sigma_MPa: float    # rango tensión
    Y: float = 1.12           # factor de forma
    C: float = 6.9e-12        # acero ferrítico-perlítico Paris-Erdogan
    m: float = 3.0
    n_increments: int = 200


@dataclass(frozen=True)
class ParisResult:
    N_cycles: float
    a_vs_N: list[tuple[float, float]]
    failure: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "N_cycles": self.N_cycles,
            "samples": self.a_vs_N[:50],
            "failure": self.failure,
        }


def integrate_paris(inp: ParisInput) -> ParisResult:
    if inp.a_initial_mm >= inp.a_critical_mm:
        raise ValueError("a_initial debe ser < a_critical")
    if inp.delta_sigma_MPa <= 0:
        raise ValueError("delta_sigma_MPa debe ser > 0")

    a_values = np.linspace(inp.a_initial_mm, inp.a_critical_mm, inp.n_increments)
    da = a_values[1] - a_values[0]
    N_total = 0.0
    samples: list[tuple[float, float]] = []
    for a_mm in a_values[:-1]:
        a_m = a_mm / 1000.0
        dK = inp.Y * inp.delta_sigma_MPa * sqrt(pi * a_m) * sqrt(1000)  # MPa·√mm
        if dK <= 0:
            continue
        dN_dA = inp.C * dK ** inp.m
        if dN_dA <= 0:
            continue
        N_total += da / dN_dA
        samples.append((float(N_total), float(a_mm)))

    return ParisResult(
        N_cycles=float(N_total),
        a_vs_N=samples,
        failure=True,
    )


__all__ = ["ParisInput", "ParisResult", "integrate_paris"]
