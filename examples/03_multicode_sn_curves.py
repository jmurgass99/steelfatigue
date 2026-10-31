"""Comparación multinorma de curvas S-N y efecto de tamaño.

Para un mismo rango de tensión se obtiene el número de ciclos resistentes según
las categorías de EN 1993-1-9 (FAT), AISC 360-22 Apéndice 3 (categorías A-E)
y las demás normas cargadas en el catálogo, y se aplica la reducción por
espesor (efecto de tamaño) a una placa gruesa.

Ejecutar:  python examples/03_multicode_sn_curves.py
"""
from steelfatigue.sn_curves_multi import (
    AISC_CATEGORIES,
    cycles_to_failure,
    equivalent_categories,
    lookup_sn,
    size_effect_ks,
    with_size_effect,
)
from steelfatigue.wohler_db import list_fat_categories

DELTA_SIGMA = 80.0   # MPa


def main() -> None:
    print(f"Ciclos resistentes para Δσ = {DELTA_SIGMA} MPa\n")

    print("EN 1993-1-9 (catálogo FAT):")
    for fat in list_fat_categories()[:8]:
        curve = lookup_sn("EU", fat.code) if lookup_sn("EU", fat.code) else None
        n = cycles_to_failure(curve, DELTA_SIGMA) if curve else float("nan")
        print(f"  {fat.code:>8}  Δσ_C = {fat.delta_sigma_C:6.1f} MPa  N = {n:.3e}")

    print("\nAISC 360-22 Apéndice 3:")
    for curve in AISC_CATEGORIES:
        print(f"  Cat. {curve.category:>2}  Δσ_C = {curve.delta_sigma_C_MPa:6.1f} MPa  "
              f"m = {curve.slope_m:.0f}  N = {cycles_to_failure(curve, DELTA_SIGMA):.3e}")

    # Efecto de tamaño: placa de 50 mm frente a la referencia de 25 mm
    base = AISC_CATEGORIES[2]
    thick = with_size_effect(base, thickness_mm=50.0)
    print(f"\nEfecto de tamaño (t = 50 mm): k_s = {size_effect_ks(50.0):.3f}")
    print(f"  {base.category}: Δσ_C {base.delta_sigma_C_MPa:.1f} → {thick.delta_sigma_C_MPa:.1f} MPa, "
          f"N {cycles_to_failure(base, DELTA_SIGMA):.2e} → {cycles_to_failure(thick, DELTA_SIGMA):.2e}")

    # Categorías equivalentes a un FAT 90 en las demás normas
    print("\nCategorías equivalentes a Δσ_C = 90 MPa:")
    for c in equivalent_categories(90.0):
        print(f"  {c.code:>3} {c.category:>8}  Δσ_C = {c.delta_sigma_C_MPa:.1f} MPa")


if __name__ == "__main__":
    main()
