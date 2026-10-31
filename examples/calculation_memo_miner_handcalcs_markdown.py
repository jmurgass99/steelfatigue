"""Memoria de cálculo de Palmgren-Miner en Markdown y LaTeX (extra `memos`, handcalcs).

Mismo ejemplo resuelto del máster que ancla `ec3_sn` (ficha W01510, Exercise 9):
viga IPE 240, categoría 80, γ_Mf = 1,15, dos bloques de carga. `render_miner_memo`
devuelve el daño total, el desglose por bloque y el texto de la memoria listo para
pegar en un informe. Requiere `pip install "steelfatigue[memos]"`.

Ejecutar:  python examples/calculation_memo_miner_handcalcs_markdown.py
"""
from steelfatigue.memos.miner import MinerMemoInput, render_miner_memo


def main() -> None:
    memo = render_miner_memo(MinerMemoInput(
        detail_category=80.0,
        gamma_mf=1.15,
        spectrum=[
            {"label": "P1 (vano)", "stress_range_MPa": 75.16, "cycles": 1.0e6},
            {"label": "P2 (voladizo)", "stress_range_MPa": 8.67, "cycles": 2.0e6},
        ],
    ))
    print(f"D total = {memo.total_damage:.3f} → {'CUMPLE' if memo.pass_check else 'NO CUMPLE'}")
    for b in memo.blocks:
        n_txt = "∞" if b.N_endurance == float("inf") else f"{b.N_endurance:.3e}"
        print(f"  {b.label:<14} Δσ = {b.stress_range_MPa:6.2f} MPa  n = {b.cycles:.1e}  "
              f"N = {n_txt:>10}  n/N = {b.damage:.4f}")

    print("\n--- Markdown (primeras líneas) ---")
    print("\n".join(memo.markdown.splitlines()[:18]))
    print(f"\nLaTeX: {len(memo.latex)} caracteres generados")


if __name__ == "__main__":
    main()
