"""Golden — integración de Paris frente a la forma cerrada con Y constante.

Para da/dN = C·(Y·Δσ·√(π·a))^m con Y constante y m ≠ 2, la vida entre a_i y a_c
tiene solución cerrada (a en metros, ΔK en MPa·√m, da/dN en m/ciclo):

    N = 2 / [(m − 2)·C·(Y·Δσ·√π)^m] · [a_i^(1 − m/2) − a_c^(1 − m/2)]

Caso: grieta de borde a_i = 2 mm → a_c = 40 mm, Δσ = 80 MPa, Y = 1,12,
C = 6,9·10⁻¹² (Barsom & Rolfe, m/ciclo con ΔK en MPa·√m), m = 3:

    Y·Δσ·√π = 1,12·80·1,7724539 = 158,8119
    (…)³ = 4,00536·10⁶ ;  C·(…)³ = 2,76370·10⁻⁵ ;  2/(1·2,76370·10⁻⁵) = 72 367
    a_i^(−1/2) − a_c^(−1/2) = 0,002^(−0,5) − 0,040^(−0,5) = 22,3607 − 5,0000 = 17,3607
    N = 72 367 · 17,3607 = 1,2563·10⁶ ciclos

El valor se derivó a mano antes de ejecutar el código. Hasta 2026-10-31 el módulo
evaluaba ΔK en MPa·√mm con la misma C y devolvía N ≈ 4,0·10⁴ (÷31,6 = √1000);
este test fija la corrección de unidades.
"""
from __future__ import annotations

import math

import pytest

from steelfatigue.paris_law import ParisInput, integrate_paris

A_I_M, A_C_M = 0.002, 0.040
DS, Y, C, M = 80.0, 1.12, 6.9e-12, 3.0


def _closed_form_cycles() -> float:
    k = Y * DS * math.sqrt(math.pi)
    return 2.0 / ((M - 2.0) * C * k ** M) * (A_I_M ** (1 - M / 2) - A_C_M ** (1 - M / 2))


def test_paris_matches_closed_form_within_discretisation_error():
    res = integrate_paris(ParisInput(a_initial_mm=A_I_M * 1e3, a_critical_mm=A_C_M * 1e3,
                                     delta_sigma_MPa=DS, Y=Y, C=C, m=M, n_increments=2000))
    expected = _closed_form_cycles()
    assert expected == pytest.approx(1.2563e6, rel=1e-3)        # derivación a mano
    assert res.N_cycles == pytest.approx(expected, rel=1e-2)     # suma de Riemann por la izquierda
    assert res.N_cycles > expected                               # el integrando decrece: sobreestima levemente


def test_paris_life_is_not_divided_by_sqrt_1000():
    """Guarda contra la regresión de unidades (MPa·√mm con C en MPa·√m)."""
    res = integrate_paris(ParisInput(a_initial_mm=2.0, a_critical_mm=40.0, delta_sigma_MPa=80.0))
    assert res.N_cycles > 1.0e6
    assert res.N_cycles < 1.4e6


def test_paris_life_scales_with_delta_sigma_to_the_minus_m():
    n80 = integrate_paris(ParisInput(2.0, 40.0, 80.0, n_increments=1000)).N_cycles
    n40 = integrate_paris(ParisInput(2.0, 40.0, 40.0, n_increments=1000)).N_cycles
    assert n40 / n80 == pytest.approx(2.0 ** 3, rel=1e-9)
