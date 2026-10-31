"""Viga IPE 500 con voladizo bajo dos cargas repetidas: fatiga en dos secciones (EN 1993-1-9).

Problema del examen UPC «Análisis y Proyecto de Estructuras de Acero» (2020-03-30),
fichas W01468 y W01469 de la extracción del máster (dos transcripciones independientes
con el mismo resultado). Viga biapoyada A–C de 8 m con voladizo C–D de 2 m; P1 actúa
en el centro del vano (sección B) y P2 en el extremo D. IPE 500: W_el,y = 1 928,1 cm³.
Detalle de categoría 80 en B y en C, γ_Mf = 1,35 (vida segura, consecuencias altas).

Tres cuestiones del examen:
  1. P1 = P2 = 200 kN alternadas, 10 000 ciclos: el rango en B es σ1,B + σ2,B.
  2. P1 = 100 kN × 100 000 ciclos y P2 = 200 kN × 50 000 ciclos, sección B.
  3. Solo P2 = 200 kN × 50 000 ciclos, sección C (empotramiento del voladizo).
Resultado manuscrito de la ficha: N_B = 13 811 (verifica), D_B = 0,40 (verifica),
D_C = 1,07 (no verifica).

Ejecutar:  python examples/ipe500_cantilever_beam_two_sections_exam_w01468.py
"""
from steelfatigue.ec3_sn import palmgren_miner_ec3

W_EL_MM3 = 1_928.1e3   # IPE 500, módulo resistente elástico [mm³]
L_SPAN_M = 8.0         # vano A–C [m]
L_CANT_M = 2.0         # voladizo C–D [m]
DETAIL = 80            # Δσ_C [MPa], categoría de detalle en B y C
GAMMA_MF = 1.35        # EN 1993-1-9 Tabla 3.1


def sigma_B_from_P1(P1_kN: float) -> float:
    """Carga en el centro del vano: M_B = P·L/4."""
    return P1_kN * 1e3 * L_SPAN_M * 1e3 / 4.0 / W_EL_MM3


def sigma_B_from_P2(P2_kN: float) -> float:
    """Carga en D: M_C = P·l_v en el apoyo C, lineal hasta A, luego M_B = M_C/2."""
    return P2_kN * 1e3 * L_CANT_M * 1e3 / 2.0 / W_EL_MM3


def sigma_C_from_P2(P2_kN: float) -> float:
    return P2_kN * 1e3 * L_CANT_M * 1e3 / W_EL_MM3


def report(title: str, res: dict) -> None:
    print(f"\n{title}")
    for b in res["blocks"]:
        print(f"  Δσ = {b['stress_range_MPa']:7.2f} MPa   n = {b['cycles']:9.0f}   "
              f"N = {b['N_i']:11.0f}   n/N = {b['damage']:.4f}")
    print(f"  D = {res['total_damage']:.3f}  →  {'VERIFICA' if res['ok'] else 'NO VERIFICA'}")


def main() -> None:
    print(f"IPE 500, W_el,y = {W_EL_MM3/1e3:.1f} cm³; categoría {DETAIL}, γ_Mf = {GAMMA_MF}")
    print(f"Δσ_C,d = {DETAIL/GAMMA_MF:.2f} MPa")

    # 1. Cargas alternadas de 200 kN: el rango en B suma las dos tensiones máximas.
    s1 = sigma_B_from_P1(200.0)
    s2 = sigma_B_from_P2(200.0)
    print(f"\nσ1,B = {s1:.2f} MPa (P1 en vano), σ2,B = {s2:.2f} MPa (P2 en voladizo)")
    res1 = palmgren_miner_ec3([{"stress_range_MPa": s1 + s2, "cycles": 10_000}],
                              detail=DETAIL, gamma_Mf=GAMMA_MF)
    report("1) P1 = P2 = 200 kN alternadas, sección B, 10 000 ciclos", res1)

    # 2. Cargas independientes: cada una produce 103,73 MPa en B.
    res2 = palmgren_miner_ec3(
        [{"stress_range_MPa": sigma_B_from_P1(100.0), "cycles": 100_000},
         {"stress_range_MPa": sigma_B_from_P2(200.0), "cycles": 50_000}],
        detail=DETAIL, gamma_Mf=GAMMA_MF)
    report("2) P1 = 100 kN × 1e5 y P2 = 200 kN × 5e4, sección B", res2)

    # 3. Sección C: solo P2 genera momento (P1 en el vano no carga el voladizo).
    res3 = palmgren_miner_ec3([{"stress_range_MPa": sigma_C_from_P2(200.0), "cycles": 50_000}],
                              detail=DETAIL, gamma_Mf=GAMMA_MF)
    report("3) P2 = 200 kN × 5e4, sección C", res3)
    print("\nLa misma categoría de detalle verifica en B y falla en C: la sección crítica "
          "a fatiga no es la de mayor momento estático sino la de mayor rango y ciclos.")


if __name__ == "__main__":
    main()
