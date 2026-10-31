"""Elegir el espesor de ala de una viga armada S355JR para servicio a −35 °C (EN 1993-1-10).

Viga armada con alas de 400 mm y alma de 1 200 mm, M_Ed = 1 800 kN·m en la combinación
de comprobación a rotura frágil. Para cada espesor candidato se estima la tensión en el
ala con el par de alas (σ ≈ M / [b·t·(h_w + t)]), se reduce f_y por espesor y se busca
el espesor máximo admisible en los puntos de la Tabla 2.1 disponibles para S355JR a
T_Ed = −40 °C (los dos puntos transcritos en las fichas W01468/W01469).

El paquete no extrapola fuera de los puntos de tabla: cuando la relación σ_Ed/f_y(t)
cae fuera de [0,50; 0,75] lanza ValueError y aquí se informa en vez de inventar un
valor. Para cubrir otros ratios hay que pasar más puntos de la Tabla 2.1.

Ejecutar:  python examples/brittle_fracture_plate_girder_flange_thickness_choice.py
"""
from steelfatigue.ec3_brittle_fracture import brittle_fracture_check

B_FLANGE_MM = 400.0
H_WEB_MM = 1200.0
M_ED_KNM = 1800.0
FY_MPA = 355.0
T0_C = -35.0
TABLE_S355JR_TED_MINUS40 = [(0.50, 25.0), (0.75, 15.0)]
CANDIDATES_MM = [12.0, 15.0, 18.0, 20.0, 25.0]


def flange_stress(t_mm: float) -> float:
    return M_ED_KNM * 1e6 / (B_FLANGE_MM * t_mm * (H_WEB_MM + t_mm))


def main() -> None:
    print(f"M_Ed = {M_ED_KNM:.0f} kN·m, ala {B_FLANGE_MM:.0f} mm, alma {H_WEB_MM:.0f} mm, "
          f"S355JR, T₀ = {T0_C:.0f} °C\n")
    print(f"{'t [mm]':>7} {'σ_Ed':>8} {'f_y(t)':>8} {'ratio':>6} {'t_max':>7}  veredicto")
    for t in CANDIDATES_MM:
        sigma = flange_stress(t)
        try:
            r = brittle_fracture_check(sigma, FY_MPA, t, TABLE_S355JR_TED_MINUS40, T0_C=T0_C)
        except ValueError as exc:
            ratio = sigma / (FY_MPA - 0.25 * t)
            side = "por encima" if ratio > 0.75 else "por debajo"
            print(f"{t:7.1f} {sigma:8.1f} {FY_MPA - 0.25*t:8.1f} {ratio:6.3f} {'—':>7}  "
                  f"ratio {side} de los puntos de tabla: {exc}")
            continue
        print(f"{t:7.1f} {sigma:8.1f} {r.fy_t_MPa:8.1f} {r.sigma_over_fy:6.3f} "
              f"{r.t_max_admissible_mm:7.1f}  {'OK' if r.ok else 'NO'}")


if __name__ == "__main__":
    main()
