"""Fatiga de amplitud variable — Rainflow + tensión media + Miner."""
import pytest

from steelfatigue.rainflow_fatpack import RainflowCycle
from steelfatigue.sn_curves_multi import SNCurve, cycles_to_failure
from steelfatigue.variable_amplitude import damage_from_cycles, damage_from_history

CURVE = SNCurve("US", "C", 69.0)   # AISC categoría C, m=3, Nc=2e6


class TestDamageFromCycles:
    def test_un_ciclo_media_cero(self):
        # range=100, mean=0 -> Δσ_eq=100 ; N = 2e6·(69/100)^3 ; D = 1/N
        cyc = [RainflowCycle(mean=0.0, range=100.0, count=1.0)]
        r = damage_from_cycles(cyc, CURVE, Su_MPa=500.0)
        N = cycles_to_failure(CURVE, 100.0)
        assert r.total_damage == pytest.approx(1.0 / N, rel=1e-6)
        assert r.n_cycles == 1 and r.ok

    def test_tension_media_aumenta_dano(self):
        # Misma amplitud, media de tracción -> rango equivalente mayor -> más daño.
        sin_media = damage_from_cycles([RainflowCycle(0.0, 100.0, 1.0)], CURVE, 500.0).total_damage
        con_media = damage_from_cycles([RainflowCycle(100.0, 100.0, 1.0)], CURVE, 500.0).total_damage
        assert con_media > sin_media

    def test_acumulacion_lineal(self):
        uno = damage_from_cycles([RainflowCycle(0.0, 120.0, 1.0)], CURVE, 500.0).total_damage
        diez = damage_from_cycles([RainflowCycle(0.0, 120.0, 10.0)], CURVE, 500.0).total_damage
        assert diez == pytest.approx(10.0 * uno, rel=1e-9)

    def test_falla_con_muchos_ciclos(self):
        # Rango grande + muchos ciclos -> D > 1.
        cyc = [RainflowCycle(0.0, 250.0, 5_000_000.0)]
        r = damage_from_cycles(cyc, CURVE, 500.0)
        assert r.total_damage > 1.0 and not r.ok


class TestDamageFromHistory:
    def test_historia_rainflow(self):
        # Historia oscilante -> rainflow -> daño > 0.
        hist = [0, 120, -40, 100, -60, 130, 0, 110, -30, 90]
        try:
            r = damage_from_history(hist, CURVE, Su_MPa=500.0)
        except ImportError:
            pytest.skip("fatpack no disponible")
        assert r.total_damage > 0 and r.n_cycles >= 1
