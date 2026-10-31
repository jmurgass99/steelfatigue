"""Viga carrilera: de la historia de tensiones al daño con corrección por tensión media (AISC categoría C).

Historia de una hora de servicio: tensión de peso propio de 40 MPa más el paso de la grúa
(pulso de medio seno hasta +85 MPa, 60 pasadas por hora) y ruido de medida. El flujo es
rainflow → tensión equivalente totalmente alternada por ciclo (Goodman o Gerber, con
S_u = 450 MPa) → vida por la curva de pendiente única de AISC 360-22 Ap. 3, categoría C
(Δσ_C = 69 MPa) → daño de Miner. Se compara con la misma historia centrada en cero para
cuantificar lo que aporta la tensión media de tracción.

Ejecutar:  python examples/crane_girder_history_mean_stress_correction_aisc_category.py
"""
import numpy as np

from steelfatigue.sn_curves_multi import lookup_sn
from steelfatigue.variable_amplitude import damage_from_history

HOURS_PER_YEAR = 3000
DESIGN_LIFE_YEARS = 50
SU_MPA = 450.0


def crane_history(n_passes: int = 60, pts_per_pass: int = 200, seed: int = 3) -> np.ndarray:
    rng = np.random.default_rng(seed)
    t = np.linspace(0.0, 1.0, pts_per_pass)
    pulse = 85.0 * np.sin(np.pi * t)                       # paso de la grúa sobre la sección
    hist = np.concatenate([pulse * rng.uniform(0.7, 1.0) for _ in range(n_passes)])
    return 40.0 + hist + rng.normal(0.0, 2.0, hist.size)   # peso propio + grúa + ruido


def main() -> None:
    curve = lookup_sn("US", "C")
    hist = crane_history()
    print(f"Historia: {hist.size} puntos, σ ∈ [{hist.min():.1f}, {hist.max():.1f}] MPa, "
          f"media {hist.mean():.1f} MPa")
    print(f"Curva: AISC cat. {curve.category}, Δσ_C = {curve.delta_sigma_C_MPa} MPa, m = {curve.slope_m:.0f}\n")

    cases = [("Goodman, historia real", hist, "goodman"),
             ("Gerber, historia real", hist, "gerber"),
             ("Goodman, historia centrada (media 0)", hist - hist.mean(), "goodman")]
    for name, h, crit in cases:
        res = damage_from_history(h, curve, Su_MPa=SU_MPA, criterion=crit)
        D_year = res.total_damage * HOURS_PER_YEAR
        life = 1.0 / D_year if D_year > 0 else float("inf")
        print(f"{name}")
        print(f"  ciclos contados = {res.n_cycles}, D/hora = {res.total_damage:.3e}, "
              f"D/año = {D_year:.3e}, vida = {life:.0f} años "
              f"({'cumple' if life >= DESIGN_LIFE_YEARS else 'NO cumple'} {DESIGN_LIFE_YEARS} años)")
        worst = max(res.detail, key=lambda c: c.damage)
        print(f"  ciclo más dañino: Δσ_eq = {worst.delta_sigma_eq_MPa:.1f} MPa, N = {worst.N_i:.2e}")


if __name__ == "__main__":
    main()
