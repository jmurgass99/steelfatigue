"""
Curva S-N trilineal de detalle EN 1993-1-9 §7 (EC3-1-9) y daño Palmgren-Miner.

A diferencia de :func:`fatiguejm.sn_curves_multi.cycles_to_failure` (recta única
m=3 con recorte de N, pensada para AISC/AS/ASME) y de
:meth:`fatiguejm.sn_curves.FatigueEvaluator.calculate_endurance` (recta única
m=3 sin codo ni cut-off), aquí se implementa la curva **trilineal** canónica del
Eurocódigo 3 Parte 1-9, §7.1 (ec. 7.1), con sus tres tramos:

    1. Pendiente m = 3   para  Δσ ≥ Δσ_D :
           N = 2·10⁶ · (Δσ_C / Δσ)³                       (Δσ_C a N_C = 2·10⁶)
    2. Codo (límite de fatiga a amplitud constante) Δσ_D a N = 5·10⁶ :
           Δσ_D = Δσ_C · (2/5)^(1/3)  ≈ 0.737 · Δσ_C
    3. Pendiente m = 5   para  Δσ_L ≤ Δσ < Δσ_D :
           N = 5·10⁶ · (Δσ_D / Δσ)⁵
    4. Cut-off (límite de truncamiento) Δσ_L a N = 10⁸ :
           Δσ_L = Δσ_D · (5·10⁶/10⁸)^(1/5)  ≈ 0.549 · Δσ_D  ≈ 0.405 · Δσ_C
       Δσ < Δσ_L  →  N = ∞  (no contribuye al daño).

Las categorías de detalle Δσ_C (FAT) viven en :mod:`fatiguejm.wohler_db`; este
módulo las reutiliza (no define un segundo catálogo). Las funciones de la curva
son **puras**: reciben Δσ_C (resistencia característica) y devuelven N, sin
aplicar ningún factor parcial. El factor parcial de resistencia a fatiga γ_Mf
(EN 1993-1-9 §3, Tabla 3.1) se aplica una sola vez, en la capa de Miner
(:func:`palmgren_miner_ec3`), reduciendo la resistencia: Δσ_C,d = Δσ_C / γ_Mf.

Acumulación de daño — regla de Palmgren-Miner (EN 1993-1-9 §A.6):

    D = Σ_i  n_i / N_i  ≤ 1.0

Referencias de fichas máster del workspace: W01419 (apuntes EN 1993-1-9, define
la curva §7 y tabula el codo Δσ_D) y W01510 (Exercise 9, ejemplo Miner resuelto
con cut-off y γ_Mf=1.15).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Mapping, Sequence, Union

from .wohler_db import FATDetail, lookup_fat

# --- Puntos fijos de la curva EN 1993-1-9 §7.1 (Fig. 7.1) ---
EC3_NC: float = 2.0e6        # número de ciclos de la categoría de detalle Δσ_C
EC3_N_KNEE: float = 5.0e6    # codo: cambio de pendiente m=3 → m=5 (Δσ_D)
EC3_N_CUTOFF: float = 1.0e8  # cut-off / límite de truncamiento (Δσ_L)

_M1: float = 3.0  # pendiente tramo alto (Δσ ≥ Δσ_D)
_M2: float = 5.0  # pendiente tramo bajo (Δσ_L ≤ Δσ < Δσ_D)

# Factores derivados (constantes, derivados de los puntos fijos):
#   Δσ_D = Δσ_C·(N_C/N_knee)^(1/m1) = Δσ_C·(2/5)^(1/3) ≈ 0.7368·Δσ_C
#   Δσ_L = Δσ_D·(N_knee/N_cutoff)^(1/m2) = Δσ_D·(1/20)^(1/5) ≈ 0.549·Δσ_D
_KNEE_FACTOR: float = (EC3_NC / EC3_N_KNEE) ** (1.0 / _M1)        # ≈ 0.7368
_CUTOFF_FACTOR_ON_D: float = (EC3_N_KNEE / EC3_N_CUTOFF) ** (1.0 / _M2)  # ≈ 0.549


def _resolve_delta_sigma_c(detail: Union[float, int, str, FATDetail]) -> float:
    """Acepta Δσ_C numérico, código FAT ('FAT 90') o un :class:`FATDetail`."""
    if isinstance(detail, FATDetail):
        return float(detail.delta_sigma_C)
    if isinstance(detail, str):
        fat = lookup_fat(detail)
        if fat is None:
            raise ValueError(f"categoría FAT desconocida: {detail!r}")
        return float(fat.delta_sigma_C)
    dc = float(detail)
    if dc <= 0:
        raise ValueError(f"Δσ_C debe ser > 0 (recibido {dc})")
    return dc


def constant_amplitude_limit(detail: Union[float, int, str, FATDetail]) -> float:
    """Límite de fatiga a amplitud constante Δσ_D (codo a N = 5·10⁶).

    EN 1993-1-9 §7.1: Δσ_D = Δσ_C · (2/5)^(1/3) ≈ 0.737 · Δσ_C.
    """
    return _resolve_delta_sigma_c(detail) * _KNEE_FACTOR


def cutoff_limit(detail: Union[float, int, str, FATDetail]) -> float:
    """Límite de truncamiento (cut-off) Δσ_L a N = 10⁸.

    EN 1993-1-9 §7.1: Δσ_L = Δσ_D · (5·10⁶/10⁸)^(1/5) = 0.549 · Δσ_D ≈ 0.405·Δσ_C.
    Por debajo de Δσ_L una oscilación no produce daño por fatiga.
    """
    return constant_amplitude_limit(detail) * _CUTOFF_FACTOR_ON_D


def ec3_cycles_to_failure(
    delta_sigma_MPa: float, detail: Union[float, int, str, FATDetail]
) -> float:
    """Número de ciclos resistentes N para un rango Δσ (EN 1993-1-9 §7.1).

    Curva trilineal:
      * Δσ ≥ Δσ_D            → N = 2·10⁶·(Δσ_C/Δσ)³        (m=3)
      * Δσ_L ≤ Δσ < Δσ_D     → N = 5·10⁶·(Δσ_D/Δσ)⁵        (m=5)
      * Δσ < Δσ_L            → N = ∞ (sin daño)

    :param delta_sigma_MPa: rango de tensión Δσ (MPa).
    :param detail: Δσ_C (MPa), código FAT o :class:`FATDetail`.
    :returns: N (ciclos), o ``math.inf`` si Δσ ≤ 0 o Δσ < Δσ_L.
    """
    if delta_sigma_MPa <= 0:
        return math.inf
    dc = _resolve_delta_sigma_c(detail)
    dD = dc * _KNEE_FACTOR
    dL = dD * _CUTOFF_FACTOR_ON_D
    if delta_sigma_MPa >= dD:
        return EC3_NC * (dc / delta_sigma_MPa) ** _M1
    if delta_sigma_MPa >= dL:
        return EC3_N_KNEE * (dD / delta_sigma_MPa) ** _M2
    return math.inf


@dataclass(frozen=True)
class MinerBlock:
    """Bloque del espectro evaluado: Δσ, n aplicados, N resistente, daño n/N."""

    stress_range_MPa: float
    cycles: float
    N_i: float
    damage: float


def palmgren_miner_ec3(
    spectrum: Sequence[Mapping[str, float]],
    detail: Union[float, int, str, FATDetail, None] = None,
    gamma_Mf: float = 1.0,
    *,
    delta_sigma_c: Union[float, int, str, FATDetail, None] = None,
) -> dict[str, Any]:
    """Daño acumulado de Palmgren-Miner con la curva EC3-1-9 (EN 1993-1-9 §A.6).

    D = Σ n_i / N_i, con N_i de :func:`ec3_cycles_to_failure` evaluada sobre la
    resistencia de diseño Δσ_C,d = Δσ_C / γ_Mf (EN 1993-1-9 §3). Los ciclos con
    Δσ por debajo del cut-off Δσ_L,d no producen daño (N = ∞).

    :param spectrum: lista de bloques ``{"stress_range_MPa": .., "cycles": ..}``.
    :param detail / delta_sigma_c: categoría de detalle (numérica/FAT/FATDetail).
    :param gamma_Mf: factor parcial de resistencia a fatiga (1.00 damage-tolerant,
        1.15 safe-life para tensión normal; EN 1993-1-9 Tabla 3.1).
    :returns: dict con ``total_damage``, ``ok`` (D ≤ 1), ``blocks`` y la
        resistencia de diseño usada.
    """
    detail_in = detail if detail is not None else delta_sigma_c
    if detail_in is None:
        raise TypeError("falta la categoría de detalle (detail / delta_sigma_c)")
    if gamma_Mf <= 0:
        raise ValueError(f"gamma_Mf debe ser > 0 (recibido {gamma_Mf})")

    dc_design = _resolve_delta_sigma_c(detail_in) / gamma_Mf

    blocks: list[MinerBlock] = []
    total_D = 0.0
    for blk in spectrum:
        ds = float(blk["stress_range_MPa"])
        # 'cycles' se exige con el MISMO rigor que 'stress_range_MPa'. Con
        # .get(..., 0.0) un bloque sin ciclos aportaba dano 0.0 y desaparecia
        # del sumatorio, ademas de reportarse con `cycles: 0.0` — un numero que
        # el usuario nunca dio. Un 0.0 declarado explicitamente sigue valiendo.
        n = float(blk["cycles"])
        N = ec3_cycles_to_failure(ds, dc_design)
        d = n / N if math.isfinite(N) and N > 0 else 0.0
        total_D += d
        blocks.append(MinerBlock(ds, n, N, d))

    return {
        "total_damage": total_D,
        "ok": total_D <= 1.0,
        "delta_sigma_c_design_MPa": dc_design,
        "gamma_Mf": gamma_Mf,
        "blocks": [
            {
                "stress_range_MPa": b.stress_range_MPa,
                "cycles": b.cycles,
                "N_i": b.N_i,
                "damage": b.damage,
            }
            for b in blocks
        ],
    }


__all__ = [
    "EC3_NC",
    "EC3_N_KNEE",
    "EC3_N_CUTOFF",
    "constant_amplitude_limit",
    "cutoff_limit",
    "ec3_cycles_to_failure",
    "MinerBlock",
    "palmgren_miner_ec3",
]
