"""Pruebas del servicio de evaluacion de fatiga."""
from __future__ import annotations

import pytest

from fatiguejm.exceptions import DetailCategoryError, SpectrumError
from fatiguejm.services import (
    FatigueInput,
    FatigueResult,
    StressBlock,
    evaluate_fatigue,
)


def _build_input(
    spectrum: list[dict[str, float]],
    detail_category: float = 90.0,
    gamma_mf: float = 1.35,
) -> FatigueInput:
    blocks = [StressBlock(**b) for b in spectrum]
    return FatigueInput(
        detail_category=detail_category, gamma_mf=gamma_mf, spectrum=blocks
    )


@pytest.mark.unit
def test_evaluate_fatigue_pass(spectrum_simple: list[dict[str, float]]) -> None:
    result = evaluate_fatigue(_build_input(spectrum_simple))
    assert isinstance(result, FatigueResult)
    assert result.status in ("PASS", "FAIL")
    assert result.total_damage >= 0
    assert result.detail_category == 90.0


@pytest.mark.unit
def test_evaluate_fatigue_fail_alta_tension() -> None:
    spectrum = [{"stress_range": 300.0, "cycles": 1.0e7}]
    result = evaluate_fatigue(_build_input(spectrum, detail_category=71.0))
    assert result.status == "FAIL"
    assert result.total_damage > 1.0


@pytest.mark.unit
def test_detail_category_invalida() -> None:
    with pytest.raises(DetailCategoryError):
        evaluate_fatigue(
            _build_input([{"stress_range": 50.0, "cycles": 1e4}], detail_category=0.0)
        )


@pytest.mark.unit
def test_espectro_vacio() -> None:
    with pytest.raises(SpectrumError):
        evaluate_fatigue(FatigueInput(detail_category=90.0, spectrum=[]))


@pytest.mark.unit
def test_bloque_negativo_lanza_spectrum_error() -> None:
    with pytest.raises(SpectrumError):
        evaluate_fatigue(
            _build_input([{"stress_range": -10.0, "cycles": 1e3}])
        )


@pytest.mark.unit
def test_resultado_serializable(spectrum_simple: list[dict[str, float]]) -> None:
    result = evaluate_fatigue(_build_input(spectrum_simple))
    d = result.to_dict()
    assert set(d.keys()) == {"detail_category", "total_damage", "status", "message"}
