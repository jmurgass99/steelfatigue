"""Comprobación a rotura frágil de una lista de elementos de una misma estructura.

Nave con puente grúa en zona fría (T₀ = −35 °C): ala de viga carrilera, platabanda
inferior, chapa de nudo de la celosía y alma del pilar, todos en S355JR. Cada fila
lleva su espesor y su tensión de cálculo; el resultado se tabula con el veredicto.
Los puntos de la Tabla 2.1 son los transcritos para S355JR a T_Ed = −40 °C (fichas
W01468/W01469). Si una fila cae fuera del rango de ratios cubierto, se marca en vez
de forzar un número.

Ejecutar:  python examples/brittle_fracture_batch_check_members.py
"""
from steelfatigue.ec3_brittle_fracture import brittle_fracture_check

T0_C = -35.0
FY = 355.0
TABLE_S355JR_TED_MINUS40 = [(0.50, 25.0), (0.75, 15.0)]

MEMBERS = [                     # (nombre, t [mm], σ_Ed [N/mm²])
    ("Ala viga carrilera", 16.0, 207.0),
    ("Platabanda inferior", 22.0, 185.0),
    ("Chapa de nudo celosía", 25.0, 180.0),
    ("Alma del pilar", 12.0, 230.0),
    ("Cartela de apoyo", 30.0, 150.0),
]


def main() -> None:
    print(f"S355JR, T₀ = {T0_C:.0f} °C → T_Ed = −40 °C\n")
    print(f"{'Elemento':<24} {'t':>5} {'σ_Ed':>6} {'ratio':>6} {'t_max':>6}  veredicto")
    n_ok = n_no = n_out = 0
    for name, t, sigma in MEMBERS:
        try:
            r = brittle_fracture_check(sigma, FY, t, TABLE_S355JR_TED_MINUS40, T0_C=T0_C)
        except ValueError:
            n_out += 1
            print(f"{name:<24} {t:5.0f} {sigma:6.0f} {sigma/(FY-0.25*t):6.3f} {'—':>6}  "
                  "fuera de los puntos de tabla")
            continue
        n_ok += r.ok
        n_no += not r.ok
        print(f"{name:<24} {t:5.0f} {sigma:6.0f} {r.sigma_over_fy:6.3f} "
              f"{r.t_max_admissible_mm:6.1f}  {'OK' if r.ok else 'NO VERIFICA'}")
    print(f"\n{n_ok} verifican, {n_no} no verifican, {n_out} sin veredicto por falta de puntos de tabla.")


if __name__ == "__main__":
    main()
