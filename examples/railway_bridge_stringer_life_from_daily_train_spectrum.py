"""Vida a fatiga de un larguero de puente ferroviario a partir del espectro diario de trenes.

Larguero metálico soldado con empalme a tope transversal (categoría 71) y, como
alternativa constructiva, cordón longitudinal continuo (categoría 112). El espectro
diario de rangos de tensión se ha agrupado por tipo de bogie (valores de proyecto,
no de una ficha). Se calcula el daño por día con la curva trilineal EN 1993-1-9,
la vida en años (1/(D_día·365)) y el efecto del factor γ_Mf de la Tabla 3.1.

Ejecutar:  python examples/railway_bridge_stringer_life_from_daily_train_spectrum.py
"""
from steelfatigue.ec3_sn import palmgren_miner_ec3

SPECTRUM_PER_DAY = [                               # rango [MPa], ciclos por día
    {"stress_range_MPa": 72.0, "cycles": 40},      # locomotoras pesadas
    {"stress_range_MPa": 52.0, "cycles": 320},     # vagones cargados
    {"stress_range_MPa": 34.0, "cycles": 900},     # vagones vacíos y regionales
    {"stress_range_MPa": 19.0, "cycles": 2400},    # bogies lejanos, vibración
]
DETAILS = {"empalme a tope transversal": 71, "cordón longitudinal continuo": 112}
GAMMAS = {"tolerante al daño, consecuencia baja": 1.00,
          "vida segura, consecuencia baja": 1.15,
          "vida segura, consecuencia alta": 1.35}
DESIGN_LIFE_YEARS = 100


def main() -> None:
    for name, fat in DETAILS.items():
        print(f"\nDetalle: {name} (categoría {fat})")
        for gname, g in GAMMAS.items():
            res = palmgren_miner_ec3(SPECTRUM_PER_DAY, detail=fat, gamma_Mf=g)
            D_day = res["total_damage"]
            life = 1.0 / (D_day * 365.0) if D_day > 0 else float("inf")
            verdict = "cumple" if life >= DESIGN_LIFE_YEARS else "NO cumple"
            print(f"  γ_Mf = {g:.2f} ({gname}): D/día = {D_day:.3e}  "
                  f"vida = {life:8.0f} años  → {verdict} ({DESIGN_LIFE_YEARS} años)")
        res = palmgren_miner_ec3(SPECTRUM_PER_DAY, detail=fat, gamma_Mf=1.35)
        print("  Reparto del daño por bloque (γ_Mf = 1,35):")
        for b in res["blocks"]:
            share = b["damage"] / res["total_damage"] if res["total_damage"] else 0.0
            n_txt = "∞" if b["N_i"] == float("inf") else f"{b['N_i']:.2e}"
            print(f"    Δσ = {b['stress_range_MPa']:5.1f} MPa  n/día = {b['cycles']:5.0f}  "
                  f"N = {n_txt:>9}  {share:6.1%} del daño")


if __name__ == "__main__":
    main()
