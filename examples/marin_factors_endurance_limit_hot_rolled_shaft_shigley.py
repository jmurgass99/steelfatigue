"""Límite de fatiga corregido de un eje por los factores de Marin (Shigley §6-9 a §6-18).

Eje de acero laminado en caliente, S_u = 620 MPa, d = 40 mm, flexión rotatoria, 20 °C
y confiabilidad del 99 %. Se obtiene S_e' = 0,5·S_u y los factores k_a (superficie),
k_b (tamaño), k_c (carga), k_d (temperatura) y k_e (confiabilidad). Se compara con el
mismo eje mecanizado y rectificado, y con carga axial, para ver qué factor pesa más.

Ejecutar:  python examples/marin_factors_endurance_limit_hot_rolled_shaft_shigley.py
"""
from steelfatigue.endurance_factors import EnduranceInput, endurance_limit

BASE = dict(Su_MPa=620.0, d_mm=40.0, loading="bending", T_C=20.0, reliability=0.99)


def show(label: str, inp: EnduranceInput) -> None:
    r = endurance_limit(inp)
    print(f"{label:<34} ka={r['ka']:.3f} kb={r['kb']:.3f} kc={r['kc']:.2f} kd={r['kd']:.3f} "
          f"ke={r['ke']:.3f}  S_e' = {r['Se_prime_MPa']:.0f} → S_e = {r['Se_MPa']:.1f} MPa")


def main() -> None:
    print("Eje S_u = 620 MPa, d = 40 mm, confiabilidad 99 %\n")
    show("laminado en caliente, flexión", EnduranceInput(finish="hot-rolled", **BASE))
    show("mecanizado, flexión", EnduranceInput(finish="machined", **BASE))
    show("rectificado, flexión", EnduranceInput(finish="ground", **BASE))
    show("mecanizado, carga axial", EnduranceInput(finish="machined", **{**BASE, "loading": "axial"}))
    show("mecanizado, torsión", EnduranceInput(finish="machined", **{**BASE, "loading": "torsion"}))
    show("mecanizado, flexión, 250 °C", EnduranceInput(finish="machined", **{**BASE, "T_C": 250.0}))
    show("mecanizado, flexión, conf. 50 %", EnduranceInput(finish="machined", **{**BASE, "reliability": 0.50}))


if __name__ == "__main__":
    main()
