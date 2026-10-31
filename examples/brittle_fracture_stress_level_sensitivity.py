"""Sensibilidad del espesor admisible a rotura frágil frente al nivel de tensión (EN 1993-1-10).

Ala de 20 mm en S355JR con T_Ed = −40 °C. Se barre σ_Ed entre 170 y 265 N/mm² y se
obtiene el espesor máximo admisible interpolado en los puntos de la Tabla 2.1
transcritos en las fichas W01468/W01469 (0,50 → 25 mm; 0,75 → 15 mm). Sirve para
leer de un vistazo a partir de qué utilización un ala de 20 mm deja de verificar.

Ejecutar:  python examples/brittle_fracture_stress_level_sensitivity.py
"""
from steelfatigue.ec3_brittle_fracture import brittle_fracture_check, interpolate_max_thickness

T_MM = 20.0
FY_MPA = 355.0
TABLE_S355JR_TED_MINUS40 = [(0.50, 25.0), (0.75, 15.0)]


def main() -> None:
    fy_t = FY_MPA - 0.25 * T_MM
    print(f"S355JR, t = {T_MM:.0f} mm, f_y(t) = {fy_t:.1f} N/mm², T_Ed = −40 °C\n")
    print(f"{'σ_Ed [MPa]':>10} {'ratio':>6} {'t_max [mm]':>10}  t = 20 mm")
    for sigma in range(175, 266, 10):
        try:
            r = brittle_fracture_check(float(sigma), FY_MPA, T_MM, TABLE_S355JR_TED_MINUS40)
        except ValueError:
            print(f"{sigma:10d} {sigma/fy_t:6.3f} {'—':>10}  ratio > 0,75: fuera de los puntos de tabla, "
                  "no se extrapola")
            continue
        print(f"{sigma:10d} {r.sigma_over_fy:6.3f} {r.t_max_admissible_mm:10.1f}  "
              f"{'OK' if r.ok else 'NO'}")

    # Ratio límite para t = 20 mm: resolver t_max(ratio) = 20 en la recta entre los dos puntos.
    (r0, t0), (r1, t1) = TABLE_S355JR_TED_MINUS40
    ratio_lim = r0 + (T_MM - t0) * (r1 - r0) / (t1 - t0)
    print(f"\nRatio límite para t = {T_MM:.0f} mm: {ratio_lim:.3f} → σ_Ed,lim = {ratio_lim*fy_t:.1f} N/mm²")
    print(f"Comprobación: t_max({ratio_lim:.3f}) = "
          f"{interpolate_max_thickness(ratio_lim, TABLE_S355JR_TED_MINUS40):.2f} mm")


if __name__ == "__main__":
    main()
