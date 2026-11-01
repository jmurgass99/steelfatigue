"""Rainflow counting via fatpack (ASTM E1049-85 validado) y exacto float64.

Sustituye la implementacion casera de steelfatigue.sn_curves por el algoritmo
canonico de fatpack o por el conteo de 4 puntos exacto en float64.
"""
from __future__ import annotations
import logging
from dataclasses import dataclass

import numpy as np

try:
    import fatpack
    _HAS_FATPACK = True
except ImportError:
    _HAS_FATPACK = False
    fatpack = None  # type: ignore

log = logging.getLogger("steelfatigue.rainflow_fatpack")


@dataclass(frozen=True)
class RainflowCycle:
    """Un ciclo extraido por rainflow."""
    mean: float       # tension media
    range: float      # rango (sigma_max - sigma_min)
    count: float = 1.0  # fatpack puede devolver semi-ciclos (0.5)


def rainflow_count_exact_float64(stress_history) -> list[RainflowCycle]:
    """Conteo rainflow exacto en coma flotante de 64 bits (regla de 4 puntos ASTM E1049-85).

    A diferencia de ``fatpack.find_rainflow_cycles`` (que discretiza en 64 bins),
    opera directamente sobre los valores reales de las inversiones sin cuantizar.
    """
    sig = np.asarray(stress_history, dtype=float)
    if sig.size < 4:
        raise ValueError(f"stress_history requiere >= 4 puntos (recibido {sig.size})")
    if float(np.ptp(sig)) == 0.0:
        return []

    revs: list[float] = [float(sig[0])]
    for i in range(1, sig.size - 1):
        prev_d = sig[i] - revs[-1]
        next_d = sig[i + 1] - sig[i]
        if prev_d * next_d < 0.0:
            revs.append(float(sig[i]))
        elif prev_d != 0.0 and next_d == 0.0:
            continue
    if sig[-1] != revs[-1]:
        revs.append(float(sig[-1]))

    stack: list[float] = []
    cycles: list[RainflowCycle] = []
    for s in revs:
        stack.append(s)
        while len(stack) >= 4:
            s1, s2, s3, s4 = stack[-4], stack[-3], stack[-2], stack[-1]
            r1 = abs(s2 - s1)
            r2 = abs(s3 - s2)
            r3 = abs(s4 - s3)
            if r2 <= r1 and r2 <= r3:
                mean = 0.5 * (s2 + s3)
                cycles.append(RainflowCycle(mean=float(mean), range=float(r2), count=1.0))
                del stack[-3:-1]
            else:
                break

    for i in range(len(stack) - 1):
        a, b = stack[i], stack[i + 1]
        cycles.append(
            RainflowCycle(
                mean=float(0.5 * (a + b)),
                range=float(abs(b - a)),
                count=0.5,
            )
        )
    return cycles


def rainflow_count(stress_history, use_float64_exact: bool = False):
    """Conteo rainflow ASTM E1049 via fatpack (o exacto float64 si ``use_float64_exact=True``)."""
    if use_float64_exact:
        return rainflow_count_exact_float64(stress_history)

    if not _HAS_FATPACK:
        raise ImportError(
            "fatpack no esta instalado (pip install fatpack>=0.7). "
            "Sin fatpack solo esta disponible el algoritmo legacy en sn_curves."
        )

    sig = np.asarray(stress_history, dtype=float)
    if sig.size < 4:
        raise ValueError(f"stress_history requiere >= 4 puntos (recibido {sig.size})")

    if float(np.ptp(sig)) == 0.0:
        return []

    rev_result = fatpack.find_reversals(sig)
    rev_values = rev_result[0] if isinstance(rev_result, tuple) else rev_result
    cycles_array, residue = fatpack.find_rainflow_cycles(rev_values)
    out = []
    for low, high in cycles_array:
        rng = abs(high - low)
        mean = (high + low) / 2
        out.append(RainflowCycle(mean=float(mean), range=float(rng), count=1.0))
    if len(residue) >= 2:
        rev_res = np.asarray(residue, dtype=float)
        if rev_res.ndim == 2:
            rev_res = rev_res[0]
        n_res = rev_res.shape[0]
        for i in range(0, n_res - 1):
            a, b = float(rev_res[i]), float(rev_res[i + 1])
            low, high = (a, b) if a <= b else (b, a)
            out.append(RainflowCycle(
                mean=(high + low) / 2,
                range=high - low,
                count=0.5,
            ))
    return out


def rainflow_count_arrays(stress_history, use_float64_exact: bool = False):
    """Variante que devuelve numpy arrays (means, ranges, counts)."""
    cycles = rainflow_count(stress_history, use_float64_exact=use_float64_exact)
    if not cycles:
        return np.array([]), np.array([]), np.array([])
    means = np.array([c.mean for c in cycles])
    ranges = np.array([c.range for c in cycles])
    counts = np.array([c.count for c in cycles])
    return means, ranges, counts
