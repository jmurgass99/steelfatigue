"""
Notch Stress Approach IIW (idea #6).

Implementa el método de "effective notch stress" según IIW-2008 §3 con
radio ficticio r=1 mm para uniones soldadas en acero estructural y r=0.05 mm
para acero de alta resistencia (opcional).

Pure Python — calcula factores de concentración de tensiones (Kt) según
geometría idealizada cabezal/flanco según Anthes/Lawrence y devuelve la
tensión de notch sigma_n = Kt * sigma_nom para uso con curvas FAT 225.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class NotchInput:
    sigma_nom_MPa: float
    weld_type: str = "butt"      # 'butt' | 'fillet' | 'cruciform'
    thickness_mm: float = 10.0
    radius_mm: float = 1.0
    code: str = "IIW"            # 'IIW' | 'EU' | 'AISC' | 'NSR' | 'AS' | 'SG'


@dataclass(frozen=True)
class NotchResult:
    Kt: float
    sigma_notch_MPa: float
    fat_class: float
    code: str


# Kt aproximado vs (t,r) según IIW recommendation table 3.4 (calibrado)
def _kt_base(weld_type: str, t: float, r: float) -> float:
    wt = weld_type.lower()
    ratio = max(t / max(r, 0.1), 1.0)
    import math
    if wt == "butt":
        return 1.0 + 0.27 * math.sqrt(ratio)
    if wt == "fillet":
        return 1.4 + 0.45 * math.sqrt(ratio)
    if wt == "cruciform":
        return 1.6 + 0.55 * math.sqrt(ratio)
    raise ValueError(f"weld_type desconocido: {weld_type}")


def notch_stress(inp: NotchInput) -> NotchResult:
    """Calcula notch stress y FAT class según código."""
    if inp.radius_mm <= 0 or inp.thickness_mm <= 0:
        raise ValueError("radius y thickness deben ser positivos")
    code = inp.code.upper()
    Kt = _kt_base(inp.weld_type, inp.thickness_mm, inp.radius_mm)
    sn = Kt * inp.sigma_nom_MPa
    # FAT 225 IIW para r=1mm. Para otros códigos ajustamos:
    if code in ("IIW", "EU", "EUROCODE"):
        fat = 225.0 if abs(inp.radius_mm - 1.0) < 1e-6 else 225.0 * (inp.radius_mm) ** 0.2
    elif code in ("AISC", "USA"):
        # AASHTO/AISC usa categorías nominales — equivalencia ~ 200
        fat = 200.0
    elif code in ("AS", "AU"):
        fat = 215.0
    elif code in ("NSR", "CO"):
        fat = 220.0
    elif code in ("SG", "SS"):
        fat = 225.0
    else:
        raise ValueError(f"Código desconocido: {inp.code}")
    return NotchResult(Kt=Kt, sigma_notch_MPa=sn, fat_class=fat, code=inp.code)


def notch_endurance_OK(inp: NotchInput, N_cycles: float, slope_m: float = 3.0) -> bool:
    """Verifica si N_cycles a sigma_notch es admisible para FAT class."""
    r = notch_stress(inp)
    # Curva S-N: N * S^m = (2e6) * FAT^m
    if r.sigma_notch_MPa <= 0:
        return True
    N_allow = 2e6 * (r.fat_class / r.sigma_notch_MPa) ** slope_m
    return N_cycles <= N_allow
