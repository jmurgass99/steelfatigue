"""Fatiga multiaxial Smith-Watson-Topper: plano crítico desde una historia de tensiones del FEM.

Punto de una chapa de nudo con tensiones σ_xx, σ_yy y τ_xy no proporcionales a lo
largo de un ciclo de carga (16 instantes). `critical_plane_search` gira el plano de
0 a 180° y busca el que maximiza P_SWT = σ_max·ε_a (con E = 200 GPa); después
`cycles_to_failure_swt` resuelve N_f en la curva de Basquin–Coffin-Manson con los
parámetros por defecto del paquete (σ'_f = 1000 MPa, ε'_f = 0,5, b = −0,10,
c = −0,60), que deben sustituirse por los del acero ensayado.

Ejecutar:  python examples/swt_multiaxial_critical_plane_from_fem_stress_history.py
"""
import math

from steelfatigue.multiaxial import SWTInput, critical_plane_search, cycles_to_failure_swt

N_STEPS = 16
# Ciclo no proporcional: σ_xx y τ_xy desfasados 90°.
SXX = [120.0 * math.sin(2 * math.pi * i / N_STEPS) for i in range(N_STEPS)]
SYY = [40.0 * math.sin(2 * math.pi * i / N_STEPS) for i in range(N_STEPS)]
SXY = [60.0 * math.cos(2 * math.pi * i / N_STEPS) for i in range(N_STEPS)]


def main() -> None:
    best = critical_plane_search({"sxx": SXX, "syy": SYY, "sxy": SXY}, n_angles=36)
    print(f"Plano crítico: θ = {math.degrees(best['theta_rad']):.1f}°")
    print(f"  σ_max = {best['sigma_max']:.1f} MPa, ε_a = {best['eps_a']:.3e}, "
          f"P_SWT = {best['P_SWT']:.4f} MPa")

    N = cycles_to_failure_swt(SWTInput(sigma_max_MPa=best["sigma_max"], eps_amplitude=best["eps_a"]))
    print(f"  N_f (SWT, parámetros por defecto) = {N:.3e} ciclos")

    print("\nMismo plano con amplitudes de deformación crecientes (daño plástico):")
    for eps in (0.0008, 0.0015, 0.003, 0.006):
        n = cycles_to_failure_swt(SWTInput(sigma_max_MPa=best["sigma_max"], eps_amplitude=eps))
        print(f"  ε_a = {eps:.4f} → N_f = {n:.3e}")

    sh = critical_plane_search({"sxx": SXX, "syy": SYY, "sxy": SXY}, n_angles=36, include_shear=True)
    print("\nCon include_shear=True cada criterio busca su propio plano (elástico, Δγ = Δτ/G):")
    print(f"  SWT          θ = {math.degrees(sh['theta_rad']):5.1f}°  P_SWT = {sh['P_SWT']:.4f} MPa")
    print(f"  Findley      θ = {math.degrees(sh['findley_theta_rad']):5.1f}°  P_F = τ_a + 0,30·σ_n,max = {sh['findley_MPa']:.1f} MPa (τ_a = {sh['tau_a']:.1f} MPa)")
    print(f"  Brown-Miller θ = {math.degrees(sh['brown_miller_theta_rad']):5.1f}°  P_BM = Δγ/2 + Δε_n = {sh['brown_miller']:.3e}")


if __name__ == "__main__":
    main()
