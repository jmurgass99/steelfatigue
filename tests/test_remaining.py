"""Tests SWT + corrosion."""
import pytest

from fatiguejm.multiaxial import (
    SWTInput,
    critical_plane_search,
    cycles_to_failure_swt,
)
from fatiguejm.corrosion import CORROSION_FACTORS, adjusted_FAT


class TestSWT:
    def test_decreciente_con_strain(self):
        N_low = cycles_to_failure_swt(SWTInput(
            sigma_max_MPa=200, eps_amplitude=0.001,
        ))
        N_high = cycles_to_failure_swt(SWTInput(
            sigma_max_MPa=200, eps_amplitude=0.01,
        ))
        assert N_low > N_high

    def test_runout_devuelve_infinito_no_cero(self):
        """Vida infinita (la curva no corta la demanda) NO es N_f = 0.

        Cuando f(lo) y f(hi) tienen el mismo signo positivo, la capacidad supera
        la demanda incluso en N_max: es run-out. El test de bracket comparaba
        `P_target < f_hi` (magnitudes distintas) en vez del signo de f_hi, y
        devolvia el literal 0.0 —vida nula— para un caso de vida infinita.
        """
        N = cycles_to_failure_swt(SWTInput(
            sigma_max_MPa=100.0, eps_amplitude=0.0003,
        ))
        assert N == float("inf")

    def test_demanda_por_encima_de_la_curva_sigue_dando_vida_nula(self):
        """El otro lado del bracket no se toca: demanda brutal -> N_f = 0."""
        N = cycles_to_failure_swt(SWTInput(
            sigma_max_MPa=1000.0, eps_amplitude=1.0,
        ))
        assert N == 0.0


class TestCriticalPlaneSearch:
    def test_historia_vacia_rechazada(self):
        """Sin historia de tensiones no hay plano critico: no vale devolver 0.0.

        Devolvia sigma_max = 0.0 y eps_a = 0.0, es decir P_SWT = 0 -> vida
        infinita: una ausencia de datos leida como 'no hay demanda de fatiga'.
        """
        with pytest.raises(ValueError):
            critical_plane_search({})

    def test_historia_presente_devuelve_P_SWT(self):
        """El camino valido conserva la clave P_SWT (forma consistente)."""
        out = critical_plane_search({
            "sxx": [0.0, 200.0, 0.0, 200.0],
            "syy": [0.0, 50.0, 0.0, 50.0],
            "sxy": [0.0, 20.0, 0.0, 20.0],
        })
        assert "P_SWT" in out
        assert out["sigma_max"] > 0.0


class TestCorrosion:
    def test_seawater_50pct(self):
        assert adjusted_FAT(90, "seawater") == 45.0

    def test_rural_sin_reduccion(self):
        assert adjusted_FAT(90, "rural") == 90.0

    def test_invalido(self):
        with pytest.raises(ValueError):
            adjusted_FAT(90, "xx")
