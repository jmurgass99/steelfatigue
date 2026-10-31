"""Golden tests — curva S-N trilineal EN 1993-1-9 §7 (`steelfatigue.ec3_sn`).

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

from steelfatigue.ec3_sn import (
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


def test_palgrem_miner_bloque_sin_cycles_rechazado():
    """Las dos claves del bloque deben exigirse con el MISMO rigor.

    `stress_range_MPa` se leia con indexacion directa (KeyError si falta) pero
    `cycles` con .get(..., 0.0): un bloque sin ciclos desaparecia del sumatorio
    de Miner con dano 0.0 y ademas se reportaba con `cycles: 0.0`, un numero
    que el usuario nunca dio.
    """
    with pytest.raises(KeyError):
        palmgren_miner_ec3([{"stress_range_MPa": 200.0}], delta_sigma_c=80.0)


def test_palgrem_miner_cycles_cero_explicito_sigue_valiendo():
    """Un 0.0 declarado SI es un dato: cero ciclos, cero dano, sin excepcion."""
    res = palmgren_miner_ec3(
        [{"stress_range_MPa": 200.0, "cycles": 0.0}], delta_sigma_c=80.0
    )
    assert res["total_damage"] == 0.0


# --------------------------------------------------------------------------
# Golden W01468 / W01469 — IPE 500 S355JR, examen UPC 2020-03-30 resuelto.
# Dos fichas independientes (transcripciones distintas del mismo examen
# manuscrito) dan resultados idénticos → cross-validación fuerte. Recalculado
# a mano (mecánica de vigas M=P·a·b/L, σ=M/W) ANTES de anclar, no se detectó
# errata: valores propios reproducen los de ambas fichas al decimal
# (N_B≈13,811; N1,B=N2,B≈372,904; N2,C≈46,613; D_B≈0.40; D_C≈1.07).
#
# Viga biapoyada con voladizo, IPE 500 (W_el,y=1928.1 cm³), vano 4+4 m,
# voladizo 2 m. Detalle crítico: rigidizador transversal, cat. Δσ_C=80 MPa,
# γ_Mf=1.35 (integridad asegurada, consecuencias graves).
# --------------------------------------------------------------------------
_W_IPE500_mm3 = 1928.1e3
_L_VANO_mm = 8000.0
_L_VOLADIZO_mm = 2000.0


def _momento_flector_vano(P_N: float) -> float:
    # M = P·L/4 (carga central en vano biapoyado L=8m). P en N → M en N·mm.
    return P_N * _L_VANO_mm / 4.0


def _momento_flector_voladizo_en_B(P_N: float) -> float:
    # M en apoyo B por carga P en el extremo del voladizo (brazo L_v/2 hasta B).
    return P_N * _L_VOLADIZO_mm / 2.0


def _momento_flector_voladizo_en_C(P_N: float) -> float:
    # M en el empotramiento C (extremo voladizo) por carga P en D.
    return P_N * _L_VOLADIZO_mm


def test_ec3_1_9_seccion_B_cargas_alternadas_golden_W01468_W01469():
    # P1=P2=200 kN alternadas: Δσ_R,B = σ_max,1,B + σ_max,2,B (rango completo).
    P = 200_000.0  # N
    sigma1_B = _momento_flector_vano(P) / _W_IPE500_mm3
    sigma2_B = _momento_flector_voladizo_en_B(P) / _W_IPE500_mm3
    assert sigma1_B == pytest.approx(207.46, abs=0.05)
    assert sigma2_B == pytest.approx(103.73, abs=0.05)
    delta_sigma_R_B = sigma1_B + sigma2_B
    assert delta_sigma_R_B == pytest.approx(311.19, abs=0.05)

    res = palmgren_miner_ec3(
        [{"stress_range_MPa": delta_sigma_R_B, "cycles": 10_000.0}],
        delta_sigma_c=80.0,
        gamma_Mf=1.35,
    )
    N_B = res["blocks"][0]["N_i"]
    # N ≈ 13,811 ciclos > 10,000 aplicados → VERIFICA (ficha: método integridad
    # asegurada, mismo resultado que Palmgren-Miner con un único bloque D=n/N).
    assert N_B == pytest.approx(13_811, rel=2e-3)
    assert res["ok"] is True


def test_ec3_1_9_palmgren_miner_seccion_B_verifica_golden_W01468_W01469():
    # Cargas independientes: P1=100kN×100,000 ciclos + P2=200kN×50,000 ciclos.
    # Ambas producen el mismo Δσ=103.73 MPa en B (P1 vía vano, P2 vía voladizo).
    P1, P2 = 100_000.0, 200_000.0
    sigma1_B = _momento_flector_vano(P1) / _W_IPE500_mm3
    sigma2_B = _momento_flector_voladizo_en_B(P2) / _W_IPE500_mm3
    assert sigma1_B == pytest.approx(103.73, abs=0.05)
    assert sigma2_B == pytest.approx(103.73, abs=0.05)

    res = palmgren_miner_ec3(
        [
            {"stress_range_MPa": sigma1_B, "cycles": 100_000.0},
            {"stress_range_MPa": sigma2_B, "cycles": 50_000.0},
        ],
        delta_sigma_c=80.0,
        gamma_Mf=1.35,
    )
    # Ficha: N1,B=N2,B≈372,894 → D_B=0.2682+0.1341=0.40 < 1.0 → VERIFICA.
    assert res["blocks"][0]["N_i"] == pytest.approx(372_894, rel=2e-3)
    assert res["blocks"][1]["N_i"] == pytest.approx(372_894, rel=2e-3)
    assert res["total_damage"] == pytest.approx(0.40, abs=0.01)
    assert res["ok"] is True


def test_ec3_1_9_palmgren_miner_seccion_C_no_verifica_golden_W01468_W01469():
    # Solo P2 actúa en C (P1 en el vano no genera momento en C por simetría).
    # Caso NEGATIVO real (no arbitrario): la propia ficha muestra que la
    # sección C SÍ falla mientras que B (misma categoría) no — discrimina
    # falsos positivos de un check que ignore la sección crítica correcta.
    P2 = 200_000.0
    sigma2_C = _momento_flector_voladizo_en_C(P2) / _W_IPE500_mm3
    assert sigma2_C == pytest.approx(207.46, abs=0.05)

    res = palmgren_miner_ec3(
        [{"stress_range_MPa": sigma2_C, "cycles": 50_000.0}],
        delta_sigma_c=80.0,
        gamma_Mf=1.35,
    )
    # Ficha: N2,C≈46,611 → D_C=1.07 > 1.0 → NO VERIFICA.
    assert res["blocks"][0]["N_i"] == pytest.approx(46_611, rel=2e-3)
    assert res["total_damage"] == pytest.approx(1.07, abs=0.01)
    assert res["ok"] is False


# --------------------------------------------------------------------------
# Golden W01508 — Exercise 7b Fatigue and brittle fracture resolution.
# Curva S-N invertida: despejar la carga P admisible para N=500,000 ciclos
# dados (en vez de despejar N dado Δσ, como en los tests anteriores).
# Recalculado a mano con la fórmula EC3-1-9 antes de anclar: ambos resultados
# (P=376.3 kN, P=102.4 kN) se reproducen sin errata.
# --------------------------------------------------------------------------
def test_ec3_1_9_carga_admisible_cat80_golden_W01508():
    # Soporte interno, cat. 80, γ_Mf=1.35, N=500,000, Δσ=2.50e-4·P (P en N).
    P_kN = 376.3
    delta_sigma = 2.50e-4 * (P_kN * 1000.0)
    N = ec3_cycles_to_failure(delta_sigma, 80.0 / 1.35)
    assert N == pytest.approx(500_000, rel=2e-3)


def test_ec3_1_9_carga_admisible_cat36_domina_golden_W01508():
    # Conexión a un lado, cat. 36 (domina el diseño frente a cat.80), mismo
    # N=500,000, Δσ=4.133e-4·P.
    P_kN = 102.4
    delta_sigma = 4.133e-4 * (P_kN * 1000.0)
    N = ec3_cycles_to_failure(delta_sigma, 36.0 / 1.35)
    assert N == pytest.approx(500_000, rel=2e-3)
    # La categoría 36 permite una carga muy inferior a la 80: confirma que
    # domina el diseño (tal como concluye la ficha).
    assert P_kN < 376.3


# --------------------------------------------------------------------------
# Golden W01407 — Problema fatiga 1. Discrimina un error de razonamiento
# real documentado en la ficha (que selecciona el tramo m=3/m=5 según el
# número de ciclos APLICADOS N₁, en vez de según la magnitud de Δσ frente a
# Δσ_D — la ficha llega a sugerir "N₁=2.2e8 → pendiente m=5 aplica" aunque
# Δσ₁ esté muy por encima del codo Δσ_D). Recalculado a mano: Δσ₁=67.61 MPa >
# Δσ_D≈58.94 MPa (cat. 80) → el tramo correcto es m=3, SIEMPRE, sin importar
# cuántos ciclos se apliquen. NO se ancla el resultado erróneo de la ficha
# (m=5); se ancla el comportamiento correcto de `ec3_cycles_to_failure`
# (selección por Δσ vs Δσ_D) frente a los datos de geometría/carga reales.
# --------------------------------------------------------------------------
def test_ec3_1_9_seleccion_tramo_por_tension_no_por_N_aplicado_golden_W01407():
    W_mm3 = 3550e3
    L_m, a_m = 6.0, 2.0
    F1_kN = 180.0
    M1_kNm = F1_kN * a_m * (L_m - a_m) / L_m  # = 240 kN·m (viga biapoyada, carga excéntrica)
    delta_sigma1 = M1_kNm * 1e6 / W_mm3  # MPa
    assert delta_sigma1 == pytest.approx(67.61, abs=0.05)

    dc = 80.0
    dD = constant_amplitude_limit(dc)
    assert delta_sigma1 > dD  # por encima del codo → tramo m=3 obligatorio

    N1 = ec3_cycles_to_failure(delta_sigma1, dc)
    N1_m3_esperado = 2.0e6 * (dc / delta_sigma1) ** 3
    assert N1 == pytest.approx(N1_m3_esperado, rel=1e-9)
    assert N1 == pytest.approx(3.314e6, rel=1e-3)

    # n1=2.2e8 ciclos aplicados (dato de la ficha) sobre N1≈3.31e6 → D≈66.4,
    # falla ampliamente. El daño NO se reduce por usar m=5 solo porque
    # n1 > 5e6: eso sería el razonamiento erróneo de la ficha.
    res = palmgren_miner_ec3(
        [{"stress_range_MPa": delta_sigma1, "cycles": 2.2e8}], delta_sigma_c=dc
    )
    assert res["total_damage"] == pytest.approx(66.4, rel=1e-2)
    assert res["ok"] is False


# --------------------------------------------------------------------------
# Golden W01445 — Examen enero 2019, Pregunta 7 (V/F): "Daño acumulado
# fatiga tiene en cuenta la secuencia de ciclos" → Falso. Palmgren-Miner es
# independiente de la secuencia/orden de aplicación de los bloques.
# --------------------------------------------------------------------------
def test_ec3_1_9_miner_independiente_de_la_secuencia_golden_W01445():
    bloque_a = {"stress_range_MPa": 90.0, "cycles": 2.0e5}
    bloque_b = {"stress_range_MPa": 60.0, "cycles": 1.5e6}
    bloque_c = {"stress_range_MPa": 120.0, "cycles": 3.0e4}

    d_orden_1 = palmgren_miner_ec3(
        [bloque_a, bloque_b, bloque_c], delta_sigma_c=90.0
    )["total_damage"]
    d_orden_2 = palmgren_miner_ec3(
        [bloque_c, bloque_a, bloque_b], delta_sigma_c=90.0
    )["total_damage"]
    d_orden_3 = palmgren_miner_ec3(
        [bloque_b, bloque_c, bloque_a], delta_sigma_c=90.0
    )["total_damage"]

    assert d_orden_1 == pytest.approx(d_orden_2, rel=1e-12)
    assert d_orden_1 == pytest.approx(d_orden_3, rel=1e-12)


# --------------------------------------------------------------------------
# Golden EN 1993-1-9 §7 — categoría de detalle Δσ_C = 90 MPa, curva completa.
#
# Oráculo: el TEXTO DE LA NORMA (EN 1993-1-9:2005 §7.1, Ec. 7.1 y Fig. 7.1), NO
# la ejecución de `steelfatigue`. La categoría Δσ_C = 90 MPa figura en el catálogo
# del propio paquete como 'FAT 90' (steelfatigue.wohler_db, atiesador transversal)
# y NO estaba cubierta por los goldens anteriores de este fichero (que anclan
# 160/112/80/71/50/36). Aquí se cierra la curva completa para Δσ_C = 90: codo,
# cut-off y un punto en CADA tramo.
#
# DERIVACIÓN A MANO (EN 1993-1-9 §7.1, Fig. 7.1):
#
#   Δσ_C = 90 MPa a N_C = 2·10⁶ ciclos                          (definición)
#
#   1) Codo (límite de fatiga a amplitud constante), N_D = 5·10⁶:
#        Δσ_D = Δσ_C·(N_C/N_D)^(1/3) = 90·(2/5)^(1/3)
#             = 90·0.40^(0.333333) = 90·0.7368063 = 66.3126 MPa
#
#   2) Cut-off (límite de truncamiento) sobre la recta m=5, N_L = 10⁸:
#        Δσ_L = Δσ_D·(N_D/N_L)^(1/5) = 66.3126·(5·10⁶/10⁸)^(1/5)
#             = 66.3126·0.05^0.2 = 66.3126·0.5492803 = 36.4242 MPa
#        (equivale a 0.40525·Δσ_C; NO a 0.549·Δσ_C)
#
#   3) Tramo m = 3 (Δσ ≥ Δσ_D). Nivel Δσ = 120 MPa > 66.3126 → aplica m=3:
#        N = 2·10⁶·(90/120)³ = 2·10⁶·(0.75)³ = 2·10⁶·0.421875 = 843 750 ciclos
#        (valor CERRADO y exacto: 0.75³ es racional, sin redondeo)
#
#   4) Tramo m = 5 (Δσ_L ≤ Δσ < Δσ_D). Nivel Δσ = 50 MPa, y en efecto
#      36.4242 < 50 < 66.3126 → aplica m=5:
#        N = 5·10⁶·(Δσ_D/50)⁵ = 5·10⁶·(66.3126/50)⁵ = 5·10⁶·(1.3262523)⁵
#          = 5·10⁶·4.1032613 = 2.0516·10⁷ ciclos
#        Forma cerrada equivalente: N = 5·10⁶·(90/50)⁵·0.4^(5/3).
#        DISCRIMINACIÓN: una recta única m=3 daría 2·10⁶·(90/50)³ = 1.166·10⁷
#        (≈ 43 % del valor trilineal) y un clamp a 10⁸ daría 10⁸ — ambos
#        distintos del valor correcto.
#
# Estas cifras se derivaron a mano ANTES de ejecutar el código y coincidieron
# con él hasta la precisión anclada: NO es un test de caracterización.
# --------------------------------------------------------------------------
def test_ec3_1_9_curva_completa_cat90_golden_norma():
    # Se entra por el código FAT del catálogo del paquete (no por el literal),
    # de modo que el golden ata también la entrada 'FAT 90' de wohler_db.
    dc = "FAT 90"

    # (1) Codo Δσ_D a N = 5·10⁶ — EN 1993-1-9 §7.1.
    dD = constant_amplitude_limit(dc)
    assert dD == pytest.approx(66.3126, abs=5e-5)

    # (2) Cut-off Δσ_L a N = 10⁸ — EN 1993-1-9 §7.1.
    dL = cutoff_limit(dc)
    assert dL == pytest.approx(36.4242, abs=5e-5)

    # (3) Tramo m=3: Δσ = 120 MPa → N = 843 750 ciclos (exacto).
    assert 120.0 > dD
    assert ec3_cycles_to_failure(120.0, dc) == pytest.approx(843_750.0, abs=0.5)

    # (4) Tramo m=5: Δσ = 50 MPa (estrictamente entre Δσ_L y Δσ_D).
    assert dL < 50.0 < dD
    N50 = ec3_cycles_to_failure(50.0, dc)
    assert N50 == pytest.approx(2.0516e7, rel=5e-5)
    # Discrimina frente a recta única m=3 (1.166·10⁷) y frente a clamp a 10⁸.
    assert N50 > 1.7 * 1.166e7
    assert N50 < EC3_N_CUTOFF


def test_ec3_1_9_cat90_puntos_de_definicion_de_la_curva():
    """Los dos vértices caen exactamente sobre 5·10⁶ y 10⁸ (Fig. 7.1)."""
    dc = 90.0
    assert ec3_cycles_to_failure(dc, dc) == pytest.approx(2.0e6, rel=1e-9)
    assert ec3_cycles_to_failure(66.3126, dc) == pytest.approx(5.0e6, rel=1e-4)
    assert ec3_cycles_to_failure(36.4242, dc) == pytest.approx(1.0e8, rel=1e-4)
    # Justo por debajo del cut-off derivado a mano: vida infinita (sin daño).
    assert ec3_cycles_to_failure(36.4, dc) == math.inf
