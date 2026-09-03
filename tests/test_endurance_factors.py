"""Factores de Marin + efecto espesor — validado contra Shigley / EN 1993-1-9."""
import pytest

from fatiguejm.exceptions import ValidationError
from fatiguejm.endurance_factors import (
    EnduranceInput,
    Se_prime,
    endurance_limit,
    ka_surface,
    kb_size,
    kc_load,
    kd_temperature,
    ke_reliability,
)
from fatiguejm.sn_curves_multi import SNCurve, size_effect_ks, with_size_effect


class TestSePrime:
    def test_regla_mitad(self):
        assert Se_prime(690.0) == pytest.approx(345.0)

    def test_tope_700(self):
        assert Se_prime(2000.0) == 700.0


class TestKa:
    def test_machined_su690(self):
        # Shigley Ej 6-9: Su=690 MPa, mecanizado -> ka ~ 0.798
        assert ka_surface(690.0, "machined") == pytest.approx(0.798, abs=0.005)

    def test_ground_mejor_que_forjado(self):
        assert ka_surface(800.0, "ground") > ka_surface(800.0, "as-forged")


class TestKb:
    def test_axial_es_1(self):
        assert kb_size(50.0, "axial") == 1.0

    def test_flexion_d10(self):
        assert kb_size(10.0, "bending") == pytest.approx(1.24 * 10.0 ** -0.107, rel=1e-9)

    def test_decrece_con_tamano(self):
        assert kb_size(100.0, "bending") < kb_size(10.0, "bending")


class TestKcKdKe:
    def test_kc(self):
        assert kc_load("bending") == 1.0
        assert kc_load("axial") == 0.85
        assert kc_load("torsion") == 0.59

    def test_kc_load_desconocido_rechazado(self):
        """Una carga desconocida NO puede degradar al factor mas favorable.

        kc_load devolvia 1.0 (sin reduccion) ante cualquier cadena no tabulada,
        mientras ka_surface —su hermana en el mismo modulo— si lanza. Un typo
        como 'axail' pasaba de kc=0.85 a kc=1.0 y sobreestimaba Se un 18%.
        """
        with pytest.raises(ValidationError):
            kc_load("axail")
        with pytest.raises(ValidationError):
            kc_load("tension")

    def test_kd_ambiente(self):
        assert kd_temperature(20.0) == pytest.approx(1.0, abs=0.01)

    def test_kd_decrece_con_temperatura(self):
        assert kd_temperature(400.0) < kd_temperature(20.0)

    def test_ke_tabla(self):
        assert ke_reliability(0.50) == 1.0
        assert ke_reliability(0.99) == pytest.approx(0.814)
        assert ke_reliability(0.999) == pytest.approx(0.753)


class TestEnduranceLimit:
    def test_producto_marin(self):
        r = endurance_limit(EnduranceInput(Su_MPa=690.0, finish="machined",
                                           d_mm=10.0, loading="bending",
                                           T_C=20.0, reliability=0.99))
        prod = r["ka"] * r["kb"] * r["kc"] * r["kd"] * r["ke"] * r["Se_prime_MPa"]
        assert r["Se_MPa"] == pytest.approx(prod, rel=1e-12)
        # Se corregido siempre menor que Se' (factores <= 1 en este caso).
        assert r["Se_MPa"] < r["Se_prime_MPa"]


class TestSizeEffectEN:
    def test_sin_reduccion_bajo_25mm(self):
        assert size_effect_ks(20.0) == 1.0

    def test_reduccion_espesor(self):
        # EN 1993-1-9 §7.2.1: k_s = (25/t)^0.2
        assert size_effect_ks(50.0) == pytest.approx((25.0 / 50.0) ** 0.2, rel=1e-9)

    def test_with_size_effect_reduce_categoria(self):
        c = SNCurve("US", "C", 69.0)
        cr = with_size_effect(c, 50.0)
        assert cr.delta_sigma_C_MPa < c.delta_sigma_C_MPa
        assert cr.delta_sigma_C_MPa == pytest.approx(69.0 * (25.0 / 50.0) ** 0.2, rel=1e-9)
