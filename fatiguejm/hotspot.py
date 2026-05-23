"""
Hot-Spot Stress (HSS) — extrapolación lineal/cuadrática IIW (2008) para
evitar leer tensiones en singularidades nodales (gotcha #8). Usado en
soldaduras y uniones marco-shell donde el FEM genera picos artificiales.

Convención IIW: hot-spot a t/2 y 3t/2 desde el cordón (Tipo "a", lineal).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Sequence


@dataclass(frozen=True)
class HotSpotInput:
    """Tensiones leídas a las distancias de referencia desde el cordón.

    Args:
        sigma_t_half: tensión a t/2 [MPa].
        sigma_3t_half: tensión a 3t/2 [MPa].
        thickness_mm: espesor de la placa [mm].
        method: 'linear' (IIW Tipo a) o 'quadratic' (IIW Tipo b).
        sigma_5t_half: tensión a 5t/2 (sólo para 'quadratic').
    """
    sigma_t_half: float
    sigma_3t_half: float
    thickness_mm: float
    method: Literal["linear", "quadratic"] = "linear"
    sigma_5t_half: float | None = None


def hot_spot_stress(data: HotSpotInput) -> float:
    """Extrapolación al borde del cordón (distancia 0).

    Lineal IIW: ``σ_hs = 1.67·σ(t/2) - 0.67·σ(3t/2)``.
    Cuadrática IIW: ``σ_hs = 2.52·σ(t/2) - 2.24·σ(3t/2) + 0.72·σ(5t/2)``.
    """
    if data.thickness_mm <= 0:
        raise ValueError("thickness_mm debe ser > 0")
    if data.method == "linear":
        return 1.67 * data.sigma_t_half - 0.67 * data.sigma_3t_half
    if data.method == "quadratic":
        if data.sigma_5t_half is None:
            raise ValueError("método quadratic requiere sigma_5t_half")
        return (2.52 * data.sigma_t_half
                - 2.24 * data.sigma_3t_half
                + 0.72 * data.sigma_5t_half)
    raise ValueError(f"método '{data.method}' no soportado")


def hot_spot_from_radial_samples(stresses: Sequence[float],
                                  radii_mm: Sequence[float],
                                  thickness_mm: float,
                                  hot_spot_distance_mm: float = 0.0
                                  ) -> float:
    """Cuando el FEM da tensiones a distancias arbitrarias, interpola
    linealmente los dos puntos más cercanos a ``hot_spot_distance_mm``.

    Útil como fallback cuando no tienes muestras exactas a t/2 y 3t/2.
    """
    if len(stresses) != len(radii_mm) or len(stresses) < 2:
        raise ValueError("Necesario ≥2 puntos con misma longitud")
    pairs = sorted(zip(radii_mm, stresses))
    # Encontrar los dos puntos que rodean hot_spot_distance
    for i in range(len(pairs) - 1):
        r1, s1 = pairs[i]
        r2, s2 = pairs[i + 1]
        if r1 <= hot_spot_distance_mm <= r2:
            if r2 == r1:
                return s1
            return s1 + (s2 - s1) * (hot_spot_distance_mm - r1) / (r2 - r1)
    # Extrapolar usando los dos primeros
    r1, s1 = pairs[0]
    r2, s2 = pairs[1]
    if r2 == r1:
        return s1
    return s1 + (s2 - s1) * (hot_spot_distance_mm - r1) / (r2 - r1)


__all__ = ["HotSpotInput", "hot_spot_stress", "hot_spot_from_radial_samples"]
