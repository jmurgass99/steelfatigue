"""Rango equivalente de daño (DEL) de una junta de torre eólica a partir del rainflow.

Historia de tensiones de 10 minutos en la soldadura circunferencial de una torre
(oscilación de primer modo modulada por ráfagas). Se cuenta por rainflow, se
extrapola el recuento a 20 años de operación y se calcula a mano el rango
equivalente de daño para m = 3 y N_ref = 10⁷ ciclos (práctica habitual en eólica):

    Δσ_eq = ( Σ n_i·Δσ_i^m / N_ref )^(1/m)

Se comprueba que un único bloque {Δσ_eq, N_ref} produce el mismo daño de Miner que
el espectro completo sobre una curva de pendiente única (categoría 71 sin cut-off,
para que la identidad sea exacta) y, por separado, se evalúa el mismo espectro con
la curva trilineal de EN 1993-1-9, donde los ciclos bajo el cut-off no dañan.
El DEL es el dato que se intercambia con el fabricante del aerogenerador en lugar
del espectro completo.

Ejecutar:  python examples/wind_turbine_tower_damage_equivalent_range_from_rainflow.py
"""
import numpy as np

from steelfatigue.ec3_sn import palmgren_miner_ec3
from steelfatigue.rainflow_fatpack import rainflow_count
from steelfatigue.sn_curves_multi import SNCurve, cycles_to_failure

M = 3.0
N_REF = 1.0e7
FAT = 71.0
YEARS = 20
WINDOWS_PER_YEAR = 365 * 24 * 6
CURVE = SNCurve("EU", "FAT 71", FAT, slope_m=M, cutoff_N=1e30)   # sin cut-off: identidad exacta


def tower_history(duration_s: float = 600.0, fs: float = 20.0, seed: int = 11) -> np.ndarray:
    rng = np.random.default_rng(seed)
    t = np.arange(0.0, duration_s, 1.0 / fs)
    gust = 1.0 + 0.5 * np.sin(2 * np.pi * t / 45.0)
    first_mode = 9.0 * gust * np.sin(2 * np.pi * 0.32 * t)        # f₁ ≈ 0,32 Hz
    thrust = 35.0 + 8.0 * np.sin(2 * np.pi * t / 120.0)           # empuje medio variable
    return thrust + first_mode + rng.normal(0.0, 0.8, t.size)


def main() -> None:
    hist = tower_history()
    cycles = [c for c in rainflow_count(hist) if c.range > 0]
    n_win = np.array([c.count for c in cycles])
    ds = np.array([c.range for c in cycles])
    n_life = n_win * WINDOWS_PER_YEAR * YEARS
    print(f"Ventana de 10 min: {len(cycles)} ciclos rainflow, Δσ máx = {ds.max():.1f} MPa, Σn = {n_win.sum():.1f}")
    print(f"Extrapolación a {YEARS} años: {WINDOWS_PER_YEAR * YEARS} ventanas, Σn = {n_life.sum():.3e} ciclos")

    ds_eq = (np.sum(n_life * ds ** M) / N_REF) ** (1.0 / M)
    print(f"\nΔσ_eq (m = {M:.0f}, N_ref = {N_REF:.0e}, {YEARS} años) = {ds_eq:.2f} MPa")

    D_spectrum = float(np.sum(n_life / np.array([cycles_to_failure(CURVE, d) for d in ds])))
    D_del = N_REF / cycles_to_failure(CURVE, ds_eq)
    print(f"Daño del espectro completo (recta m = 3, sin cut-off) = {D_spectrum:.4f}")
    print(f"Daño del bloque equivalente                          = {D_del:.4f}  "
          f"(diferencia relativa {abs(D_del / D_spectrum - 1):.1e})")

    spectrum = [{"stress_range_MPa": float(d), "cycles": float(n)} for d, n in zip(ds, n_life)]
    res = palmgren_miner_ec3(spectrum, detail=FAT, gamma_Mf=1.0)
    n_nodamage = sum(1 for b in res["blocks"] if b["N_i"] == float("inf"))
    print(f"\nMismo espectro con la curva trilineal EN 1993-1-9 (FAT 71, γ_Mf = 1): D = {res['total_damage']:.4f}; "
          f"{n_nodamage} de {len(spectrum)} niveles quedan bajo el cut-off y no dañan.")


if __name__ == "__main__":
    main()
