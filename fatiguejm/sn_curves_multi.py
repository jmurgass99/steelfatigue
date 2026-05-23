"""
Curvas S-N por código — EN 1993-1-9 + AISC 360 Apéndice 3 + AS 4100 §11 +
ASME BPVC VIII Div.2 + NSR-10 (referencia AISC).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class SNCurve:
    code: str
    category: str        # 'FAT 90' (EU), 'A' (AISC), '50' (AS), ...
    delta_sigma_C_MPa: float
    N_C: float = 2.0e6
    slope_m: float = 3.0
    cutoff_N: float = 1.0e8


# --- AISC 360-22 Appendix 3 (Tabla A3.1) ---
AISC_CATEGORIES: list[SNCurve] = [
    SNCurve("US", "A",  165.0, slope_m=3.0),
    SNCurve("US", "B",  110.0, slope_m=3.0),
    SNCurve("US", "B'", 83.0,  slope_m=3.0),
    SNCurve("US", "C",  69.0,  slope_m=3.0),
    SNCurve("US", "C'", 55.0,  slope_m=3.0),
    SNCurve("US", "D",  48.0,  slope_m=3.0),
    SNCurve("US", "E",  31.0,  slope_m=3.0),
    SNCurve("US", "E'", 18.0,  slope_m=3.0),
]


# --- AS 4100 §11 (Tabla 11.6.2) — categorías 36..160 ---
AS4100_CATEGORIES: list[SNCurve] = [
    SNCurve("AU", "160", 160, slope_m=3.0),
    SNCurve("AU", "125", 125, slope_m=3.0),
    SNCurve("AU", "100", 100, slope_m=3.0),
    SNCurve("AU", "80",   80, slope_m=3.0),
    SNCurve("AU", "63",   63, slope_m=3.0),
    SNCurve("AU", "50",   50, slope_m=3.0),
    SNCurve("AU", "36",   36, slope_m=3.0),
]


# --- ASME BPVC VIII Div.2 (curvas estandarizadas para pressure vessels) ---
ASME_CATEGORIES: list[SNCurve] = [
    SNCurve("ASME", "AD-160",        160, slope_m=3.5),
    SNCurve("ASME", "AD-100",        100, slope_m=3.5),
    SNCurve("ASME", "AD-71",          71, slope_m=3.5),
    SNCurve("ASME", "AD-50",          50, slope_m=3.5),
]


def lookup_sn(code: str, category: str) -> SNCurve | None:
    libs = {
        "US": AISC_CATEGORIES, "CO": AISC_CATEGORIES,    # NSR-10 referencia AISC
        "AU": AS4100_CATEGORIES,
        "ASME": ASME_CATEGORIES,
    }
    lib = libs.get(code.upper())
    if lib is None:
        return None
    for c in lib:
        if c.category == category:
            return c
    return None


def size_effect_ks(thickness_mm: float, t_ref_mm: float = 25.0, exponent: float = 0.2) -> float:
    """Factor de reducción por espesor (EN 1993-1-9 §7.2.1).

    Para detalles con espesor t > t_ref (25 mm por defecto), la resistencia a
    fatiga se reduce:  k_s = (t_ref / t)^n  (n = 0.2 típico). t <= t_ref -> 1.0.
    """
    if thickness_mm <= t_ref_mm:
        return 1.0
    return (t_ref_mm / thickness_mm) ** exponent


def with_size_effect(curve: SNCurve, thickness_mm: float) -> SNCurve:
    """Devuelve una copia de la curva con Δσ_C reducido por el efecto espesor EN §7.2.1."""
    ks = size_effect_ks(thickness_mm)
    return SNCurve(curve.code, curve.category, curve.delta_sigma_C_MPa * ks,
                   curve.N_C, curve.slope_m, curve.cutoff_N)


def cycles_to_failure(curve: SNCurve, delta_sigma_MPa: float) -> float:
    """N a partir de Δσ usando la curva del código."""
    if delta_sigma_MPa <= 0:
        return float("inf")
    N = curve.N_C * (curve.delta_sigma_C_MPa / delta_sigma_MPa) ** curve.slope_m
    return min(N, curve.cutoff_N)


def equivalent_categories(delta_sigma_C_MPa: float,
                            tolerance: float = 10.0) -> list[SNCurve]:
    """Encuentra categorías de otros códigos con Δσ_C similar."""
    matches = []
    for lib in (AISC_CATEGORIES, AS4100_CATEGORIES, ASME_CATEGORIES):
        for c in lib:
            if abs(c.delta_sigma_C_MPa - delta_sigma_C_MPa) <= tolerance:
                matches.append(c)
    return matches


__all__ = [
    "SNCurve", "AISC_CATEGORIES", "AS4100_CATEGORIES", "ASME_CATEGORIES",
    "lookup_sn", "cycles_to_failure", "equivalent_categories",
    "size_effect_ks", "with_size_effect",
]
