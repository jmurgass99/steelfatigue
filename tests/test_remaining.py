"""Tests SWT + corrosion."""
import pytest

from fatiguejm.multiaxial import SWTInput, cycles_to_failure_swt
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


class TestCorrosion:
    def test_seawater_50pct(self):
        assert adjusted_FAT(90, "seawater") == 45.0

    def test_rural_sin_reduccion(self):
        assert adjusted_FAT(90, "rural") == 90.0

    def test_invalido(self):
        with pytest.raises(ValueError):
            adjusted_FAT(90, "xx")
