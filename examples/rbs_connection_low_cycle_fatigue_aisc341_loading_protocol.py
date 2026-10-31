"""Fatiga oligocíclica de una conexión RBS bajo el protocolo de carga de AISC 341 (Coffin-Manson).

Conexión viga-pilar con sección reducida (RBS) ensayada con el protocolo cíclico de
AISC 341-16 §K2.4b: derivas de 0,375 % (6 ciclos), 0,5 % (6), 0,75 % (6), 1 % (4),
1,5 % (2), 2 % (2), 3 % (2) y 4 % (2). La rotación plástica se toma como la deriva
menos la rotación de fluencia (1 %). `CoffinMansonRBS` convierte cada amplitud en
deformación plástica del ala (factor geométrico 0,5), obtiene N_f con los parámetros
calibrados a ASTM A992 (ε'_f = 0,30, c = −0,60; Engelhardt 2007 / FEMA 350) y acumula
daño de Miner. Se repite el protocolo hasta agotar el daño para estimar cuántas
secuencias resiste la conexión.

Ejecutar:  python examples/rbs_connection_low_cycle_fatigue_aisc341_loading_protocol.py
"""
from steelfatigue.lowcycle import CoffinMansonParams, CoffinMansonRBS

PROTOCOL = [(0.00375, 6), (0.005, 6), (0.0075, 6), (0.01, 4), (0.015, 2), (0.02, 2), (0.03, 2), (0.04, 2)]
THETA_YIELD = 0.01


def plastic_history() -> list[float]:
    hist = []
    for drift, n in PROTOCOL:
        hist.extend([max(drift - THETA_YIELD, 0.0)] * n)
    return hist


def main() -> None:
    rbs = CoffinMansonRBS(CoffinMansonParams(eps_f=0.30, c=-0.60, geometric_factor=0.50))
    hist = plastic_history()
    res = rbs.evaluate(hist)
    print(f"Protocolo AISC 341: {len(hist)} ciclos, {sum(1 for h in hist if h > 0)} con rotación plástica")
    print(f"Daño acumulado D = {res.total_damage:.3f}, ε_p máx = {res.max_plastic_strain:.4f} "
          f"→ {res.status}: {res.message}\n")

    print("N_f por amplitud de rotación plástica:")
    for theta_p in (0.005, 0.01, 0.02, 0.03, 0.04):
        print(f"  θ_p = {theta_p:.3f} rad → ε_p = {theta_p*0.5:.4f} → N_f = {rbs.cycles_to_failure(theta_p*0.5):8.1f}")

    D_once = res.total_damage
    print(f"\nSecuencias completas del protocolo hasta D = 1: {1.0 / D_once:.2f}")


if __name__ == "__main__":
    main()
