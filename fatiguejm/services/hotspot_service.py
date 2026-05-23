"""Servicio de analisis Hot-Spot Stress (HSS) con vida a fatiga.

Envuelve :func:`fatiguejm.hotspot.hot_spot_stress` con calculo de
categoria IIW/FAT y estimacion de vida via curva S-N bilineal.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal


@dataclass(frozen=True)
class HotSpotAnalysisInput:
    """Entrada para el analisis HSS completo.

    Args:
        sigma_t_half: tension a t/2 [MPa].
        sigma_3t_half: tension a 3t/2 [MPa].
        thickness_mm: espesor de la placa [mm].
        weld_type: tipo de soldadura / categoria FAT (ej. 'butt', 'fillet').
        fat_class: categoria FAT (numero) asociada al tipo de soldadura.
        method: 'linear' (IIW Tipo a) o 'quadratic' (IIW Tipo b).
        sigma_5t_half: tension a 5t/2 (solo para 'quadratic').
        gamma_mf: factor parcial de seguridad a fatiga.
    """
    sigma_t_half: float
    sigma_3t_half: float
    thickness_mm: float
    weld_type: str = "butt"
    fat_class: float = 90.0
    method: Literal["linear", "quadratic"] = "linear"
    sigma_5t_half: float | None = None
    gamma_mf: float = 1.0

    def validate(self) -> None:
        if self.thickness_mm <= 0:
            raise ValueError(f"thickness_mm debe ser > 0 (recibido {self.thickness_mm})")
        if self.fat_class <= 0:
            raise ValueError(f"fat_class debe ser > 0 (recibido {self.fat_class})")
        if self.gamma_mf <= 0:
            raise ValueError(f"gamma_mf debe ser > 0 (recibido {self.gamma_mf})")


@dataclass(frozen=True)
class HotSpotAnalysisResult:
    """Resultado del analisis HSS."""
    sigma_hot_spot_MPa: float
    weld_type: str
    fat_class: float
    estimated_life_cycles: float
    method: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _fatigue_life(stress_range: float, fat_class: float, gamma_mf: float) -> float:
    """Vida a fatiga N via curva S-N bilineal (EN 1993-1-9 simplificada).

    N = N_c * (FAT_d / sigma_range)^m
    con N_c = 2e6, m = 3, FAT_d = fat_class / gamma_mf.
    """
    fat_d = fat_class / gamma_mf
    if stress_range <= 0:
        return float("inf")
    return 2.0e6 * (fat_d / stress_range) ** 3


def run_hotspot_analysis(
    sigma_t_half: float,
    sigma_3t_half: float,
    thickness_mm: float,
    weld_type: str = "butt",
    fat_class: float = 90.0,
    method: str = "linear",
    sigma_5t_half: float | None = None,
    gamma_mf: float = 1.0,
) -> HotSpotAnalysisResult:
    """Ejecuta analisis HSS completo: extrapolacion + vida a fatiga.

    Args:
        sigma_t_half: tension a t/2 [MPa].
        sigma_3t_half: tension a 3t/2 [MPa].
        thickness_mm: espesor [mm].
        weld_type: tipo de soldadura.
        fat_class: categoria FAT (ej. 90, 100).
        method: 'linear' o 'quadratic'.
        sigma_5t_half: tension a 5t/2 (solo quadratic).
        gamma_mf: factor parcial de seguridad.

    Returns:
        HotSpotAnalysisResult con HSS, categoria FAT y vida estimada.
    """
    from ..hotspot import HotSpotInput, hot_spot_stress

    inp = HotSpotAnalysisInput(
        sigma_t_half=sigma_t_half,
        sigma_3t_half=sigma_3t_half,
        thickness_mm=thickness_mm,
        weld_type=weld_type,
        fat_class=fat_class,
        method=method,
        sigma_5t_half=sigma_5t_half,
        gamma_mf=gamma_mf,
    )
    inp.validate()

    sigma_hs = hot_spot_stress(HotSpotInput(
        sigma_t_half=inp.sigma_t_half,
        sigma_3t_half=inp.sigma_3t_half,
        thickness_mm=inp.thickness_mm,
        method=inp.method,
        sigma_5t_half=inp.sigma_5t_half,
    ))

    life = _fatigue_life(abs(sigma_hs), inp.fat_class, inp.gamma_mf)

    return HotSpotAnalysisResult(
        sigma_hot_spot_MPa=sigma_hs,
        weld_type=inp.weld_type,
        fat_class=inp.fat_class,
        estimated_life_cycles=life,
        method=inp.method,
    )


__all__ = [
    "HotSpotAnalysisInput",
    "HotSpotAnalysisResult",
    "run_hotspot_analysis",
]
