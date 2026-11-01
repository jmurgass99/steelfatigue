"""Separación Semántica -> Malla de Extrapolación Hot-Spot y Grieta (HotspotMeshMapping) para SteelFatigue.

Mapea cordones de soldadura semánticos (`weld_toe_to_points`) y frentes de propagación de grieta
(`crack_to_segments`) a puntos de lectura FEM IIW (0.4t, 1.0t) y segmentos de ley de Paris,
preservando la tensión de punto caliente extrapolada sigma_hs, los ciclos admisibles EN 1993-1-9
y el factor de intensidad de tensiones Delta_K al refinar la malla de muestreo.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from math import sqrt
from typing import Dict, List, Tuple

from .hotspot import HotSpotInput, hot_spot_stress


@dataclass(frozen=True)
class SemanticWeldToe:
    id: str
    plate_thickness_mm: float
    detail_category_MPa: float = 80.0
    nominal_stress_range_MPa: float = 95.0


@dataclass
class HotspotMeshMapping:
    """Mapeo Cordón Semántico -> Puntos de Muestreo de Tensión y Segmentos de Grieta."""
    weld_toe_to_points: Dict[str, List[int]] = field(default_factory=dict)
    point_to_weld: Dict[int, str] = field(default_factory=dict)
    crack_to_segments: Dict[str, List[int]] = field(default_factory=dict)


@dataclass
class SurfaceStressNode:
    index: int
    weld_id: str
    dist_from_toe_mm: float
    stress_MPa: float


def build_hotspot_crack_mesh(
    weld: SemanticWeldToe | None = None,
    points_per_zone: int = 6,
    initial_crack_mm: float = 1.0,
    cycles_applied: float = 500000.0,
) -> Tuple[List[SurfaceStressNode], HotspotMeshMapping, Dict[str, float]]:
    """Genera la malla de muestreo de tensiones superficiales y evalúa fatiga IIW y EN 1993-1-9."""
    if weld is None:
        weld = SemanticWeldToe(
            id="WELD-TOE-FLANGE",
            plate_thickness_mm=25.0,
            detail_category_MPa=90.0,
            nominal_stress_range_MPa=110.0,
        )

    t = weld.plate_thickness_mm
    div = max(2, int(points_per_zone))
    mapping = HotspotMeshMapping()
    nodes: List[SurfaceStressNode] = []

    # Distancias de lectura IIW Tipo a: t/2 y 3t/2
    d_half = 0.5 * t
    d_three_half = 1.5 * t

    # Concentración elástica teórica hacia el borde del cordón (dist = 0)
    # sigma(x) = sigma_nom * (1 + 1.25 / sqrt(max(x/t, 0.04)))
    def stress_at(dist: float) -> float:
        norm_d = max(dist / t, 0.03)
        return weld.nominal_stress_range_MPa * (1.0 + 0.65 / sqrt(norm_d))

    mapping.weld_toe_to_points[weld.id] = []
    # Generar muestras densas desde dist=1.0 mm hasta dist=2.5*t
    dist_vals = [0.2 * t + (i / (div - 1)) * (2.2 * t) for i in range(div)]
    for d in dist_vals:
        idx = len(nodes)
        s_val = stress_at(d)
        nodes.append(
            SurfaceStressNode(
                index=idx,
                weld_id=weld.id,
                dist_from_toe_mm=d,
                stress_MPa=s_val,
            )
        )
        mapping.weld_toe_to_points[weld.id].append(idx)
        mapping.point_to_weld[idx] = weld.id

    # Extrapolación IIW lineal
    s_t_half = stress_at(d_half)
    s_3t_half = stress_at(d_three_half)
    hs_in = HotSpotInput(
        sigma_t_half=s_t_half,
        sigma_3t_half=s_3t_half,
        thickness_mm=t,
        method="linear",
    )
    sigma_hs = hot_spot_stress(hs_in)

    # Capacidad de ciclos N_R según EN 1993-1-9: N = 2e6 * (Delta_sigma_c / Delta_sigma_hs)^3
    n_cycles_cap = 2.0e6 * (weld.detail_category_MPa / max(sigma_hs, 1.0)) ** 3.0
    damage_d = cycles_applied / max(n_cycles_cap, 1.0)

    # Crecimiento de grieta Paris: da/dN = C * (Delta_K)^m
    # Delta_K = Y * Delta_sigma * sqrt(pi * a), Y=1.12
    c_paris = 3.0e-13  # mm/ciclo para Delta_K en MPa*sqrt(mm)
    m_paris = 3.0
    a_curr = initial_crack_mm
    mapping.crack_to_segments["CRACK-GROWTH"] = []
    n_steps = 10
    d_n = cycles_applied / n_steps
    for i in range(n_steps):
        delta_k = 1.12 * sigma_hs * sqrt(3.14159 * a_curr)
        da = c_paris * (delta_k ** m_paris) * d_n
        a_curr += min(da, 5.0)
        mapping.crack_to_segments["CRACK-GROWTH"].append(i)

    summary = {
        "hotspot_stress_MPa": sigma_hs,
        "detail_category_MPa": weld.detail_category_MPa,
        "N_cycles_capacity": n_cycles_cap,
        "damage_Miner_D": damage_d,
        "final_crack_size_mm": a_curr,
        "stress_concentration_K_hs": sigma_hs / max(weld.nominal_stress_range_MPa, 1.0),
    }
    return nodes, mapping, summary
