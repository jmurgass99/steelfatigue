"""Golden — residuo del rainflow contado como semiciclos consecutivos (ASTM E1049-85 §5.4.4).

Señal del ejemplo del estándar: −2, 1, −3, 5, −1, 3, −4, 4, −2. La tabla del método
rainflow de ASTM E1049 da, por rango: 3 → 0,5; 4 → 1,5; 6 → 0,5; 8 → 1,0; 9 → 0,5
(4,0 ciclos en total). El único ciclo cerrado es el par (−1, 3) de rango 4; el resto
es el residuo −2, 1, −3, 5, −4, 4, −2 (7 puntos → 6 semiciclos).

Hasta 2026-10-31 el residuo se recorría de dos en dos y se perdían tres de los seis
semiciclos (los de rango 4, 9 y 6), con lo que el recuento total era 2,5 y el ciclo
de mayor rango de toda la señal desaparecía del espectro. Este test fija la tabla
del estándar. fatpack cuantiza las inversiones en 64 niveles, por eso los rangos se
redondean al entero antes de agrupar.
"""
from __future__ import annotations

from collections import Counter

import pytest

fatpack = pytest.importorskip("fatpack")
from steelfatigue.rainflow_fatpack import rainflow_count  # noqa: E402

ASTM_SIGNAL = [-2, 1, -3, 5, -1, 3, -4, 4, -2]
ASTM_TABLE = {3: 0.5, 4: 1.5, 6: 0.5, 8: 1.0, 9: 0.5}


def _counts_by_rounded_range(signal):
    out = Counter()
    for c in rainflow_count(signal):
        out[round(c.range)] += c.count
    return dict(out)


def test_astm_e1049_rainflow_table_is_reproduced():
    assert _counts_by_rounded_range(ASTM_SIGNAL) == ASTM_TABLE


def test_total_count_is_four_cycles():
    assert sum(c.count for c in rainflow_count(ASTM_SIGNAL)) == pytest.approx(4.0)


def test_largest_range_of_the_signal_is_counted():
    """El tramo 5 → −4 (rango 9) es el más dañino y antes se perdía."""
    assert max(round(c.range) for c in rainflow_count(ASTM_SIGNAL)) == 9
