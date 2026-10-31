"""Golden tests — rotura frágil EN 1993-1-10 (`steelfatigue.ec3_brittle_fracture`).

Ancla el único ejemplo COMPLETO de EC3-1-10 encontrado en la campaña de
extracción de fichas, confirmado por DOS transcripciones independientes del
mismo examen (mismo enunciado, mismo resultado manuscrito):

- **W01468** (Ex Fatigue 2 — Fatiga y Rotura Frágil IPE 500/S355JR, examen
  UPC 2020-03-30).
- **W01469** (Ex Fatigue 2, transcripción independiente de la misma
  convocatoria — mismos números al decimal).

Viga biapoyada con voladizo, IPE 500 (W_el,y=1928.1 cm³, t_f=16.0mm), S355JR.
T₀=−35°C → T_ref=−40°C. Carga P₂=200 kN en el extremo del voladizo (D)
produce el momento máximo en el empotramiento (sección C):

    M_max = P₂ · l_v = 200 kN · 2 m = 400 kN·m
    σ_max = M_max / W_el,y = 400e6 / 1,928,100 = 207.46 N/mm²
    f_y(t) = f_y − 0.25·t_f = 355 − 0.25·16 = 351 N/mm²
    σ_max / f_y(t) = 207.46 / 351 = 0.591

Tabla EC3-1-10 (S355JR, T_ref=−40°C) — dos puntos calibrados transcritos
literalmente por ambas fichas: (ratio=0.50 → t_max=25mm), (ratio=0.75 →
t_max=15mm). Interpolando linealmente en ratio=0.591:

    t_max ≈ 25 − 40·(0.591 − 0.50) ≈ 21.4 mm > t_f = 16.0 mm → VERIFICA

Recalculado a mano (ver script de verificación en el informe de la tarea)
ANTES de anclar: t_max=21.36mm con la ratio sin redondear (207.458/351 en vez
de 0.59), coincide con el 21.4mm de la ficha dentro del margen de redondeo de
un cálculo manual — NO hay errata aquí, las dos fichas independientes
concuerdan y el recálculo confirma el mismo orden de magnitud y conclusión
(t_max > t_f, verifica).

Nota de alcance: la tabla completa EC3-1-10 (todos los T_Ed y subgrados) NO
está en el workspace; `interpolate_max_thickness` recibe los puntos como
parámetro en vez de traer un catálogo inventado (regla de oro: no inventar
lo que no está anclado por una ficha).
"""
import pytest

from steelfatigue.ec3_brittle_fracture import (
    EC3110_DELTA_TR_DEFAULT_C,
    brittle_fracture_check,
    interpolate_max_thickness,
    reduced_yield_strength,
    reference_temperature,
)

# Puntos de tabla EC3-1-10 para S355JR a T_ref=-40°C, transcritos literalmente
# por W01468/W01469: (ratio sigma/fy(t), t_max_mm).
_TABLA_S355JR_MENOS40C = [(0.50, 25.0), (0.75, 15.0)]

_W_IPE500_mm3 = 1928.1e3
_L_VOLADIZO_mm = 2000.0


def test_reference_temperature_golden_W01468_W01469():
    # T0=-35°C, ΔT_r=5°C → T_ref=-40°C (valor usado en ambas fichas).
    assert reference_temperature(-35.0) == pytest.approx(-40.0, abs=1e-9)
    assert EC3110_DELTA_TR_DEFAULT_C == 5.0


def test_reduced_yield_strength_golden_W01468_W01469():
    # f_y(t) = 355 - 0.25*16 = 351 MPa (IPE 500, t_f=16mm, S355JR).
    assert reduced_yield_strength(355.0, 16.0) == pytest.approx(351.0, abs=1e-9)


def test_interpolate_max_thickness_golden_W01468_W01469():
    # ratio=0.591 (sin redondear) -> t_max ~21.36mm; ficha redondea a 21.4mm
    # tras redondear antes la ratio a 0.59. Ambos coinciden dentro de 0.1mm.
    ratio = 207.46 / 351.0
    t_max = interpolate_max_thickness(ratio, _TABLA_S355JR_MENOS40C)
    assert t_max == pytest.approx(21.4, abs=0.1)

    # Coherencia interna: en los puntos exactos de tabla se recupera el valor
    # tabulado (sin desviación de interpolación).
    assert interpolate_max_thickness(0.50, _TABLA_S355JR_MENOS40C) == pytest.approx(25.0)
    assert interpolate_max_thickness(0.75, _TABLA_S355JR_MENOS40C) == pytest.approx(15.0)


def test_interpolate_max_thickness_fuera_de_rango_lanza_error():
    # No se extrapola fuera de los puntos calibrados (regla de oro: no
    # inventar valores de tabla que no están anclados por ninguna ficha).
    with pytest.raises(ValueError):
        interpolate_max_thickness(0.10, _TABLA_S355JR_MENOS40C)
    with pytest.raises(ValueError):
        interpolate_max_thickness(0.95, _TABLA_S355JR_MENOS40C)


def test_brittle_fracture_check_verifica_golden_W01468_W01469():
    # Sección C (empotramiento del voladizo): M_max = P2*l_v = 200kN*2m = 400kN*m.
    P2_N = 200_000.0
    M_max_Nmm = P2_N * _L_VOLADIZO_mm
    sigma_max = M_max_Nmm / _W_IPE500_mm3
    assert sigma_max == pytest.approx(207.46, abs=0.05)

    res = brittle_fracture_check(
        sigma_MPa=sigma_max,
        fy_MPa=355.0,
        t_mm=16.0,
        table_points=_TABLA_S355JR_MENOS40C,
        T0_C=-35.0,
    )
    assert res.fy_t_MPa == pytest.approx(351.0, abs=1e-6)
    assert res.sigma_over_fy == pytest.approx(0.591, abs=0.001)
    assert res.t_max_admissible_mm == pytest.approx(21.4, abs=0.1)
    assert res.T_ref_C == pytest.approx(-40.0, abs=1e-9)
    # Conclusión de la ficha: t_f=16mm < t_max≈21.4mm → VERIFICA (no rotura frágil).
    assert res.ok is True


def test_brittle_fracture_check_no_verifica_si_espesor_excede_tmax():
    # Caso negativo sintético (no ficha): mismo σ y f_y(t), pero espesor real
    # por encima de t_max -> debe fallar la verificación.
    res = brittle_fracture_check(
        sigma_MPa=207.46,
        fy_MPa=355.0,
        t_mm=25.0,  # > t_max ~21.4mm
        table_points=_TABLA_S355JR_MENOS40C,
    )
    assert res.ok is False
    assert res.T_ref_C is None  # T0_C no se pasó -> no se reporta T_ref
