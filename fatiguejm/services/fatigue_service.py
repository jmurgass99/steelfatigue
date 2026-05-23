"""Servicio de evaluacion de fatiga.

Envuelve :class:`fatiguejm.sn_curves.FatigueEvaluator` con funciones puras
tipadas, validacion y dataclasses serializables.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from ..exceptions import DetailCategoryError, SpectrumError


@dataclass(frozen=True)
class StressBlock:
    """Bloque del espectro de tensiones."""

    stress_range: float
    cycles: float

    def validate(self) -> None:
        if self.stress_range < 0:
            raise SpectrumError(
                f"stress_range no puede ser negativo (recibido {self.stress_range})"
            )
        if self.cycles < 0:
            raise SpectrumError(
                f"cycles no puede ser negativo (recibido {self.cycles})"
            )


@dataclass(frozen=True)
class FatigueInput:
    """Datos de entrada de la evaluacion de fatiga."""

    detail_category: float
    spectrum: list[StressBlock] = field(default_factory=list)
    gamma_mf: float = 1.35

    def validate(self) -> None:
        if self.detail_category <= 0:
            raise DetailCategoryError(
                f"detail_category debe ser > 0 (recibido {self.detail_category})"
            )
        if self.gamma_mf <= 0:
            raise DetailCategoryError(
                f"gamma_mf debe ser > 0 (recibido {self.gamma_mf})"
            )
        if not self.spectrum:
            raise SpectrumError("el espectro no puede estar vacio")
        for block in self.spectrum:
            block.validate()


@dataclass(frozen=True)
class FatigueResult:
    """Resultado de la evaluacion de fatiga."""

    detail_category: float
    total_damage: float
    status: str
    message: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def evaluate_fatigue(data: FatigueInput) -> FatigueResult:
    """Evalua el dano acumulado de Palmgren-Miner y devuelve el informe."""
    data.validate()
    # Lazy import.
    from ..sn_curves import FatigueEvaluator

    evaluator = FatigueEvaluator(
        detail_category=data.detail_category, gamma_mf=data.gamma_mf
    )
    spectrum_dicts = [
        {"stress_range": b.stress_range, "cycles": b.cycles} for b in data.spectrum
    ]
    report = evaluator.evaluation_report(spectrum_dicts)
    return FatigueResult(
        detail_category=float(report["detail_category"]),
        total_damage=float(report["total_damage"]),
        status=str(report["status"]),
        message=str(report["message"]),
    )
