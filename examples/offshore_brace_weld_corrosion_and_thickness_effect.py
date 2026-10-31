"""Soldadura de riostra de jacket: reducción de la categoría por ambiente marino y por espesor.

Detalle soldado de categoría 71 en chapa de 40 mm (> 25 mm de referencia) expuesto a
agua de mar, atmósfera marina o atmósfera industrial. Se aplica el factor ambiental
del paquete (`corrosion.adjusted_FAT`, factores IIW orientativos) y el efecto de
tamaño de EN 1993-1-9 §7.2.1, k_s = (25/t)^0,2, sobre una curva de pendiente única,
y se compara N para un rango de 50 MPa. Las dos reducciones se componen.

Ejecutar:  python examples/offshore_brace_weld_corrosion_and_thickness_effect.py
"""
from steelfatigue.corrosion import CORROSION_FACTORS, adjusted_FAT
from steelfatigue.sn_curves_multi import SNCurve, cycles_to_failure, size_effect_ks, with_size_effect

FAT_C = 71.0
T_MM = 40.0
DELTA_SIGMA = 50.0


def main() -> None:
    ks = size_effect_ks(T_MM)
    print(f"Categoría base {FAT_C:.0f} MPa, t = {T_MM:.0f} mm → k_s = {ks:.3f}, Δσ = {DELTA_SIGMA} MPa\n")
    print(f"{'ambiente':<18} {'factor':>6} {'Δσ_C amb':>9} {'Δσ_C amb·k_s':>13} {'N (amb)':>10} {'N (amb+t)':>11}")
    for env, f in CORROSION_FACTORS.items():
        dc_env = adjusted_FAT(FAT_C, env)
        base = SNCurve("EU", f"FAT {FAT_C:.0f}/{env}", dc_env)
        thick = with_size_effect(base, T_MM)
        print(f"{env:<18} {f:6.2f} {dc_env:9.1f} {thick.delta_sigma_C_MPa:13.1f} "
              f"{cycles_to_failure(base, DELTA_SIGMA):10.2e} {cycles_to_failure(thick, DELTA_SIGMA):11.2e}")
    print("\nLos factores ambientales son valores orientativos del paquete; para proyecto, "
          "usar la curva en agua de mar con o sin protección catódica de la norma aplicable (p. ej. DNV-RP-C203).")


if __name__ == "__main__":
    main()
