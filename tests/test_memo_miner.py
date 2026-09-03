"""Tests para memoria handcalcs Miner."""
import pytest

from fatiguejm.exceptions import DetailCategoryError
from fatiguejm.memos import MinerMemoInput, render_miner_memo


def test_memo_pass():
    inp = MinerMemoInput(
        detail_category=90, gamma_mf=1.35,
        spectrum=[
            {"label": "alta", "stress_range_MPa": 80, "cycles": 1e4},
            {"label": "media", "stress_range_MPa": 50, "cycles": 5e5},
        ],
    )
    r = render_miner_memo(inp)
    assert r.pass_check
    assert r.total_damage < 1.0
    assert "PASS" in r.markdown


def test_memo_fail():
    inp = MinerMemoInput(
        detail_category=71, gamma_mf=1.35,
        spectrum=[
            {"label": "severo", "stress_range_MPa": 200, "cycles": 1e6},
        ],
    )
    r = render_miner_memo(inp)
    assert not r.pass_check
    assert r.total_damage > 1.0


def test_memo_breakdown_consistente():
    inp = MinerMemoInput(
        detail_category=90,
        spectrum=[
            {"label": "B1", "stress_range_MPa": 60, "cycles": 1e5},
            {"label": "B2", "stress_range_MPa": 80, "cycles": 5e4},
        ],
    )
    r = render_miner_memo(inp)
    assert len(r.blocks) == 2
    assert r.total_damage == pytest.approx(sum(b.damage for b in r.blocks))


def test_latex_y_markdown_no_vacios():
    r = render_miner_memo(MinerMemoInput(
        detail_category=80,
        spectrum=[{"label": "x", "stress_range_MPa": 50, "cycles": 1e3}],
    ))
    assert "frac" in r.latex
    assert "##" in r.markdown


# --------------------------------------------------------------------------- #
# Regresion: la memoria NO puede imprimir "PASS" a partir de un dato ausente.
# Con detail_category <= 0 la resistencia de diseno es nula, _n_endurance
# devolvia N = 0 y el guardia `d = n/N if N > 0 else 0.0` convertia esa
# capacidad NULA en dano CERO -> D = 0 -> "PASS" en una memoria firmada.
# --------------------------------------------------------------------------- #
def test_categoria_detalle_nula_no_rinde_memoria_pass():
    """Delta_sigma_C = 0 es resistencia nula: no puede salir un PASS."""
    inp = MinerMemoInput(
        detail_category=0.0, gamma_mf=1.35,
        spectrum=[{"label": "severo", "stress_range_MPa": 200.0, "cycles": 1e9}],
    )
    with pytest.raises(DetailCategoryError):
        render_miner_memo(inp)


def test_categoria_detalle_negativa_rechazada():
    with pytest.raises(DetailCategoryError):
        render_miner_memo(MinerMemoInput(
            detail_category=-90.0,
            spectrum=[{"label": "x", "stress_range_MPa": 50.0, "cycles": 1e3}],
        ))


def test_gamma_mf_no_positivo_rechazado():
    with pytest.raises(DetailCategoryError):
        render_miner_memo(MinerMemoInput(
            detail_category=90.0, gamma_mf=0.0,
            spectrum=[{"label": "x", "stress_range_MPa": 50.0, "cycles": 1e3}],
        ))


def test_bloque_sin_cycles_rechazado():
    """Un bloque sin ciclos no es un bloque de 0 ciclos: es un dato ausente."""
    with pytest.raises(KeyError):
        render_miner_memo(MinerMemoInput(
            detail_category=90.0,
            spectrum=[{"label": "x", "stress_range_MPa": 50.0}],
        ))
