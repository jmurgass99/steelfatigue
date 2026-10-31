"""Tensión de entalla efectiva (IIW, radio ficticio 1 mm) para tres tipos de cordón.

Chapa de 12 mm con tensión nominal de 80 MPa en una unión a tope, en ángulo y
cruciforme. El paquete estima el factor de concentración K_t con su ajuste
calibrado por tipo de cordón y relación t/r, calcula σ_notch = K_t·σ_nom y la
compara con la categoría FAT 225 (IIW, r = 1 mm). Se comprueba si 2·10⁶ y 10⁷
ciclos son admisibles. Fuente: IIW Recommendations (Hobbacher 2008) §2.2.4 y §3.4.

Ejecutar:  python examples/effective_notch_stress_iiw_fat225_weld_types.py
"""
from steelfatigue.notch_stress import NotchInput, notch_endurance_OK, notch_stress

SIGMA_NOM = 80.0
T_MM = 12.0


def main() -> None:
    print(f"σ_nom = {SIGMA_NOM} MPa, t = {T_MM} mm, r_ref = 1 mm, código IIW\n")
    print(f"{'cordón':<11} {'K_t':>5} {'σ_notch':>8} {'FAT':>5}  N=2e6  N=1e7")
    for weld in ("butt", "fillet", "cruciform"):
        inp = NotchInput(sigma_nom_MPa=SIGMA_NOM, weld_type=weld, thickness_mm=T_MM, radius_mm=1.0)
        r = notch_stress(inp)
        ok2 = notch_endurance_OK(inp, 2.0e6)
        ok7 = notch_endurance_OK(inp, 1.0e7)
        print(f"{weld:<11} {r.Kt:5.2f} {r.sigma_notch_MPa:8.1f} {r.fat_class:5.0f}  "
              f"{'OK' if ok2 else 'NO':>4}  {'OK' if ok7 else 'NO':>4}")

    print("\nMismo cordón en ángulo evaluado con las categorías de entalla que el paquete asigna a otros códigos:")
    for code in ("IIW", "AISC", "AS", "NSR"):
        r = notch_stress(NotchInput(SIGMA_NOM, "fillet", T_MM, 1.0, code=code))
        print(f"  {code:<5} FAT = {r.fat_class:5.0f}, σ_notch = {r.sigma_notch_MPa:.1f} MPa")


if __name__ == "__main__":
    main()
