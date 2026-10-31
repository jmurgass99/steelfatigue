"""Punto caliente cuando la malla no tiene nodos exactamente a t/2 y 3t/2.

Lo habitual: el modelo da tensiones en nodos a 4, 8, 14, 22 y 35 mm del pie del cordón
de una chapa de 20 mm. `hot_spot_from_radial_samples` interpola linealmente entre los
dos nodos que rodean la distancia pedida (y extrapola con los dos primeros si se pide
la distancia 0). Se obtienen σ(t/2) y σ(3t/2) por interpolación y después la
extrapolación lineal IIW, y se compara con la extrapolación directa a distancia 0.

Ejecutar:  python examples/hot_spot_from_arbitrary_fem_node_distances.py
"""
from steelfatigue.hotspot import HotSpotInput, hot_spot_from_radial_samples, hot_spot_stress

T_MM = 20.0
RADII_MM = [4.0, 8.0, 14.0, 22.0, 35.0]
STRESSES = [171.0, 152.0, 134.0, 125.0, 112.0]   # MPa


def main() -> None:
    print("Lecturas FEM (distancia al pie del cordón → tensión):")
    for r, s in zip(RADII_MM, STRESSES):
        print(f"  {r:5.1f} mm → {s:6.1f} MPa")

    s_t2 = hot_spot_from_radial_samples(STRESSES, RADII_MM, T_MM, hot_spot_distance_mm=0.5 * T_MM)
    s_3t2 = hot_spot_from_radial_samples(STRESSES, RADII_MM, T_MM, hot_spot_distance_mm=1.5 * T_MM)
    s_hs_iiw = hot_spot_stress(HotSpotInput(s_t2, s_3t2, T_MM))
    s_hs_direct = hot_spot_from_radial_samples(STRESSES, RADII_MM, T_MM, hot_spot_distance_mm=0.0)

    print(f"\nσ(t/2 = {0.5*T_MM:.0f} mm) interpolada  = {s_t2:.1f} MPa")
    print(f"σ(3t/2 = {1.5*T_MM:.0f} mm) interpolada = {s_3t2:.1f} MPa")
    print(f"σ_hs IIW lineal sobre esas dos lecturas = {s_hs_iiw:.1f} MPa")
    print(f"σ_hs extrapolando los dos nodos más cercanos al cordón (4 y 8 mm) = {s_hs_direct:.1f} MPa")
    print("\nLa extrapolación con los nodos más cercanos recoge el pico de entalla y sobreestima; "
          "el esquema IIW a t/2 y 3t/2 es el que corresponde a las categorías hot-spot.")


if __name__ == "__main__":
    main()
