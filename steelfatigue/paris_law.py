"""
Paris-Erdogan crack propagation (1963).

    da/dN = C·(ΔK)^m

donde ΔK = Y·Δσ·√(π·a), Y factor de forma (~1.12 borde libre, ~1.0 interior).

Unidades: ΔK se evalúa en MPa·√m (a en metros) y da/dN en m/ciclo, que son las
unidades de la C por defecto (Barsom & Rolfe, aceros ferrítico-perlíticos:
C = 6,9·10⁻¹², m = 3). Si se pasa una C de otra fuente, debe estar en esas
mismas unidades. Hasta 2026-10-31 ΔK se evaluaba en MPa·√mm con esa misma C,
lo que multiplicaba la velocidad de propagación por √1000 = 31,6 y dividía la
vida por el mismo factor (ver tests/test_paris_closed_form_golden.py).

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
    C: float = 6.9e-12        # m/ciclo con ΔK en MPa·√m (Barsom & Rolfe, ferrítico-perlítico)
    m: float = 3.0
    n_increments: int = 200
    delta_K_th_MPa_sqrt_m: float = 0.0  # umbral de propagación ΔK_th [MPa·√m]


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
        dK = inp.Y * inp.delta_sigma_MPa * sqrt(pi * a_m)   # MPa·√m
        if dK <= 0 or dK <= inp.delta_K_th_MPa_sqrt_m:
            if a_mm == a_values[0] and dK <= inp.delta_K_th_MPa_sqrt_m:
                return ParisResult(
                    N_cycles=float("inf"),
                    a_vs_N=[],
                    failure=False,
                )
            continue
        da_dN_m = inp.C * dK ** inp.m                        # m/ciclo
        if da_dN_m <= 0:
            continue
        N_total += (da / 1000.0) / da_dN_m                   # da en mm -> m
        samples.append((float(N_total), float(a_mm)))

    return ParisResult(
        N_cycles=float(N_total),
        a_vs_N=samples,
        failure=True,
    )


def paris_cycles_to_failure(inp: ParisInput) -> float:
    """Atajo que devuelve directamente el número de ciclos hasta a_critical."""
    return integrate_paris(inp).N_cycles


__all__ = ["ParisInput", "ParisResult", "integrate_paris", "paris_cycles_to_failure"]
