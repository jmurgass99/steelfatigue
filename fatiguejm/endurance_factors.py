"""
Factores modificadores del límite de fatiga (factores de Marin).

Shigley, *Mechanical Engineering Design* §6-9..6-18 (unidades SI, MPa):

    Se = ka * kb * kc * kd * ke * Se'

donde Se' es el límite de fatiga de probeta de viga rotatoria pulida y los
factores corrigen por superficie (ka), tamaño (kb), tipo de carga (kc),
temperatura (kd) y confiabilidad (ke). Útil para el camino de fatiga por
tensión-vida (componentes), complementario a las curvas S-N por categoría de
detalle de los códigos estructurales.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from .exceptions import ValidationError

# ka = a * Su^b  (Su en MPa) — Shigley Tabla 6-2.
_SURFACE = {
    "ground":      (1.58, -0.085),
    "machined":    (4.51, -0.265),
    "cold-drawn":  (4.51, -0.265),
    "hot-rolled":  (57.7, -0.718),
    "as-forged":   (272.0, -0.995),
}

# ke por confiabilidad — Shigley Tabla 6-5.
_RELIABILITY = {
    0.50: 1.000, 0.90: 0.897, 0.95: 0.868, 0.99: 0.814,
    0.999: 0.753, 0.9999: 0.702, 0.99999: 0.659, 0.999999: 0.620,
}


def Se_prime(Su_MPa: float) -> float:
    """Límite de fatiga de viga rotatoria Se' (Shigley Eq 6-10): 0.5·Su, tope 700 MPa."""
    if Su_MPa <= 0:
        raise ValidationError("Su debe ser > 0")
    return 0.5 * Su_MPa if Su_MPa <= 1400.0 else 700.0


def ka_surface(Su_MPa: float, finish: str = "machined") -> float:
    """Factor de superficie ka = a·Su^b (Shigley Tabla 6-2)."""
    key = finish.lower()
    if key not in _SURFACE:
        raise ValidationError("acabado desconocido: %s (válidos: %s)" % (finish, sorted(_SURFACE)))
    a, b = _SURFACE[key]
    return a * Su_MPa ** b


def kb_size(d_mm: float, loading: str = "bending", rotating: bool = True) -> float:
    """Factor de tamaño kb (Shigley Eq 6-20/6-21).

    Carga axial -> kb = 1. Flexión/torsión rotatoria usa d directamente; para
    secciones no rotatorias o no circulares conviene un diámetro equivalente
    (no implementado aquí: pasar d_e si ya lo tienes).
    """
    if loading.lower() == "axial":
        return 1.0
    if d_mm <= 0:
        raise ValidationError("d debe ser > 0")
    if 2.79 <= d_mm <= 51.0:
        return 1.24 * d_mm ** -0.107
    if 51.0 < d_mm <= 254.0:
        return 1.51 * d_mm ** -0.157
    # Fuera de rango: extiende la 2ª rama (conservador) o devuelve ~ a d=2.79.
    if d_mm < 2.79:
        return 1.24 * 2.79 ** -0.107
    return 1.51 * d_mm ** -0.157


def kc_load(loading: str = "bending") -> float:
    """Factor de tipo de carga kc (Shigley Eq 6-26): flexión 1, axial 0.85, torsión 0.59."""
    return {"bending": 1.0, "axial": 0.85, "torsion": 0.59}.get(loading.lower(), 1.0)


def kd_temperature(T_C: float) -> float:
    """Factor de temperatura kd (Shigley Eq 6-27, ajuste polinómico, T en °F).

    kd = 0.975 + 0.432e-3·Tf − 0.115e-5·Tf² + 0.104e-8·Tf³ − 0.595e-12·Tf⁴
    Válido ~ 20..540 °C. A 20 °C devuelve ~1.0.
    """
    Tf = T_C * 9.0 / 5.0 + 32.0
    kd = (0.975 + 0.432e-3 * Tf - 0.115e-5 * Tf ** 2
          + 0.104e-8 * Tf ** 3 - 0.595e-12 * Tf ** 4)
    return kd


def ke_reliability(reliability: float = 0.50) -> float:
    """Factor de confiabilidad ke (Shigley Tabla 6-5). Interpola al valor tabulado más cercano por debajo."""
    if reliability in _RELIABILITY:
        return _RELIABILITY[reliability]
    # Toma el ke del nivel tabulado <= solicitado más alto (conservador).
    candidates = [r for r in _RELIABILITY if r <= reliability + 1e-9]
    if not candidates:
        return 1.0
    return _RELIABILITY[max(candidates)]


@dataclass(frozen=True)
class EnduranceInput:
    Su_MPa: float
    finish: str = "machined"
    d_mm: float = 10.0
    loading: str = "bending"
    T_C: float = 20.0
    reliability: float = 0.50
    rotating: bool = True


def endurance_limit(inp: EnduranceInput) -> Dict[str, float]:
    """Se corregido y todos los factores de Marin.

    Returns dict: ka, kb, kc, kd, ke, Se_prime_MPa, Se_MPa.
    """
    if inp.Su_MPa <= 0:
        raise ValidationError("Su debe ser > 0")
    sep = Se_prime(inp.Su_MPa)
    ka = ka_surface(inp.Su_MPa, inp.finish)
    kb = kb_size(inp.d_mm, inp.loading, inp.rotating)
    kc = kc_load(inp.loading)
    kd = kd_temperature(inp.T_C)
    ke = ke_reliability(inp.reliability)
    Se = ka * kb * kc * kd * ke * sep
    return {"ka": ka, "kb": kb, "kc": kc, "kd": kd, "ke": ke,
            "Se_prime_MPa": sep, "Se_MPa": Se}


__all__ = [
    "Se_prime", "ka_surface", "kb_size", "kc_load", "kd_temperature",
    "ke_reliability", "EnduranceInput", "endurance_limit",
]
