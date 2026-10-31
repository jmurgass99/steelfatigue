"""Fuerzas en las interfaces de una cartela de arriostramiento por el Método de la Fuerza Uniforme.

Cartela de un pórtico arriostrado (AISC Manual Part 13, Thornton-Muir): α = 380 mm,
β = 305 mm, e_c = 152 mm (medio canto del pilar), e_b = 178 mm (medio canto de la
viga), diagonal a 900 kN de tracción. Con θ implícito por la geometría las cuatro
interfaces quedan libres de momento y las sumas ΣH = P·cos θ, ΣV = P·sin θ se cumplen.
Si se impone otro ángulo (42°), `equilibrium_check` avisa de que la geometría no
satisface la restricción del UFM. Estas fuerzas son la entrada del cálculo de fatiga
de las soldaduras de la cartela (categorías FAT del catálogo).

Ejecutar:  python examples/gusset_plate_uniform_force_method_brace_connection.py
"""
import math

from steelfatigue.lowcycle import UFMGeometry, UFMGussetForces

GEOM = UFMGeometry(alpha=380.0, beta=305.0, ec=152.0, eb=178.0)
P_BRACE_KN = 900.0


def main() -> None:
    ufm = UFMGussetForces(GEOM)
    theta = GEOM.implied_theta()
    f = ufm.interface_forces(P_BRACE_KN, theta)
    print(f"θ implícito = atan((β+e_b)/(α+e_c)) = {math.degrees(theta):.2f}°")
    print(f"  Interfaz cartela-viga:   H_b = {f.H_b:7.1f} kN   V_b = {f.V_b:7.1f} kN")
    print(f"  Interfaz cartela-pilar:  H_c = {f.H_c:7.1f} kN   V_c = {f.V_c:7.1f} kN")
    print(f"  ΣH = {f.H_b + f.H_c:.1f} kN frente a P·cos θ = {P_BRACE_KN*math.cos(theta):.1f} kN")
    print(f"  ΣV = {f.V_b + f.V_c:.1f} kN frente a P·sin θ = {P_BRACE_KN*math.sin(theta):.1f} kN")

    theta_42 = math.radians(42.0)
    print(f"\nCon θ = 42° impuesto: equilibrio UFM {'OK' if ufm.equilibrium_check(P_BRACE_KN, theta_42) else 'NO se cumple'} "
          f"(residuo α − β·tanθ − (e_c·tanθ − e_b) = {GEOM.constraint_residual(theta_42):.1f} mm)")
    f42 = ufm.interface_forces(P_BRACE_KN, theta_42)
    print(f"  Las componentes no cambian (dependen solo de la geometría): H_b = {f42.H_b:.1f} kN, "
          f"V_c = {f42.V_c:.1f} kN, pero ΣH = {f42.H_b + f42.H_c:.1f} ≠ P·cos 42° = {P_BRACE_KN*math.cos(theta_42):.1f} kN")

    f_comp = ufm.interface_forces(-P_BRACE_KN)
    print(f"\nDiagonal a compresión (P = −900 kN): H_b = {f_comp.H_b:.1f} kN, V_c = {f_comp.V_c:.1f} kN (signos invertidos)")


if __name__ == "__main__":
    main()
