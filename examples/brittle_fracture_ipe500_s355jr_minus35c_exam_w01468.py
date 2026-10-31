"""Rotura frágil EN 1993-1-10: espesor máximo admisible de un ala IPE 500 S355JR a −35 °C.

Mismo examen UPC 2020-03-30 que las fichas W01468/W01469 (parte de rotura frágil).
Carga P2 = 200 kN en el extremo del voladizo de 2 m produce M = 400 kN·m en el
empotramiento: σ_Ed = 400·10⁶ / 1 928 100 = 207,46 N/mm². Temperatura mínima de
servicio T₀ = −35 °C, ΔT_r = 5 °C → T_Ed = −40 °C.
Para S355JR y T_Ed = −40 °C, las fichas transcriben dos puntos calibrados de la
Tabla 2.1: (σ_Ed/f_y(t) = 0,50 → t_max = 25 mm) y (0,75 → 15 mm). Se interpola
linealmente; la tabla completa no forma parte del paquete y se pasa como parámetro.
Resultado de la ficha: f_y(t) = 351 N/mm², ratio = 0,591, t_max ≈ 21,4 mm > t_f = 16 mm.

Ejecutar:  python examples/brittle_fracture_ipe500_s355jr_minus35c_exam_w01468.py
"""
from steelfatigue.ec3_brittle_fracture import (
    brittle_fracture_check,
    reduced_yield_strength,
    reference_temperature,
)

W_EL_MM3 = 1_928.1e3
T_FLANGE_MM = 16.0
FY_MPA = 355.0
T0_C = -35.0
TABLE_S355JR_TED_MINUS40 = [(0.50, 25.0), (0.75, 15.0)]   # (σ_Ed/f_y(t), t_max mm)


def main() -> None:
    M_Ed_Nmm = 200e3 * 2000.0
    sigma = M_Ed_Nmm / W_EL_MM3
    print(f"σ_Ed = {sigma:.2f} N/mm² (M = {M_Ed_Nmm/1e6:.0f} kN·m, W_el,y = {W_EL_MM3/1e3:.1f} cm³)")
    print(f"T_Ed = {reference_temperature(T0_C):.0f} °C (T₀ = {T0_C:.0f} °C, ΔT_r = 5 °C)")
    print(f"f_y(t) = {reduced_yield_strength(FY_MPA, T_FLANGE_MM):.1f} N/mm² "
          f"(f_y − 0,25·t, Anexo B)")

    res = brittle_fracture_check(sigma, FY_MPA, T_FLANGE_MM, TABLE_S355JR_TED_MINUS40, T0_C=T0_C)
    print(f"\nσ_Ed / f_y(t) = {res.sigma_over_fy:.3f}")
    print(f"t_max admisible (interpolado en la tabla S355JR, T_Ed = {res.T_ref_C:.0f} °C) = "
          f"{res.t_max_admissible_mm:.1f} mm")
    print(f"t_f = {res.t_mm:.1f} mm  →  {'VERIFICA' if res.ok else 'NO VERIFICA'}")


if __name__ == "__main__":
    main()
