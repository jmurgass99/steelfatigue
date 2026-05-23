"""Tests para fatiguejm.lowcycle (UFM gusset + Coffin-Manson RBS)."""
import numpy as np
import pytest

from fatiguejm.exceptions import ValidationError
from fatiguejm.lowcycle import (
    CoffinMansonParams,
    CoffinMansonRBS,
    UFMGeometry,
    UFMGussetForces,
)
from fatiguejm.services import (
    LowCycleInput,
    UFMInput,
    evaluate_lowcycle,
    evaluate_ufm,
)


# ---------------------------------------------------------------------
# UFM
# ---------------------------------------------------------------------

class TestUFMGusset:
    def test_equilibrio_con_theta_implicito(self):
        geom = UFMGeometry(alpha=380, beta=305, ec=152, eb=178)
        ufm = UFMGussetForces(geom)
        P = 900_000
        theta = geom.implied_theta()
        forces = ufm.interface_forces(P)  # usa θ implícito
        # ΣH = P cosθ, ΣV = P sinθ (equilibrio del nodo)
        assert forces.H_b + forces.H_c == pytest.approx(P * np.cos(theta), rel=1e-9)
        assert forces.V_b + forces.V_c == pytest.approx(P * np.sin(theta), rel=1e-9)

    def test_equilibrium_check_geometria_consistente(self):
        geom = UFMGeometry(alpha=300, beta=200, ec=100, eb=120)
        ufm = UFMGussetForces(geom)
        # θ que satisface la restricción UFM
        theta_ok = geom.implied_theta()
        assert ufm.equilibrium_check(500_000, theta_ok)

    def test_equilibrium_check_geometria_inconsistente(self):
        geom = UFMGeometry(alpha=300, beta=200, ec=100, eb=120)
        ufm = UFMGussetForces(geom)
        # θ deliberadamente lejos del implícito
        assert not ufm.equilibrium_check(500_000, np.radians(70))

    def test_geometria_invalida_levanta(self):
        with pytest.raises(ValidationError):
            UFMGeometry(alpha=-1, beta=1, ec=0, eb=0).validate()

    def test_compresion_invierte_signos(self):
        geom = UFMGeometry(alpha=300, beta=200, ec=100, eb=120)
        ufm = UFMGussetForces(geom)
        f_t = ufm.interface_forces(+1000)
        f_c = ufm.interface_forces(-1000)
        assert f_t.H_b == pytest.approx(-f_c.H_b)


class TestUFMService:
    def test_service_devuelve_equilibrio_ok(self):
        # θ explícito alineado con la geometría
        geom = UFMGeometry(alpha=380, beta=305, ec=152, eb=178)
        result = evaluate_ufm(UFMInput(
            alpha=380, beta=305, ec=152, eb=178,
            P_brace=900_000, theta_rad=geom.implied_theta(),
        ))
        assert result.equilibrium_ok
        d = result.to_dict()
        assert set(d) == {"H_b", "V_b", "H_c", "V_c", "equilibrium_ok"}


# ---------------------------------------------------------------------
# Coffin-Manson RBS
# ---------------------------------------------------------------------

class TestCoffinMansonRBS:
    def test_cycles_to_failure_monotono(self):
        rbs = CoffinMansonRBS()
        assert rbs.cycles_to_failure(0.001) > rbs.cycles_to_failure(0.01)

    def test_strain_cero_da_inf(self):
        assert CoffinMansonRBS().cycles_to_failure(0) == float("inf")

    def test_historia_pequena_ok(self):
        rbs = CoffinMansonRBS()
        rot = np.array([0.005, 0.005, 0.005])
        r = rbs.evaluate(rot)
        assert r.status == "OK"
        assert r.total_damage < 0.5
        assert r.n_cycles == 3

    def test_historia_severa_falla(self):
        rbs = CoffinMansonRBS()
        # Rotaciones plásticas grandes y muchas → debe sumar daño ≥ 1
        rot = np.full(60, 0.05)
        r = rbs.evaluate(rot)
        assert r.status == "FAILED"
        assert r.total_damage >= 1.0

    def test_rotaciones_negativas_levanta(self):
        with pytest.raises(ValidationError):
            CoffinMansonRBS().evaluate(np.array([0.01, -0.01]))

    def test_historia_vacia_levanta(self):
        with pytest.raises(ValidationError):
            CoffinMansonRBS().evaluate(np.array([]))

    def test_parametros_invalidos(self):
        with pytest.raises(ValidationError):
            CoffinMansonParams(eps_f=-0.1).validate()
        with pytest.raises(ValidationError):
            CoffinMansonParams(c=0.5).validate()


class TestLowCycleService:
    def test_service_status_ok(self):
        r = evaluate_lowcycle(LowCycleInput(
            plastic_rotation_history=[0.005, 0.005, 0.005],
        ))
        assert r.status == "OK"
        assert r.n_cycles == 3

    def test_service_status_failed(self):
        r = evaluate_lowcycle(LowCycleInput(
            plastic_rotation_history=[0.05] * 60,
        ))
        assert r.status == "FAILED"

    def test_historia_vacia_levanta(self):
        with pytest.raises(ValidationError):
            evaluate_lowcycle(LowCycleInput(plastic_rotation_history=[]))
