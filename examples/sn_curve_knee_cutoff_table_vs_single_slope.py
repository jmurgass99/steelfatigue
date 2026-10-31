"""Codo, cut-off y tramo m = 5 de cada categoría FAT: cuánto cambia frente a una recta única m = 3.

Tabla de Δσ_D (N = 5·10⁶) y Δσ_L (N = 10⁸) para las categorías del catálogo del
paquete, y comparación de N en el tramo m = 5 entre la curva trilineal de EN 1993-1-9
§7.1 (`ec3_sn`) y la recta única de pendiente 3 que usa `FatigueEvaluator` (uso
heredado, pensado para AISC/AS con cut-off a 10⁸). Los valores del codo coinciden
con la tabla de los apuntes UPC (ficha W01419): 160 → 117,9; 112 → 82,5; 71 → 52,3;
50 → 36,8; 36 → 26,5 MPa.

Ejecutar:  python examples/sn_curve_knee_cutoff_table_vs_single_slope.py
"""
from steelfatigue.ec3_sn import constant_amplitude_limit, cutoff_limit, ec3_cycles_to_failure
from steelfatigue.sn_curves import FatigueEvaluator
from steelfatigue.wohler_db import list_fat_categories


def main() -> None:
    print(f"{'FAT':>8} {'Δσ_D [MPa]':>11} {'Δσ_L [MPa]':>11} | "
          f"{'Δσ=0,9·Δσ_D':>12} {'N trilineal':>12} {'N recta m=3':>12} {'ratio':>6}")
    print("-" * 82)
    for fat in list_fat_categories():
        dc = fat.delta_sigma_C
        dD, dL = constant_amplitude_limit(dc), cutoff_limit(dc)
        ds = 0.9 * dD                                   # dentro del tramo m = 5
        n_tri = ec3_cycles_to_failure(ds, dc)
        n_single = FatigueEvaluator(dc, gamma_mf=1.0).calculate_endurance(ds)
        print(f"{fat.code:>8} {dD:11.1f} {dL:11.1f} | {ds:12.1f} {n_tri:12.3e} {n_single:12.3e} "
              f"{n_tri / n_single:6.2f}")

    print("\nPor debajo del cut-off la curva trilineal no acumula daño; la recta única sí:")
    dc = 90.0
    ds = 0.9 * cutoff_limit(dc)
    print(f"  FAT 90, Δσ = {ds:.1f} MPa (< Δσ_L = {cutoff_limit(dc):.1f}): "
          f"N trilineal = {ec3_cycles_to_failure(ds, dc)},  "
          f"N recta m=3 = {FatigueEvaluator(dc, gamma_mf=1.0).calculate_endurance(ds):.3e}")
    print("\nUsa `ec3_sn` para EN 1993-1-9; `FatigueEvaluator` queda para espectros de alta "
          "tensión donde todo cae en el tramo m = 3 o para normas de pendiente única.")


if __name__ == "__main__":
    main()
