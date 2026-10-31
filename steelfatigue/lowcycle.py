"""
lowcycle.py — Low-Cycle Fatigue para conexiones sísmicas.

Dos motores extraídos del Master IEG 3240 (Taller de Diseño de Acero):

1. :class:`UFMGussetForces` — Método de Fuerza Uniforme (Thornton-Muir, AISC
   Manual Part 13) para extraer las fuerzas en las interfaces gusset-viga y
   gusset-columna a partir del esfuerzo en la diagonal. Esas fuerzas son la
   entrada del cálculo de fatiga por la curva S-N (ver
   :class:`steelfatigue.sn_curves.FatigueEvaluator`).

2. :class:`CoffinMansonRBS` — daño oligocíclico (Low-Cycle Fatigue, LCF) sobre
   una historia de rotaciones plásticas en conexiones RBS (Reduced Beam
   Section), siguiendo Coffin-Manson y la base experimental de Engelhardt
   (2007). Útil para evaluar la conexión bajo demanda sísmica severa cuando
   la curva S-N de alto ciclo deja de aplicar.

Convenciones del paquete: unidades SI coherentes, type hints, sin estado
global, excepciones derivadas de :class:`steelfatigue.exceptions.FatigueError`.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import cos, isfinite, sin
from typing import Sequence

import numpy as np

from .exceptions import ValidationError


# ----------------------------------------------------------------------
# UFM — Uniform Force Method
# ----------------------------------------------------------------------

@dataclass(frozen=True)
class UFMGeometry:
    """Geometría de la conexión gusset según UFM (AISC Manual Part 13).

    Args:
        alpha: distancia del centroide de la cara del gusset al eje de la
            columna [longitud].
        beta: distancia del centroide de la cara del gusset al eje de la
            viga [longitud].
        ec: media profundidad de la columna (excentricidad horizontal) [longitud].
        eb: media profundidad de la viga (excentricidad vertical) [longitud].

    La restricción de equilibrio UFM, ``alpha - beta·tan(θ) = ec·tan(θ) - eb``,
    debe satisfacerse para que las interfaces queden libres de momento.
    """

    alpha: float
    beta: float
    ec: float
    eb: float

    def validate(self) -> None:
        for name, value in (
            ("alpha", self.alpha), ("beta", self.beta),
            ("ec", self.ec), ("eb", self.eb),
        ):
            if value < 0 or not isfinite(value):
                raise ValidationError(f"{name} debe ser finito y ≥ 0 (recibido {value})")
        if self.alpha + self.beta <= 0:
            raise ValidationError("alpha + beta debe ser > 0")

    def constraint_residual(self, theta_rad: float) -> float:
        """Residuo de la restricción de equilibrio UFM (debe ≈ 0)."""
        return self.alpha - self.beta * np.tan(theta_rad) - (
            self.ec * np.tan(theta_rad) - self.eb
        )

    def implied_theta(self) -> float:
        """Ángulo de la diagonal implícito por la geometría sin momentos
        en las interfaces: ``tan θ = (β+eb)/(α+ec)``."""
        return float(np.arctan2(self.beta + self.eb, self.alpha + self.ec))


@dataclass(frozen=True)
class UFMForces:
    """Fuerzas en las interfaces gusset-viga y gusset-columna."""

    H_b: float  # cortante horizontal en interfaz gusset-viga
    V_b: float  # axial vertical en interfaz gusset-viga
    H_c: float  # axial horizontal en interfaz gusset-columna
    V_c: float  # cortante vertical en interfaz gusset-columna

    def to_dict(self) -> dict[str, float]:
        return {"H_b": self.H_b, "V_b": self.V_b, "H_c": self.H_c, "V_c": self.V_c}


class UFMGussetForces:
    """Método de Fuerza Uniforme (UFM) para placas gusset (AISC Part 13).

    Examples:
        >>> geom = UFMGeometry(alpha=380, beta=305, ec=152, eb=178)
        >>> ufm = UFMGussetForces(geom)
        >>> forces = ufm.interface_forces(P_brace=900e3, theta_rad=np.radians(42))
        >>> forces.H_b + forces.H_c  # ≈ P_brace · cos θ
    """

    def __init__(self, geometry: UFMGeometry):
        geometry.validate()
        self.geometry = geometry

    def interface_forces(self, P_brace: float,
                          theta_rad: float | None = None) -> UFMForces:
        """Calcula las fuerzas en las cuatro interfaces (sin momentos).

        Args:
            P_brace: esfuerzo axial en la diagonal (tracción positiva).
            theta_rad: ángulo de la diagonal respecto a la horizontal (rad).
                Si es None, se toma el implícito por la geometría
                (``arctan((β+eb)/(α+ec))``). Si se pasa explícito y no
                satisface la restricción UFM, igual se calcula pero
                :meth:`equilibrium_check` lo señalará.

        Notas:
            Convenciones: H_b, H_c son horizontales; V_b, V_c verticales.
            La restricción del UFM garantiza ΣH = P·cosθ, ΣV = P·sinθ
            cuando ``α, β, ec, eb`` y θ son consistentes.
        """
        if not isfinite(P_brace):
            raise ValidationError("P_brace debe ser finito")
        if theta_rad is None:
            theta_rad = self.geometry.implied_theta()
        if not isfinite(theta_rad):
            raise ValidationError("theta_rad debe ser finito")

        g = self.geometry
        r = np.hypot(g.alpha + g.ec, g.beta + g.eb)
        if r <= 0:
            raise ValidationError("Geometría degenerada: r = 0")

        # Componentes (sin momento en las interfaces) — Thornton-Muir.
        return UFMForces(
            H_b=(g.alpha / r) * P_brace,
            V_b=(g.eb / r) * P_brace,
            H_c=(g.ec / r) * P_brace,
            V_c=(g.beta / r) * P_brace,
        )

    def equilibrium_check(self, P_brace: float,
                          theta_rad: float | None = None,
                          atol_rel: float = 1e-6) -> bool:
        """Verifica que la geometría satisfaga el UFM con el θ dado.

        Si ``theta_rad`` es None, el chequeo siempre pasa (la geometría
        define el θ). Si se pasa explícito, compara con ``implied_theta``.
        """
        if theta_rad is None:
            return True
        implied = self.geometry.implied_theta()
        return abs(theta_rad - implied) < max(atol_rel, atol_rel * abs(implied))


# ----------------------------------------------------------------------
# Coffin-Manson — daño oligocíclico en RBS
# ----------------------------------------------------------------------

@dataclass(frozen=True)
class CoffinMansonParams:
    """Parámetros de la curva ε_p–N (Coffin-Manson).

    Defaults calibrados a acero estructural ASTM A992 (Engelhardt 2007 / FEMA 350).

    Args:
        eps_f: coeficiente de ductilidad a fatiga (intersección a N=1).
        c: exponente de ductilidad a fatiga (típicamente -0.5 .. -0.7).
        geometric_factor: relación rotación plástica → deformación plástica
            en el ala del RBS. Engelhardt sugiere ~0.5·(d/L_p).
    """

    eps_f: float = 0.30
    c: float = -0.60
    geometric_factor: float = 0.50

    def validate(self) -> None:
        if self.eps_f <= 0:
            raise ValidationError(f"eps_f debe ser > 0 (recibido {self.eps_f})")
        if self.c >= 0:
            raise ValidationError(f"c debe ser < 0 (recibido {self.c})")
        if self.geometric_factor <= 0:
            raise ValidationError(
                f"geometric_factor debe ser > 0 (recibido {self.geometric_factor})"
            )


@dataclass(frozen=True)
class LowCycleDamageResult:
    """Resultado de la evaluación oligocíclica."""

    total_damage: float
    n_cycles: int
    max_plastic_strain: float
    status: str
    message: str

    def to_dict(self) -> dict[str, float | int | str]:
        return {
            "total_damage": self.total_damage,
            "n_cycles": self.n_cycles,
            "max_plastic_strain": self.max_plastic_strain,
            "status": self.status,
            "message": self.message,
        }


class CoffinMansonRBS:
    """Evaluador de fatiga oligocíclica en conexiones RBS.

    Aplica Coffin-Manson sobre la historia de amplitudes de rotación
    plástica y suma daño con Palmgren-Miner.

    Examples:
        >>> rbs = CoffinMansonRBS()
        >>> rot = np.array([0.01, 0.02, 0.015, 0.025, 0.03])
        >>> result = rbs.evaluate(rot)
        >>> result.status
        'OK'
    """

    def __init__(self, params: CoffinMansonParams | None = None):
        self.params = params or CoffinMansonParams()
        self.params.validate()

    def cycles_to_failure(self, plastic_strain: float) -> float:
        """N_f a partir de la amplitud de deformación plástica.

        ``ε_p = ε_f · (2·N_f)^c``  →  ``N_f = 0.5 · (ε_p / ε_f)^(1/c)``.
        """
        if plastic_strain <= 0:
            return float("inf")
        p = self.params
        return 0.5 * (plastic_strain / p.eps_f) ** (1.0 / p.c)

    def evaluate(self, plastic_rotation_history: Sequence[float]) -> LowCycleDamageResult:
        """Suma daño de Miner sobre la historia de rotaciones plásticas."""
        arr = np.asarray(list(plastic_rotation_history), dtype=float)
        if arr.size == 0:
            raise ValidationError("plastic_rotation_history vacía")
        if np.any(arr < 0):
            raise ValidationError(
                "rotaciones plásticas deben ser amplitudes ≥ 0 (usa |Δθ_p|)"
            )

        strain = arr * self.params.geometric_factor
        # np.where evalúa las dos ramas: para strain = 0 la potencia negativa
        # dispara un aviso de división por cero aunque el resultado se descarte.
        with np.errstate(divide="ignore"):
            nf = np.where(strain > 0,
                          0.5 * (strain / self.params.eps_f) ** (1.0 / self.params.c),
                          np.inf)
        damage = float(np.sum(1.0 / nf))

        if damage >= 1.0:
            status, msg = "FAILED", f"Daño acumulado {damage:.2f} ≥ 1.0 — falla esperada"
        elif damage >= 0.5:
            status, msg = "WARN", f"Daño {damage:.2f} > 0.5 — vida útil consumida en >50%"
        else:
            status, msg = "OK", f"Daño {damage:.3f} < 0.5"

        return LowCycleDamageResult(
            total_damage=damage,
            n_cycles=int(arr.size),
            max_plastic_strain=float(strain.max(initial=0.0)),
            status=status,
            message=msg,
        )


__all__ = [
    "UFMGeometry",
    "UFMForces",
    "UFMGussetForces",
    "CoffinMansonParams",
    "LowCycleDamageResult",
    "CoffinMansonRBS",
]
