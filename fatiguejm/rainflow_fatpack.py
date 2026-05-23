"""Rainflow counting via fatpack (ASTM E1049-85 validado).

Sustituye la implementacion casera de fatiguejm.sn_curves por el algoritmo
canonico de fatpack. La API se mantiene compatible con cycles propios.
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

log = logging.getLogger("fatiguejm.rainflow_fatpack")


@dataclass(frozen=True)
class RainflowCycle:
    """Un ciclo extraido por rainflow."""
    mean: float       # tension media
    range: float      # rango (sigma_max - sigma_min)
    count: float = 1.0  # fatpack puede devolver semi-ciclos (0.5)


def rainflow_count(stress_history):
    """Conteo rainflow ASTM E1049 via fatpack.

    Args:
        stress_history: secuencia (iterable) de tensiones (cualquier unidad
            consistente con la curva S-N usada despues).

    Returns:
        list[RainflowCycle] ordenados por aparicion en el algoritmo.

    Raises:
        ImportError si fatpack no esta disponible.
        ValueError si la historia es muy corta.
    """
    if not _HAS_FATPACK:
        raise ImportError(
            "fatpack no esta instalado (pip install fatpack>=0.7). "
            "Sin fatpack solo esta disponible el algoritmo legacy en sn_curves."
        )

    sig = np.asarray(stress_history, dtype=float)
    if sig.size < 4:
        raise ValueError(f"stress_history requiere >= 4 puntos (recibido {sig.size})")

    # Si no hay variacion no existen ciclos; fatpack falla con senal plana.
    if float(np.ptp(sig)) == 0.0:
        return []

    # find_reversals devuelve (values, indices); solo necesitamos values.
    rev_result = fatpack.find_reversals(sig)
    rev_values = rev_result[0] if isinstance(rev_result, tuple) else rev_result
    cycles_array, residue = fatpack.find_rainflow_cycles(rev_values)
    out = []
    # cycles_array tiene forma (N, 2) con (low, high)
    for low, high in cycles_array:
        rng = abs(high - low)
        mean = (high + low) / 2
        out.append(RainflowCycle(mean=float(mean), range=float(rng), count=1.0))
    # residue: semi-ciclos sin cerrar
    # fatpack puede devolver residue 2-D (row0=valores, row1=indices)
    if len(residue) >= 2:
        rev_res = np.asarray(residue, dtype=float)
        if rev_res.ndim == 2:
            rev_res = rev_res[0]          # quedarnos solo con los valores
        n_res = rev_res.shape[0]
        for i in range(0, n_res - 1, 2):
            a, b = float(rev_res[i]), float(rev_res[i + 1])
            low, high = (a, b) if a <= b else (b, a)
            out.append(RainflowCycle(
                mean=(high + low) / 2,
                range=high - low,
                count=0.5,
            ))
    return out


def rainflow_count_arrays(stress_history):
    """Variante que devuelve numpy arrays (means, ranges, counts).

    Mas eficiente para uso vectorizado downstream (Miner damage).
    """
    cycles = rainflow_count(stress_history)
    if not cycles:
        return np.array([]), np.array([]), np.array([])
    means = np.array([c.mean for c in cycles])
    ranges = np.array([c.range for c in cycles])
    counts = np.array([c.count for c in cycles])
    return means, ranges, counts
