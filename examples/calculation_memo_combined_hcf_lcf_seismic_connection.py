"""Memoria combinada: fatiga de alto ciclo (viento y tráfico) más oligocíclica (sismo) en una conexión.

Conexión soldada de categoría 71 en una estructura que acumula daño de alto ciclo
en servicio (espectro de rangos) y, además, debe sobrevivir a un sismo de proyecto
que impone amplitudes de deformación total en el ala (0,4 %, 0,6 %, 0,8 % y 1,0 %,
varias veces). `render_combined_fatigue_memo` suma D_HCF (Miner, EN 1993-1-9) y
D_LCF (Basquin + Coffin-Manson con parámetros tipo A992) y emite la memoria.
Requiere `pip install "steelfatigue[memos]"`.

Ejecutar:  python examples/calculation_memo_combined_hcf_lcf_seismic_connection.py
"""
from steelfatigue.memos.miner import MinerMemoInput
from steelfatigue.memos.miner_coffin_manson import CoffinMansonMemoInput, render_combined_fatigue_memo

HCF = MinerMemoInput(
    detail_category=71.0, gamma_mf=1.15,
    spectrum=[
        {"label": "viento fuerte", "stress_range_MPa": 60.0, "cycles": 4.0e5},
        {"label": "tráfico", "stress_range_MPa": 40.0, "cycles": 6.0e6},
    ],
)
LCF = CoffinMansonMemoInput(
    sigma_f=900.0, b=-0.10, eps_f=0.30, c=-0.60, E=200_000.0,
    strain_amplitudes=[0.004] * 6 + [0.006] * 4 + [0.008] * 2 + [0.010] * 2,
)


def main() -> None:
    res = render_combined_fatigue_memo(hcf_input=HCF, lcf_input=LCF)
    print(f"D_HCF = {res.D_HCF:.4f}   D_LCF = {res.D_LCF:.4f}   D_total = {res.D_total:.4f} "
          f"→ {'CUMPLE' if res.pass_check else 'NO CUMPLE'}")
    print("\nCiclos LCF (amplitud de deformación → N_f, daño):")
    for c in res.lcf_cycles[:6]:
        print(f"  #{c.cycle_index:<3} ε_a = {c.strain_amplitude:.4f} → N_f = {c.N_f:9.1f}  n/N = {c.damage:.4f}")
    print(f"  … {len(res.lcf_cycles)} ciclos en total")

    md = getattr(res, "markdown", "")
    if md:
        print("\n--- Markdown (primeras líneas) ---")
        print("\n".join(md.splitlines()[:14]))


if __name__ == "__main__":
    main()
