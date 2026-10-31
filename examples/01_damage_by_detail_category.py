"""Daño Palmgren-Miner de un mismo espectro para varias categorías de detalle y γ_Mf.

Caso: viga carrilera de puente grúa, espectro de rangos de tensión estimado para
la vida de servicio. Se compara el daño D para las categorías de detalle FAT de
EN 1993-1-9 habituales en vigas soldadas y para los tres valores de γ_Mf de la
Tabla 3.1 (tolerancia al daño con y sin consecuencias graves, vida segura).

Ejecutar:  python examples/01_damage_by_detail_category.py
"""
from steelfatigue.ec3_sn import palmgren_miner_ec3

# Espectro de servicio (50 años): rango de tensión [MPa] y número de ciclos.
SPECTRUM = [
    {"stress_range_MPa": 120.0, "cycles": 2.0e4},
    {"stress_range_MPa": 90.0, "cycles": 1.5e5},
    {"stress_range_MPa": 60.0, "cycles": 8.0e5},
    {"stress_range_MPa": 35.0, "cycles": 4.0e6},
    {"stress_range_MPa": 20.0, "cycles": 2.0e7},
]
DETAILS = [160, 112, 90, 71, 56, 36]       # Δσ_C [MPa], categorías FAT
GAMMAS = [1.00, 1.15, 1.35]                # EN 1993-1-9 Tabla 3.1


def main() -> None:
    print("Daño acumulado D = Σ n_i/N_i (D <= 1 cumple)\n")
    print(f"{'FAT':>5} | " + " | ".join(f"γ_Mf={g:.2f}" for g in GAMMAS))
    print("-" * 44)
    for fat in DETAILS:
        row = []
        for g in GAMMAS:
            res = palmgren_miner_ec3(SPECTRUM, detail=fat, gamma_Mf=g)
            mark = "" if res["ok"] else " ✗"
            row.append(f"{res['total_damage']:8.3f}{mark:2}")
        print(f"{fat:>5} | " + " | ".join(row))

    # Detalle del caso FAT 71 (soldadura transversal a tope con sobreespesor) y vida segura
    res = palmgren_miner_ec3(SPECTRUM, detail=71, gamma_Mf=1.15)
    print("\nDetalle FAT 71, γ_Mf = 1,15:")
    for b in res["blocks"]:
        N = b["N_i"]
        print(f"  Δσ = {b['stress_range_MPa']:6.1f} MPa  n = {b['cycles']:.2e}  "
              f"N = {'∞' if N == float('inf') else f'{N:.2e}'}  daño = {b['damage']:.4f}")
    print(f"  D total = {res['total_damage']:.3f}  →  {'CUMPLE' if res['ok'] else 'NO CUMPLE'}")


if __name__ == "__main__":
    main()
