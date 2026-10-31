"""Chapas gruesas: cómo la reducción f_y(t) del Anexo B mueve la relación σ_Ed/f_y(t).

Para una chapa de nudo o una platabanda de 40 a 100 mm, EN 1993-1-10 Anexo B ec. B.1
reduce el límite elástico 0,25 N/mm² por milímetro. Con la misma tensión de cálculo,
la utilización sube y el espesor admisible baja; en chapas gruesas los dos efectos se
suman al propio espesor real. Se muestra f_y(t), ratio y, con los puntos de tabla
disponibles para S355JR a T_Ed = −40 °C, el t_max interpolado cuando el ratio queda
dentro del rango cubierto.

Ejecutar:  python examples/brittle_fracture_thick_plate_reduced_yield.py
"""
from steelfatigue.ec3_brittle_fracture import interpolate_max_thickness, reduced_yield_strength

SIGMA_ED = 190.0
FY = 355.0
TABLE_S355JR_TED_MINUS40 = [(0.50, 25.0), (0.75, 15.0)]


def main() -> None:
    print(f"σ_Ed = {SIGMA_ED:.0f} N/mm², S355JR\n")
    print(f"{'t [mm]':>7} {'f_y(t)':>8} {'ratio':>7} {'t_max [mm]':>11}  espesor real frente a t_max")
    for t in (10, 20, 30, 40, 60, 80, 100):
        fy_t = reduced_yield_strength(FY, t)
        ratio = SIGMA_ED / fy_t
        try:
            t_max = interpolate_max_thickness(ratio, TABLE_S355JR_TED_MINUS40)
            verdict = "OK" if t <= t_max else "NO"
            print(f"{t:7d} {fy_t:8.1f} {ratio:7.3f} {t_max:11.1f}  {verdict}")
        except ValueError:
            print(f"{t:7d} {fy_t:8.1f} {ratio:7.3f} {'—':>11}  fuera de los puntos de tabla "
                  f"(ratio < 0,50): hacen falta más puntos de la Tabla 2.1")


if __name__ == "__main__":
    main()
