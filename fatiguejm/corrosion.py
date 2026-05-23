"""
Factor de reducción de curva S-N por corrosión — IIW recomendaciones.

Categoría ambiental:
    seawater          — pérdida 50% en categoría FAT (factor 0.5)
    marine_atmosphere — 0.7
    industrial        — 0.8
    rural             — 1.0
"""
from __future__ import annotations


CORROSION_FACTORS: dict[str, float] = {
    "seawater":          0.50,
    "marine_atmosphere": 0.70,
    "industrial":        0.80,
    "urban":             0.85,
    "rural":             1.00,
}


def adjusted_FAT(delta_sigma_C_MPa: float, environment: str) -> float:
    """Devuelve Δσ_C reducido por ambiente corrosivo."""
    if environment not in CORROSION_FACTORS:
        raise ValueError(
            f"environment '{environment}' no soportado; "
            f"opciones: {list(CORROSION_FACTORS)}"
        )
    return delta_sigma_C_MPa * CORROSION_FACTORS[environment]


__all__ = ["CORROSION_FACTORS", "adjusted_FAT"]
