"""Corrección por tensión media — validado contra valores publicados (Shigley)."""
import math

import pytest

from fatiguejm.mean_stress import (
    MeanStressInput,
    equivalent_reversed_stress,
    safety_factors,
)


class TestEquivalentReversed:
    def test_goodman(self):
        # sigma_ar = sigma_a / (1 - sigma_m/Su)
        sar = equivalent_reversed_stress(70.0, 100.0, 690.0, "goodman")
        assert sar == pytest.approx(70.0 / (1 - 100.0 / 690.0), rel=1e-9)

    def test_compresion_no_penaliza(self):
        assert equivalent_reversed_stress(70.0, -50.0, 690.0, "goodman") == 70.0

    def test_gerber_menos_conservador_que_goodman(self):
        g = equivalent_reversed_stress(70.0, 100.0, 690.0, "goodman")
        ge = equivalent_reversed_stress(70.0, 100.0, 690.0, "gerber")
        assert ge < g  # Gerber (parabólico) penaliza menos


class TestSafetyFactors:
    def test_goodman_n(self):
        # n = 1/(sa/Se + sm/Su)
        r = safety_factors(MeanStressInput(70.0, 100.0, 250.0, 690.0, Sy_MPa=400.0))
        esperado = 1.0 / (70.0 / 250.0 + 100.0 / 690.0)
        assert r["goodman"] == pytest.approx(esperado, rel=1e-9)

    def test_orden_conservadurismo(self):
        # Soderberg <= Goodman <= Gerber (Soderberg el más conservador).
        r = safety_factors(MeanStressInput(70.0, 100.0, 250.0, 690.0, Sy_MPa=400.0))
        assert r["soderberg"] <= r["goodman"] <= r["gerber"]

    def test_gerber_valor(self):
        # Verificación numérica del cierre de la cuadrática de Gerber.
        sa, sm, Se, Su = 70.0, 100.0, 250.0, 690.0
        r = safety_factors(MeanStressInput(sa, sm, Se, Su))
        rr = (Su / sm) ** 2
        esperado = 0.5 * rr * (sa / Se) * (-1 + math.sqrt(1 + (2 * sm * Se / (Su * sa)) ** 2))
        assert r["gerber"] == pytest.approx(esperado, rel=1e-9)
        # Y el punto (n·sa, n·sm) cae sobre la parábola de Gerber.
        n = r["gerber"]
        assert (n * sa / Se) + (n * sm / Su) ** 2 == pytest.approx(1.0, rel=1e-6)

    def test_langer_primer_ciclo(self):
        r = safety_factors(MeanStressInput(70.0, 100.0, 250.0, 690.0, Sy_MPa=400.0))
        assert r["langer"] == pytest.approx(400.0 / 170.0, rel=1e-9)

    def test_falla_predicha_n_menor_1(self):
        r = safety_factors(MeanStressInput(300.0, 400.0, 250.0, 690.0))
        assert r["goodman"] < 1.0
