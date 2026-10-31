"""
Corrección por tensión media en fatiga de alto ciclo.

Criterios clásicos del diagrama de Haigh (Shigley, *Mechanical Engineering
Design*, §6-12; Juvinall §8): convierten una combinación de amplitud de tensión
``sigma_a`` y tensión media ``sigma_m`` en un factor de seguridad ``n`` frente a
fallo por fatiga, o en una tensión equivalente totalmente alternada ``sigma_ar``
(para usar con una curva S-N R=-1).

Criterios implementados:
  - Soderberg     : sigma_a/Se + sigma_m/Sy = 1/n        (conservador, usa fluencia)
  - Goodman mod.  : sigma_a/Se + sigma_m/Su = 1/n        (el más usado)
  - Gerber        : n·sigma_a/Se + (n·sigma_m/Su)^2 = 1  (parabólico, dúctiles)
  - ASME-elíptico : (n·sigma_a/Se)^2 + (n·sigma_m/Sy)^2 = 1
  - Langer (1er ciclo): sigma_a + sigma_m = Sy → n = Sy/(sigma_a+sigma_m)

Convención: tracción media positiva es perjudicial. Para sigma_m < 0 (media de
compresión) la mayoría de criterios son no conservadores; se acota a sigma_m>=0
en el factor de Goodman/Soderberg salvo que el llamador pida lo contrario.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict

from .exceptions import ValidationError


@dataclass(frozen=True)
class MeanStressInput:
    sigma_a_MPa: float          # amplitud de tensión (>0)
    sigma_m_MPa: float          # tensión media (tracción +)
    Se_MPa: float               # límite de fatiga corregido (R=-1)
    Su_MPa: float               # resistencia última a tracción
    Sy_MPa: float | None = None  # límite elástico (requerido para Soderberg/ASME/Langer)

    def validate(self) -> None:
        if self.sigma_a_MPa < 0:
            raise ValidationError("sigma_a debe ser >= 0")
        if self.Se_MPa <= 0 or self.Su_MPa <= 0:
            raise ValidationError("Se y Su deben ser > 0")


def equivalent_reversed_stress(sigma_a: float, sigma_m: float, Su: float,
                               criterion: str = "goodman", Sy: float | None = None) -> float:
    """Tensión totalmente alternada equivalente sigma_ar (R=-1) para una curva S-N.

    Goodman:   sigma_ar = sigma_a / (1 - sigma_m/Su)
    Soderberg: sigma_ar = sigma_a / (1 - sigma_m/Sy)
    Gerber:    sigma_ar = sigma_a / (1 - (sigma_m/Su)^2)
    Para sigma_m <= 0 (compresión) se devuelve sigma_a (sin penalización).
    """
    if sigma_m <= 0:
        return sigma_a
    crit = criterion.lower()
    if crit == "goodman":
        denom = 1.0 - sigma_m / Su
    elif crit == "gerber":
        denom = 1.0 - (sigma_m / Su) ** 2
    elif crit == "soderberg":
        if not Sy:
            raise ValidationError("Soderberg requiere Sy")
        denom = 1.0 - sigma_m / Sy
    else:
        raise ValidationError("criterio desconocido: %s" % criterion)
    if denom <= 0:
        return float("inf")  # la media sola ya supera la resistencia estática
    return sigma_a / denom


def safety_factors(data: MeanStressInput) -> Dict[str, float]:
    """Factores de seguridad a fatiga por cada criterio del diagrama de Haigh.

    Devuelve un dict {criterio: n}. ``n`` < 1 indica fallo previsto.
    """
    data.validate()
    sa, sm = data.sigma_a_MPa, data.sigma_m_MPa
    Se, Su, Sy = data.Se_MPa, data.Su_MPa, data.Sy_MPa
    out: Dict[str, float] = {}

    # Goodman modificado.
    g = sa / Se + max(sm, 0.0) / Su
    out["goodman"] = (1.0 / g) if g > 0 else float("inf")

    # Gerber (parabólico): resolver n de  n·sa/Se + (n·sm/Su)^2 = 1.
    if sm > 0:
        r = (Su / sm) ** 2
        out["gerber"] = 0.5 * r * (sa / Se) * (-1.0 + math.sqrt(1.0 + (2.0 * sm * Se / (Su * sa)) ** 2))
    else:
        out["gerber"] = Se / sa if sa > 0 else float("inf")

    # Soderberg (usa fluencia).
    if Sy:
        s = sa / Se + max(sm, 0.0) / Sy
        out["soderberg"] = (1.0 / s) if s > 0 else float("inf")
        # ASME-elíptico.
        e = (sa / Se) ** 2 + (max(sm, 0.0) / Sy) ** 2
        out["asme_elliptic"] = (1.0 / math.sqrt(e)) if e > 0 else float("inf")
        # Langer (fluencia de primer ciclo).
        out["langer"] = Sy / (sa + abs(sm)) if (sa + abs(sm)) > 0 else float("inf")

    return out


__all__ = ["MeanStressInput", "equivalent_reversed_stress", "safety_factors"]
