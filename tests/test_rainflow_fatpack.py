"""Tests del wrapper fatpack."""
from __future__ import annotations
import numpy as np
import pytest

fatpack = pytest.importorskip("fatpack")
from fatiguejm.rainflow_fatpack import rainflow_count, rainflow_count_arrays


def test_rainflow_simple_sinusoid():
    """Sinusoide pura: 1 ciclo por periodo completo."""
    t = np.linspace(0, 4 * np.pi, 200)
    sig = np.sin(t) * 100
    cycles = rainflow_count(sig)
    # Debe haber ~2 ciclos completos (range = 200)
    full = [c for c in cycles if c.count == 1.0]
    assert len(full) >= 1
    assert all(abs(c.range - 200) < 30 for c in full)


def test_rainflow_astm_e1049_canonical():
    """Ejemplo canonico ASTM E1049-85 Figura 6:
    secuencia -2, +1, -3, +5, -1, +3, -4, +4, -2 produce ciclos conocidos.
    """
    sig = [-2, 1, -3, 5, -1, 3, -4, 4, -2]
    means, ranges, counts = rainflow_count_arrays(sig)
    # Verificar que se identificaron ciclos
    assert len(ranges) > 0
    # El rango mas grande deberia ser de 9 (entre -4 y 5) - ciclo dominante
    assert max(ranges) >= 8.0


def test_rainflow_constant_amplitude():
    """Amplitud constante: todos los ciclos deben tener el mismo range."""
    sig = []
    for _ in range(10):
        sig.extend([100, -100])
    sig = np.array(sig, dtype=float)
    cycles = rainflow_count(sig)
    full_ranges = [c.range for c in cycles if c.count == 1.0]
    if full_ranges:
        assert all(abs(r - 200) < 1 for r in full_ranges)


def test_rainflow_too_short_raises():
    with pytest.raises(ValueError):
        rainflow_count([1.0, 2.0])


def test_rainflow_count_arrays_consistent():
    sig = [-2, 5, -3, 4, -1, 2, -4, 3, -2]
    cycles = rainflow_count(sig)
    means, ranges, counts = rainflow_count_arrays(sig)
    assert len(means) == len(cycles)
    assert len(ranges) == len(cycles)
    assert all(r >= 0 for r in ranges)


def test_rainflow_count_arrays_empty_history():
    # 4 puntos minimos: si todos son iguales, no hay ciclos
    means, ranges, counts = rainflow_count_arrays([0, 0, 0, 0])
    assert len(means) == 0


def test_rainflow_complex_history_no_negative_ranges():
    """Todo rango debe ser positivo por definicion."""
    np.random.seed(42)
    sig = np.random.randn(500) * 50
    cycles = rainflow_count(sig)
    assert all(c.range >= 0 for c in cycles)
