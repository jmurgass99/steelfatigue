"""Factores de seguridad a fatiga de una ménsula de apoyo de maquinaria (diagrama de Haigh).

Ménsula de acero S355 (S_u = 490 MPa, S_y = 355 MPa) con límite de fatiga corregido
S_e = 200 MPa, sometida a una tensión alternante σ_a = 60 MPa sobre una media de
tracción σ_m = 40 MPa (peso de la máquina). Se obtienen los factores de seguridad
según Goodman modificado, Gerber, Soderberg, ASME elíptico y Langer (fluencia de
primer ciclo), y la tensión totalmente alternada equivalente σ_ar para entrar en una
curva S-N con R = −1. Fuente: Shigley, Mechanical Engineering Design, §6-12.

Ejecutar:  python examples/haigh_diagram_safety_factors_machine_support_bracket.py
"""
from steelfatigue.mean_stress import MeanStressInput, equivalent_reversed_stress, safety_factors

SIGMA_A, SIGMA_M = 60.0, 40.0
SE, SU, SY = 200.0, 490.0, 355.0


def main() -> None:
    data = MeanStressInput(sigma_a_MPa=SIGMA_A, sigma_m_MPa=SIGMA_M, Se_MPa=SE, Su_MPa=SU, Sy_MPa=SY)
    print(f"σ_a = {SIGMA_A} MPa, σ_m = {SIGMA_M} MPa, S_e = {SE}, S_u = {SU}, S_y = {SY} MPa\n")
    print("Factor de seguridad n por criterio (n < 1 → fallo previsto):")
    for crit, n in safety_factors(data).items():
        print(f"  {crit:<14} n = {n:6.3f}")

    print("\nTensión equivalente totalmente alternada σ_ar (R = −1):")
    for crit in ("goodman", "gerber", "soderberg"):
        sar = equivalent_reversed_stress(SIGMA_A, SIGMA_M, SU, criterion=crit, Sy=SY)
        print(f"  {crit:<10} σ_ar = {sar:6.2f} MPa  (+{(sar/SIGMA_A - 1):.1%} sobre σ_a)")

    print("\nCon media de compresión no hay penalización:")
    print(f"  σ_m = −40 MPa → σ_ar = {equivalent_reversed_stress(SIGMA_A, -40.0, SU):.2f} MPa")


if __name__ == "__main__":
    main()
