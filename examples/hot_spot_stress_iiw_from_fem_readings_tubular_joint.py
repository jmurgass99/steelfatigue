"""Tensión de punto caliente IIW a partir de lecturas de un modelo de elementos finitos.

Unión soldada de chapa de 20 mm (nudo de celosía tubular): el modelo de cáscara da
tensiones principales a t/2 = 10 mm y 3t/2 = 30 mm del pie del cordón, y una tercera
lectura a 5t/2 = 50 mm. Se extrapola al pie del cordón con los esquemas lineal
(IIW tipo a, 1,67·σ(t/2) − 0,67·σ(3t/2)) y cuadrático (2,52·σ(t/2) − 2,24·σ(3t/2) +
0,72·σ(5t/2)), y el servicio `run_hotspot_analysis` estima la vida con la categoría
hot-spot (FAT 100 para cordón no portante, FAT 90 para portante). Fuente: IIW
Recommendations for Fatigue Design of Welded Joints (Hobbacher, 2008), §2.2.3.

Ejecutar:  python examples/hot_spot_stress_iiw_from_fem_readings_tubular_joint.py
"""
from steelfatigue.hotspot import HotSpotInput, hot_spot_stress
from steelfatigue.services.hotspot_service import run_hotspot_analysis

T_MM = 20.0
SIGMA_T2, SIGMA_3T2, SIGMA_5T2 = 142.0, 118.0, 104.0   # MPa, rango de tensión leído en el FEM


def main() -> None:
    lin = hot_spot_stress(HotSpotInput(SIGMA_T2, SIGMA_3T2, T_MM, method="linear"))
    quad = hot_spot_stress(HotSpotInput(SIGMA_T2, SIGMA_3T2, T_MM, method="quadratic",
                                        sigma_5t_half=SIGMA_5T2))
    print(f"Lecturas FEM: σ(t/2) = {SIGMA_T2}, σ(3t/2) = {SIGMA_3T2}, σ(5t/2) = {SIGMA_5T2} MPa")
    print(f"σ_hs lineal (tipo a)    = {lin:.1f} MPa")
    print(f"σ_hs cuadrática (tipo b) = {quad:.1f} MPa  (+{quad/lin-1:.1%} frente a la lineal)\n")

    for fat, label in ((100.0, "cordón no portante"), (90.0, "cordón portante")):
        for method, s5 in (("linear", None), ("quadratic", SIGMA_5T2)):
            r = run_hotspot_analysis(SIGMA_T2, SIGMA_3T2, T_MM, weld_type="fillet", fat_class=fat,
                                     method=method, sigma_5t_half=s5, gamma_mf=1.15)
            print(f"FAT {fat:.0f} ({label}), {method:<9}: σ_hs = {r.sigma_hot_spot_MPa:6.1f} MPa, "
                  f"N ≈ {r.estimated_life_cycles:.2e} ciclos (γ_Mf = 1,15, recta m = 3)")
    r3 = run_hotspot_analysis(SIGMA_T2, SIGMA_3T2, T_MM, weld_type="fillet", fat_class=90.0, gamma_mf=1.15)
    rt = run_hotspot_analysis(SIGMA_T2, SIGMA_3T2, T_MM, weld_type="fillet", fat_class=90.0, gamma_mf=1.15,
                              use_trilinear_ec3=True)
    print(f"\nFAT 90 lineal con la curva trilineal de EN 1993-1-9 (use_trilinear_ec3=True): N ≈ {rt.estimated_life_cycles:.2e} "
          f"frente a {r3.estimated_life_cycles:.2e} con la recta m = 3 "
          f"({'iguales: el rango está por encima del codo de 5·10⁶' if abs(rt.estimated_life_cycles / r3.estimated_life_cycles - 1) < 1e-9 else 'distintas: el rango cae por debajo del codo'})")


if __name__ == "__main__":
    main()
