"""Vida residual de una grieta detectada en el ala de una viga de puente (ley de Paris).

Inspección: grieta de borde de 2 mm en el ala traccionada. Tensión máxima de servicio
150 MPa, rango de tensión por tráfico 80 MPa, Y = 1,12 (grieta de borde). Tamaño
crítico desde la tenacidad: a_c = (K_IC / (Y·σ_max))² / π con K_IC = 60 MPa·√m.
Se integra da/dN = C·ΔK^m con las constantes por defecto del paquete (C = 6,9·10⁻¹²,
m = 3, con ΔK en MPa·√mm y da en mm, acero ferrítico-perlítico) y se traduce la vida
en ciclos a años con 1,5·10⁶ ciclos de tráfico al año, para fijar el intervalo de
inspección (mitad de la vida residual).

Ejecutar:  python examples/paris_law_remaining_life_bridge_girder_flange_crack.py
"""
import math

from steelfatigue.paris_law import ParisInput, integrate_paris

A_INITIAL_MM = 2.0
SIGMA_MAX = 150.0
DELTA_SIGMA = 80.0
Y = 1.12
K_IC_MPA_SQRT_M = 60.0
CYCLES_PER_YEAR = 1.5e6


def main() -> None:
    a_c_m = (K_IC_MPA_SQRT_M / (Y * SIGMA_MAX)) ** 2 / math.pi
    a_c_mm = a_c_m * 1000.0
    print(f"a_c = (K_IC/(Y·σ_max))²/π = {a_c_mm:.1f} mm")

    res = integrate_paris(ParisInput(a_initial_mm=A_INITIAL_MM, a_critical_mm=a_c_mm,
                                     delta_sigma_MPa=DELTA_SIGMA, Y=Y, n_increments=400))
    years = res.N_cycles / CYCLES_PER_YEAR
    print(f"N de {A_INITIAL_MM} mm a {a_c_mm:.1f} mm = {res.N_cycles:.3e} ciclos = {years:.1f} años")
    print(f"Intervalo de inspección propuesto (vida/2): {years/2:.1f} años\n")

    print("Crecimiento de la grieta (N acumulado → a):")
    for N, a in res.a_vs_N[::50]:
        print(f"  {N:12.0f} ciclos ({N/CYCLES_PER_YEAR:5.1f} años) → a = {a:5.2f} mm")
    print("\nLa mitad de la vida se consume mientras la grieta es menor de "
          f"{next(a for N, a in res.a_vs_N if N >= res.N_cycles/2):.1f} mm: detectarla pronto es lo que cuenta.")


if __name__ == "__main__":
    main()
