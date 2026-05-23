"""Tests para memoria handcalcs Miner."""
import pytest

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
