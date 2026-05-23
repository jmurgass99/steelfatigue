"""Servicios de fatiga oligocíclica (LCF) y UFM gusset."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from ..exceptions import ValidationError
from ..lowcycle import (
    CoffinMansonParams,
    CoffinMansonRBS,
    UFMForces,
    UFMGeometry,
    UFMGussetForces,
)


# ---------------------------------------------------------------------
# UFM gusset service
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class UFMInput:
    alpha: float
    beta: float
    ec: float
    eb: float
    P_brace: float
    theta_rad: float


@dataclass(frozen=True)
class UFMResult:
    H_b: float
    V_b: float
    H_c: float
    V_c: float
    equilibrium_ok: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def evaluate_ufm(data: UFMInput) -> UFMResult:
    geom = UFMGeometry(alpha=data.alpha, beta=data.beta,
                       ec=data.ec, eb=data.eb)
    engine = UFMGussetForces(geom)
    forces: UFMForces = engine.interface_forces(data.P_brace, data.theta_rad)
    return UFMResult(
        H_b=forces.H_b, V_b=forces.V_b, H_c=forces.H_c, V_c=forces.V_c,
        equilibrium_ok=engine.equilibrium_check(data.P_brace, data.theta_rad),
    )


# ---------------------------------------------------------------------
# Coffin-Manson RBS service
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class LowCycleInput:
    plastic_rotation_history: list[float] = field(default_factory=list)
    eps_f: float = 0.30
    c: float = -0.60
    geometric_factor: float = 0.50

    def validate(self) -> None:
        if not self.plastic_rotation_history:
            raise ValidationError("plastic_rotation_history vacía")


@dataclass(frozen=True)
class LowCycleResult:
    total_damage: float
    n_cycles: int
    max_plastic_strain: float
    status: str
    message: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def evaluate_lowcycle(data: LowCycleInput) -> LowCycleResult:
    data.validate()
    params = CoffinMansonParams(
        eps_f=data.eps_f, c=data.c, geometric_factor=data.geometric_factor,
    )
    engine = CoffinMansonRBS(params)
    r = engine.evaluate(data.plastic_rotation_history)
    return LowCycleResult(
        total_damage=r.total_damage,
        n_cycles=r.n_cycles,
        max_plastic_strain=r.max_plastic_strain,
        status=r.status,
        message=r.message,
    )


__all__ = [
    "UFMInput", "UFMResult", "evaluate_ufm",
    "LowCycleInput", "LowCycleResult", "evaluate_lowcycle",
]
