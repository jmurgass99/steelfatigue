"""De un historial de tensiones medido (o simulado) al daño de fatiga.

Flujo completo: historial σ(t) → conteo rainflow (ASTM E1049) → espectro de
rangos → daño de Palmgren-Miner con la curva trilineal EN 1993-1-9 → extrapolación
a la vida de diseño.

El historial simulado representa un día de operación de una pasarela peatonal
con tráfico variable (componente lenta + vibración + ruido).

Ejecutar:  python examples/02_rainflow_history_to_damage.py
"""
import numpy as np

from steelfatigue.ec3_sn import palmgren_miner_ec3
from steelfatigue.rainflow_fatpack import rainflow_count

DESIGN_LIFE_DAYS = 50 * 365
DETAIL_FAT = 80          # Δσ_C [MPa]: detalle soldado típico
GAMMA_MF = 1.15          # vida segura, consecuencia baja


def simulated_history(n: int = 20_000, seed: int = 7) -> np.ndarray:
    rng = np.random.default_rng(seed)
    t = np.linspace(0.0, 24.0, n)                       # horas
    slow = 40.0 * np.sin(2 * np.pi * t / 24.0)           # variación diaria lenta
    traffic = 25.0 * np.sin(2 * np.pi * t * 60.0) * (1 + 0.5 * np.sin(2 * np.pi * t / 6.0))
    noise = rng.normal(0.0, 4.0, n)
    return 60.0 + slow + traffic + noise                 # MPa


def main() -> None:
    history = simulated_history()
    cycles = rainflow_count(history)
    print(f"Historial: {history.size} puntos, σ entre {history.min():.1f} y {history.max():.1f} MPa")
    print(f"Ciclos rainflow extraídos: {len(cycles)} (semiciclos cuentan 0.5)\n")

    # Espectro diario: cada ciclo contado es un bloque {Δσ, n}
    spectrum_day = [{"stress_range_MPa": c.range, "cycles": c.count} for c in cycles if c.range > 0]
    res_day = palmgren_miner_ec3(spectrum_day, detail=DETAIL_FAT, gamma_Mf=GAMMA_MF)

    D_day = res_day["total_damage"]
    D_life = D_day * DESIGN_LIFE_DAYS
    print(f"Daño por día (FAT {DETAIL_FAT}, γ_Mf = {GAMMA_MF}): D = {D_day:.3e}")
    print(f"Daño en {DESIGN_LIFE_DAYS // 365} años:               D = {D_life:.3f}")
    if D_life <= 1.0:
        print(f"→ CUMPLE. Vida estimada: {1.0 / D_day / 365:.0f} años")
    else:
        print(f"→ NO CUMPLE. Vida estimada: {1.0 / D_day / 365:.1f} años")

    # Los cinco rangos que más daño aportan
    top = sorted(res_day["blocks"], key=lambda b: -b["damage"])[:5]
    print("\nRangos más dañinos:")
    for b in top:
        print(f"  Δσ = {b['stress_range_MPa']:6.1f} MPa  n/día = {b['cycles']:6.1f}  daño/día = {b['damage']:.2e}")


if __name__ == "__main__":
    main()
