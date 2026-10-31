"""Carga admisible para una vida requerida: curva S-N invertida (EN 1993-1-9 §7.1).

Exercise 7b «Fatigue and brittle fracture» del máster UPC (ficha W01508). En vez de
calcular N para un Δσ dado, se pide la carga P que agota exactamente N = 500 000
ciclos en dos detalles de una misma viga:
  - apoyo interior con soldadura transversal, categoría 80, Δσ = 2,50·10⁻⁴·P [MPa, P en N];
  - conexión a un solo lado, categoría 36, Δσ = 4,133·10⁻⁴·P.
Resultado de la ficha (recalculado a mano antes de anclarlo): P = 376,3 kN y P = 102,4 kN.
La categoría 36 gobierna el diseño aunque su tensión por unidad de carga sea mayor.

Ejecutar:  python examples/admissible_load_for_required_life_exam_w01508.py
"""
from steelfatigue.ec3_sn import (
    EC3_NC,
    constant_amplitude_limit,
    ec3_cycles_to_failure,
)

N_REQUIRED = 500_000
GAMMA_MF = 1.35

CASES = [
    ("Apoyo interior, soldadura transversal (cat. 80)", 80.0, 2.50e-4),
    ("Conexión a un solo lado (cat. 36)", 36.0, 4.133e-4),
]


def admissible_load_N(detail: float, k_MPa_per_N: float, N_req: float, gamma: float) -> float:
    """Bisección sobre P: N(Δσ(P)) es monótona decreciente, válida en los tres tramos."""
    dc_d = detail / gamma
    lo, hi = 1.0, 5.0e6
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if ec3_cycles_to_failure(k_MPa_per_N * mid, dc_d) > N_req:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def main() -> None:
    print(f"Vida requerida N = {N_REQUIRED:,} ciclos, γ_Mf = {GAMMA_MF}\n")
    for name, detail, k in CASES:
        dc_d = detail / GAMMA_MF
        P = admissible_load_N(detail, k, N_REQUIRED, GAMMA_MF)
        ds = k * P
        # Comprobación cerrada: en el tramo m = 3, Δσ_adm = Δσ_C,d·(N_C/N)^(1/3)
        ds_closed = dc_d * (EC3_NC / N_REQUIRED) ** (1.0 / 3.0)
        branch = "m = 3" if ds >= constant_amplitude_limit(dc_d) else "m = 5"
        print(name)
        print(f"  Δσ_C,d = {dc_d:.2f} MPa, codo Δσ_D,d = {constant_amplitude_limit(dc_d):.2f} MPa")
        print(f"  Δσ admisible = {ds:.2f} MPa (tramo {branch}); forma cerrada m=3: {ds_closed:.2f} MPa")
        print(f"  P admisible  = {P/1e3:.1f} kN\n")
    P80 = admissible_load_N(80.0, 2.50e-4, N_REQUIRED, GAMMA_MF)
    P36 = admissible_load_N(36.0, 4.133e-4, N_REQUIRED, GAMMA_MF)
    print(f"Gobierna la categoría 36: P = {P36/1e3:.1f} kN frente a {P80/1e3:.1f} kN "
          f"({P36/P80:.0%} de la carga del detalle de categoría 80).")


if __name__ == "__main__":
    main()
