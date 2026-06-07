"""Golden tests — curva S-N trilineal EN 1993-1-9 §7 (`fatiguejm.ec3_sn`).

Valores anclados a fichas máster del workspace (citadas por WorkID):

- **W01419** (Fatigue — EN 1993-1-9, apuntes UPC): define la curva bilineal/
  trilineal §7 y tabula el codo Δσ_D y los puntos de definición:
    N = 2·10⁶·(Δσ_C/Δσ)³            para Δσ ≥ Δσ_D            (m=3)
    Δσ_D = Δσ_C·(2/5)^(1/3) ≈ 0.737·Δσ_C  → codo a N = 5·10⁶
    N = 5·10⁶·(Δσ_D/Δσ)⁵            para Δσ_L ≤ Δσ < Δσ_D     (m=5)
    Δσ_L = Δσ_D·(5·10⁶/10⁸)^(1/5) ≈ 0.549·Δσ_D  → cut-off a N = 10⁸
    Δσ < Δσ_L  →  N = ∞ (no produce daño)
  Tabla Δσ* (codo) de W01419 (col. correcta): 160→117.9, 112→82.5, 71→52.3,
  50→36.8, 36→26.5 MPa.

- **W01510** (Exercise 9 Fatigue Resolution): ejemplo Palmgren-Miner resuelto,
  viga IPE 240, detalle 80, γ_Mf=1.15:
    P1: Δσ=75.16 MPa, n1=10⁶ → N1=1,585,791 ciclos.
    P2: Δσ=8.67 MPa < Δσ_L → no daño (N=∞).
    D = 10⁶/1,585,791 + 0 = 0.63 < 1.0  →  OK.

NOTA sobre Δσ_L (no tautológico): W01419 §7 tabula/escribe Δσ_L = 0.549·Δσ_C,
pero ESO es un error de la ficha; el cut-off correcto EN 1993-1-9 yace sobre la
recta m=5: Δσ_L = 0.549·Δσ_D = 0.405·Δσ_C. El ejemplo resuelto W01510
(Δσ_L = 0.549·Δσ_D) confirma la forma correcta. Los goldens usan la derivación
correcta; la col. Δσ_L de W01419 NO se ancla (se ancla la col. Δσ*, sí correcta).

Los goldens NO son tautológicos: los valores objetivo provienen de las fichas /
del cálculo a mano EN 1993-1-9, no de re-ejecutar la función bajo prueba. El
punto intermedio del tramo m=5 (cat 160, Δσ=80) discrimina explícitamente la
curva trilineal frente a una recta única m=3 (que daría ~1.6·10⁷ en vez de
~3.48·10⁷) y frente al simple recorte (clamp) de N a 10⁸.
"""
import math

import pytest

from fatiguejm.ec3_sn import (
    EC3_NC,
    EC3_N_CUTOFF,
    EC3_N_KNEE,
    constant_amplitude_limit,
    cutoff_limit,
    ec3_cycles_to_failure,
    palmgren_miner_ec3,
)


# --------------------------------------------------------------------------
# Constantes de la curva (EN 1993-1-9 §7.1)
# --------------------------------------------------------------------------
def test_constantes_curva_ec3():
    assert EC3_NC == 2.0e6        # categoría de detalle definida a 2·10⁶
    assert EC3_N_KNEE == 5.0e6    # codo m=3→m=5
    assert EC3_N_CUTOFF == 1.0e8  # cut-off (límite de truncamiento)


# --------------------------------------------------------------------------
# Límites Δσ_D (codo) y Δσ_L (cut-off) — anclados a W01419 (col. Δσ*) y
# a la derivación correcta EN 1993-1-9 §7 confirmada por W01510.
# --------------------------------------------------------------------------
@pytest.mark.parametrize(
    "delta_sigma_c, delta_sigma_D_ref",   # W01419 tabla col. Δσ* (codo)
    [(160, 117.9), (112, 82.5), (71, 52.3), (50, 36.8), (36, 26.5)],
)
def test_constant_amplitude_limit_golden_W01419(delta_sigma_c, delta_sigma_D_ref):
    # Δσ_D = Δσ_C·(2/5)^(1/3) — codo de la curva a N = 5·10⁶.
    assert constant_amplitude_limit(delta_sigma_c) == pytest.approx(
        delta_sigma_D_ref, abs=0.1
    )


@pytest.mark.parametrize(
    "delta_sigma_c, delta_sigma_L_ref",   # Δσ_L = 0.549·Δσ_D = 0.405·Δσ_C
    [(160, 64.8), (112, 45.3), (71, 28.7), (50, 20.2), (36, 14.6)],
)
def test_cutoff_limit_golden_EC3(delta_sigma_c, delta_sigma_L_ref):
    # Cut-off correcto EN 1993-1-9 sobre la recta m=5 (NO el 0.549·Δσ_C de la ficha).
    assert cutoff_limit(delta_sigma_c) == pytest.approx(delta_sigma_L_ref, abs=0.1)
    # Coherencia interna: Δσ_L cae exactamente sobre la curva a N = 10⁸.
    assert ec3_cycles_to_failure(cutoff_limit(delta_sigma_c), delta_sigma_c) == pytest.approx(
        EC3_N_CUTOFF, rel=1e-9
    )


# --------------------------------------------------------------------------
# Puntos de definición de la curva (EN 1993-1-9 §7.1, ec. 7.1)
# --------------------------------------------------------------------------
def test_punto_definicion_2e6_en_delta_sigma_c():
    # Por definición: N = 2·10⁶ cuando Δσ = Δσ_C.
    assert ec3_cycles_to_failure(71.0, 71.0) == pytest.approx(2.0e6, rel=1e-9)


def test_punto_codo_5e6_en_delta_sigma_D():
    # En Δσ = Δσ_D las rectas m=3 y m=5 coinciden en N = 5·10⁶.
    dD = constant_amplitude_limit(71.0)
    assert ec3_cycles_to_failure(dD, 71.0) == pytest.approx(5.0e6, rel=1e-6)


def test_tramo_m3_golden_W01419_ejemplo2():
    # W01419 Ej.2: cat 71, Δσ1=80 → N1 = 2·10⁶·(71/80)³ = 1.40·10⁶.
    N = ec3_cycles_to_failure(80.0, 71.0)
    assert N == pytest.approx(2.0e6 * (71.0 / 80.0) ** 3, rel=1e-9)
    assert N == pytest.approx(1.398e6, rel=1e-3)


def test_tramo_m5_intermedio_discrimina_trilineal():
    # Punto ESTRICTAMENTE entre Δσ_D y Δσ_L (cat 160): discrimina m=5 vs recta m=3.
    dc = 160.0
    ds = 80.0
    dD = constant_amplitude_limit(dc)   # ≈117.9
    dL = cutoff_limit(dc)               # ≈64.8
    assert dL < ds < dD                 # cae en el tramo m=5
    N = ec3_cycles_to_failure(ds, dc)
    # Valor trilineal correcto (m=5): N = 5·10⁶·(Δσ_D/80)⁵.
    N_m5 = 5.0e6 * (dD / ds) ** 5
    assert N == pytest.approx(N_m5, rel=1e-9)
    assert N == pytest.approx(3.48e7, rel=1e-2)
    # Discriminación: una recta única m=3 daría ~1.6·10⁷ (≈mitad) — distinto.
    N_single_m3 = 2.0e6 * (dc / ds) ** 3
    assert N > 1.9 * N_single_m3


def test_cut_off_devuelve_infinito_por_debajo_de_delta_sigma_L():
    # Δσ < Δσ_L → vida infinita (no daño). Discrimina vs un clamp de N a 10⁸.
    dc = 71.0
    dL = cutoff_limit(dc)
    assert ec3_cycles_to_failure(dL * 0.99, dc) == math.inf
    # Justo por encima del cut-off la vida es finita (≈10⁸), no infinita.
    N_above = ec3_cycles_to_failure(dL * 1.001, dc)
    assert math.isfinite(N_above) and N_above < EC3_N_CUTOFF


def test_curva_monotona_decreciente():
    dc = 90.0
    Ns = [ec3_cycles_to_failure(ds, dc) for ds in (40, 60, 80, 100, 140)]
    finite = [n for n in Ns if math.isfinite(n)]
    assert finite == sorted(finite, reverse=True)


def test_delta_sigma_no_positivo_es_infinito():
    assert ec3_cycles_to_failure(0.0, 71.0) == math.inf
    assert ec3_cycles_to_failure(-5.0, 71.0) == math.inf


# --------------------------------------------------------------------------
# Palmgren-Miner end-to-end — golden W01510 (Exercise 9), γ_Mf = 1.15
# --------------------------------------------------------------------------
def test_palgrem_miner_golden_W01510():
    # IPE 240, detalle 80, γ_Mf=1.15.
    #   P1: Δσ=75.16, n=1e6 → N1=1,585,791 ; D1=0.63
    #   P2: Δσ=8.67 < Δσ_L → N=∞ → D2=0
    spectrum = [
        {"stress_range_MPa": 75.16, "cycles": 1.0e6},
        {"stress_range_MPa": 8.67, "cycles": 5.0e5},
    ]
    res = palmgren_miner_ec3(spectrum, delta_sigma_c=80.0, gamma_Mf=1.15)
    # N1 anclado al valor de la ficha W01510 (con resistencia de diseño 80/1.15).
    assert res["blocks"][0]["N_i"] == pytest.approx(1_585_791, rel=2e-3)
    # P2 cae bajo el cut-off → descartado (N=∞, daño 0).
    assert math.isinf(res["blocks"][1]["N_i"])
    assert res["blocks"][1]["damage"] == 0.0
    # Daño total y veredicto anclados a la ficha: D = 0.63 ≤ 1 → OK.
    assert res["total_damage"] == pytest.approx(0.63, abs=0.01)
    assert res["ok"] is True


def test_palgrem_miner_acumulacion_lineal():
    base = palmgren_miner_ec3(
        [{"stress_range_MPa": 90.0, "cycles": 1.0e5}], delta_sigma_c=80.0
    )["total_damage"]
    diez = palmgren_miner_ec3(
        [{"stress_range_MPa": 90.0, "cycles": 1.0e6}], delta_sigma_c=80.0
    )["total_damage"]
    assert diez == pytest.approx(10.0 * base, rel=1e-9)


def test_palgrem_miner_falla_si_D_mayor_1():
    res = palmgren_miner_ec3(
        [{"stress_range_MPa": 200.0, "cycles": 3.0e6}], delta_sigma_c=71.0
    )
    assert res["total_damage"] > 1.0 and res["ok"] is False
