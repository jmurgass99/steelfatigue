"""Conteo rainflow de la señal del ejemplo de ASTM E1049-85 §5.4.4.

Secuencia de picos y valles −2, 1, −3, 5, −1, 3, −4, 4, −2 (unidades arbitrarias).
La tabla del estándar para el método rainflow da: rango 3 → 0,5 ciclo; rango 4 →
1,5 ciclos; rango 6 → 0,5; rango 8 → 1,0; rango 9 → 0,5 (total 4 ciclos). El paquete
delega el conteo en `fatpack` y devuelve los ciclos cerrados con count = 1 y los
semiciclos del residuo con count = 0,5; aquí se listan tal cual salen y se comparan
los totales.

Ejecutar:  python examples/rainflow_astm_e1049_example_signal.py
"""
from collections import Counter

from steelfatigue.rainflow_fatpack import rainflow_count, rainflow_count_arrays

ASTM_SIGNAL = [-2, 1, -3, 5, -1, 3, -4, 4, -2]
ASTM_TABLE = {3: 0.5, 4: 1.5, 6: 0.5, 8: 1.0, 9: 0.5}


def main() -> None:
    cycles = rainflow_count(ASTM_SIGNAL)
    print("Ciclos devueltos por rainflow_count:")
    for c in cycles:
        print(f"  rango = {c.range:4.1f}  media = {c.mean:5.1f}  count = {c.count}")

    by_range = Counter()
    for c in cycles:
        by_range[round(c.range)] += c.count
    print("\nRango → ciclos (paquete)  |  tabla ASTM E1049")
    for rng in sorted(set(by_range) | set(ASTM_TABLE)):
        print(f"  {rng:2d} → {by_range.get(rng, 0):4.1f}  |  {ASTM_TABLE.get(rng, 0):4.1f}")
    print(f"\nTotal ciclos: paquete {sum(by_range.values()):.1f}, ASTM {sum(ASTM_TABLE.values()):.1f}")

    means, ranges, counts = rainflow_count_arrays(ASTM_SIGNAL)
    print(f"\nVersión vectorizada: {len(ranges)} entradas, rango máximo {ranges.max():.1f}, "
          f"Σ counts = {counts.sum():.1f}")


if __name__ == "__main__":
    main()
