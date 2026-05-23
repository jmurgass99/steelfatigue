"""
Fatiga de amplitud variable — Rainflow + corrección de tensión media + Miner.

Integra las piezas que ya existen en FatigueJm:
  1. Conteo Rainflow (`rainflow_count`) → ciclos (rango, media, conteo).
  2. Corrección de tensión media (`mean_stress.equivalent_reversed_stress`) →
     rango equivalente totalmente alternado (R=-1) por ciclo.
  3. Vida N por la curva S-N (`sn_curves_multi.cycles_to_failure`).
  4. Daño acumulado de Palmgren-Miner: D = Σ n_i / N_i ; falla si D > 1.

Así un espectro real (historia de tensiones) se evalúa de extremo a extremo, con
el efecto perjudicial de la tensión media de tracción incluido ciclo a ciclo.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from .mean_stress import equivalent_reversed_stress
from .sn_curves_multi import SNCurve, cycles_to_failure


@dataclass(frozen=True)
class DamageCycle:
    delta_sigma_eq_MPa: float   # rango equivalente R=-1 (tras corrección de media)
    n_i: float                  # conteo del ciclo
    N_i: float                  # vida admisible
    damage: float               # n_i / N_i


@dataclass(frozen=True)
class DamageResult:
    total_damage: float
    n_cycles: int
    ok: bool                    # D <= 1/gamma
    detail: List[DamageCycle]


def damage_from_cycles(cycles, curve: SNCurve, Su_MPa: float,
                       criterion: str = "goodman", gamma_Mf: float = 1.0) -> DamageResult:
    """Daño de Miner para una lista de ciclos (cada uno con .mean, .range, .count).

    Cada ciclo: amplitud = range/2, media = mean → rango equivalente R=-1 por la
    corrección de tensión media; luego N por la curva S-N y n/N acumulado.
    """
    detail: List[DamageCycle] = []
    D = 0.0
    for c in cycles:
        sa = c.range / 2.0
        sar = equivalent_reversed_stress(sa, c.mean, Su_MPa, criterion)
        dseq = 2.0 * sar                       # rango equivalente totalmente alternado
        Ni = cycles_to_failure(curve, dseq * gamma_Mf)
        di = c.count / Ni if Ni > 0 else float("inf")
        D += di
        detail.append(DamageCycle(dseq, c.count, Ni, di))
    return DamageResult(total_damage=D, n_cycles=len(detail), ok=D <= 1.0, detail=detail)


def damage_from_history(history: Sequence[float], curve: SNCurve, Su_MPa: float,
                        criterion: str = "goodman", gamma_Mf: float = 1.0) -> DamageResult:
    """Cuenta Rainflow la historia de tensiones y acumula el daño de Miner."""
    from .rainflow_fatpack import rainflow_count
    cycles = rainflow_count(history)
    return damage_from_cycles(cycles, curve, Su_MPa, criterion, gamma_Mf)


__all__ = ["DamageCycle", "DamageResult", "damage_from_cycles", "damage_from_history"]
